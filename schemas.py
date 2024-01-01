from pydantic import BaseModel
from datetime import datetime

# class ItemBase(BaseModel):
#     title: str
#     description: str | None = None


# class ItemCreate(ItemBase):
#     pass


# class Item(ItemBase):
#     id: int
#     owner_id: int

#     class Config:
#         orm_mode = True


class FileBase(BaseModel):
    url: str


class File(FileBase):
    id: int
    draft_id: int

    class Config:
        orm_mode = True


class DraftBase(BaseModel):
    text: str


class Draft(DraftBase):
    id: int
    name: str
    owner_id: int
    files: list[File] = []
    last_updated: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class User(UserBase):
    id: int
    drafts: list[Draft] = []

    class Config:
        orm_mode = True
