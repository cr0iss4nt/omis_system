from pydantic import BaseModel, Field
from typing import Optional


class ParameterBase(BaseModel):
    name: str = Field(..., max_length=100)
    value: str = Field(..., max_length=500)


class ParameterCreate(ParameterBase):
    experiment_id: int


class ParameterUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    value: Optional[str] = Field(None, max_length=500)


class Parameter(ParameterBase):
    id: int
    experiment_id: int

    class Config:
        from_attributes = True