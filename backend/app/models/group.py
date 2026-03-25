from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    multiplier = Column(Float, default=1)
    description = Column(String)

    accounts = relationship("GroupAccount", back_populates="group", cascade="all, delete")


class GroupAccount(Base):
    __tablename__ = "group_accounts"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    account_id = Column(Integer)

    group = relationship("Group", back_populates="accounts")