from pydantic import BaseModel


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
    owner_id: int
    files: list[File] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class User(UserBase):
    id: int
    items: list[Draft] = []

    class Config:
        orm_mode = True
