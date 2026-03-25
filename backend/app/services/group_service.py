from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.models.group import Group, GroupAccount
from app.schemas.group import GroupCreate


class GroupService:

    # Create Group
    @staticmethod
    async def create_group(db: AsyncSession, data: GroupCreate):

        # check duplicate group name
        result = await db.execute(
            select(Group).where(Group.name.ilike(data.name))
        )

        existing = result.scalar_one_or_none()

        if existing:
            raise Exception(f"There is already an account with similar name: {data.name}")

        group = Group(
            name=data.name,
            multiplier=data.multiplier,
            description=data.description
        )

        db.add(group)
        await db.flush()

        for acc_id in data.account_ids:
            db.add(GroupAccount(group_id=group.id, account_id=acc_id))

        await db.commit()

        return group
    
    # Get All Groups
    @staticmethod
    async def get_groups(db: AsyncSession):

        result = await db.execute(
            select(Group).options(selectinload(Group.accounts))
        )

        groups = result.scalars().all()

        response = []

        for g in groups:
            account_ids = [a.account_id for a in g.accounts]

            response.append({
                "id": g.id,
                "name": g.name,
                "multiplier": g.multiplier,
                "description": g.description,
                "account_ids": account_ids
            })

        return response


    # Get Single Group (FOR EDIT PAGE)
    @staticmethod
    async def get_group_by_id(db: AsyncSession, group_id: int):

        result = await db.execute(
            select(Group)
            .options(selectinload(Group.accounts))
            .where(Group.id == group_id)
        )

        group = result.scalar_one_or_none()

        if not group:
            return None

        account_ids = [a.account_id for a in group.accounts]

        return {
            "id": group.id,
            "name": group.name,
            "multiplier": group.multiplier,
            "description": group.description,
            "account_ids": account_ids
        }


    # Update Group
    @staticmethod
    async def update_group(db: AsyncSession, group_id: int, data: GroupCreate):

        result = await db.execute(
            select(Group).where(Group.id == group_id)
        )

        group = result.scalar_one_or_none()

        if not group:
            return None

        group.name = data.name
        group.multiplier = data.multiplier
        group.description = data.description

        # Remove old accounts
        await db.execute(
            delete(GroupAccount).where(GroupAccount.group_id == group_id)
        )

        # Add new accounts
        for acc_id in data.account_ids:
            db.add(
                GroupAccount(
                    group_id=group_id,
                    account_id=acc_id
                )
            )

        await db.commit()

        return group


    @staticmethod
    async def delete_group(db: AsyncSession, group_id: int):

        result = await db.execute(
            select(Group).where(Group.id == group_id)
        )

        group = result.scalar_one_or_none()

        if not group:
            return None

        # delete group accounts first
        await db.execute(
            delete(GroupAccount).where(GroupAccount.group_id == group_id)
        )

        # delete group
        await db.delete(group)

        await db.commit()

        return True


    @staticmethod
    async def update_group(db: AsyncSession, group_id: int, data: GroupCreate):

        group = await db.get(Group, group_id)

        if not group:
            return None

        group.name = data.name
        group.multiplier = data.multiplier
        group.description = data.description

        # delete old account mappings
        await db.execute(
            delete(GroupAccount).where(GroupAccount.group_id == group_id)
        )

        # insert new account mappings
        for acc_id in data.account_ids:
            db.add(GroupAccount(group_id=group_id, account_id=acc_id))

        await db.commit()

        return group