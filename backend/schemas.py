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
    name: str


class File(FileBase):
    id: int
    draft_id: int
    last_updated: datetime
    toggle: bool

    class Config:
        orm_mode = True


class AllFiles(BaseModel):
    files: list[File]


class DraftBase(BaseModel):
    text: str
    name: str


class DraftWithoutText(BaseModel):
    id: int
    name: str
    owner_id: int
    last_updated: datetime

    class Config:
        orm_mode = True


class AllDrafts(BaseModel):
    drafts: list[DraftWithoutText] = []


class Draft(DraftBase):
    id: int

    owner_id: int
    # files: list[File] = []
    last_updated: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True



class User(UserBase):
    id: int
    drafts: list[DraftWithoutText] = []
    credits : int
    subscription : str

    class Config:
        orm_mode = True

class Payment(BaseModel):
    success_url : str
    cancel_url : str

# class FileState(BaseModel):
#     is_active: bool

class DynamicFileStates(BaseModel):
    """Schema for dynamic file states."""
    states: dict[str, bool]

