from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class GoalBase(BaseModel):
    title: str
    target: str
    type: str
    deadline: Optional[datetime] = None

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    target: Optional[str] = None
    type: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None
    progress: Optional[float] = None

class GoalResponse(GoalBase):
    id: int
    user_id: int
    status: str
    progress: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
