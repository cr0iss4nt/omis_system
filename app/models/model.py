from pydantic import BaseModel, Field
from typing import Optional


class ModelBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=1000)
    model_type: str = Field(..., max_length=50)
    file_id: int


class ModelCreate(ModelBase):
    pass


class ModelUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    model_type: Optional[str] = Field(None, max_length=50)
    file_id: Optional[int] = None


class Model(ModelBase):
    id: int

    class Config:
        from_attributes = True