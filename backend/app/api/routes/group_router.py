from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.group import GroupCreate
from app.services.group_service import GroupService

router = APIRouter(prefix="/groups", tags=["Groups"])


# Create Group
@router.post("/")
async def create_group(
    data: GroupCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        group = await GroupService.create_group(db, data)

        return {
            "message": "Group created",
            "group_id": group.id
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get All Groups
@router.get("/")
async def get_groups(
    db: AsyncSession = Depends(get_db)
):

    groups = await GroupService.get_groups(db)

    return groups


# Get Single Group (FOR EDIT PAGE)
@router.get("/{id}")
async def get_group(
    id: int,
    db: AsyncSession = Depends(get_db)
):

    group = await GroupService.get_group_by_id(db, id)

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    return group


@router.delete("/{id}")
async def delete_group(
    id: int,
    db: AsyncSession = Depends(get_db)
):

    deleted = await GroupService.delete_group(db, id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Group not found")

    return {"message": "Group deleted successfully"}


@router.put("/{id}")
async def update_group(
    id: int,
    data: GroupCreate,
    db: AsyncSession = Depends(get_db)
):

    updated = await GroupService.update_group(db, id, data)

    if not updated:
        raise HTTPException(status_code=404, detail="Group not found")

    return {"message": "Group updated successfully"}


# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.core.database import get_db
# from app.schemas.group import GroupCreate
# from app.services.group_service import GroupService

# router = APIRouter(prefix="/groups", tags=["Groups"])


# @router.post("/")
# async def create_group(
#     data: GroupCreate,
#     db: AsyncSession = Depends(get_db)
# ):

#     group = await GroupService.create_group(db, data)

#     return {"message": "Group created", "group_id": group.id}


# @router.get("/")
# async def get_groups(
#     db: AsyncSession = Depends(get_db)
# ):

#     groups = await GroupService.get_groups(db)

#     return groups