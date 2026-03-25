from pydantic import BaseModel
from typing import List, Optional


class GroupCreate(BaseModel):
    name: str
    multiplier: float
    description: Optional[str] = None
    account_ids: List[int]


class GroupResponse(BaseModel):
    id: int
    name: str
    multiplier: float
    description: Optional[str]
    account_ids: List[int]
    totalAccounts: int

    class Config:
        orm_mode = True