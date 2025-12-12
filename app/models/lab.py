from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class LabBase(BaseModel):
    name: str = Field(..., max_length=100)
    instruction: str = Field(..., max_length=5000)
    deadline: datetime
    experiment_id: int


class LabCreate(LabBase):
    pass


class LabUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    instruction: Optional[str] = Field(None, max_length=5000)
    deadline: Optional[datetime] = None
    experiment_id: Optional[int] = None


class Lab(LabBase):
    id: int

    class Config:
        from_attributes = True


class LabAssignment(BaseModel):
    student_id: int
    grade: Optional[float] = Field(None, ge=0, le=100)


class LabSubmission(BaseModel):
    value: str = Field(..., max_length=10000)