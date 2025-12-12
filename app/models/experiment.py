from pydantic import BaseModel, Field
from typing import Optional, List
from .parameter import Parameter


class ExperimentBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=1000)
    model_id: int


class ExperimentCreate(ExperimentBase):
    parameters: Optional[dict] = {}


class ExperimentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    model_id: Optional[int] = None


class Experiment(ExperimentBase):
    id: int

    class Config:
        from_attributes = True