from pydantic import BaseModel, Field
from typing import Optional


class FileBase(BaseModel):
    name: str = Field(..., max_length=255)
    path: str = Field(..., max_length=500)


class FileCreate(FileBase):
    pass


class File(FileBase):
    id: int

    class Config:
        from_attributes = True