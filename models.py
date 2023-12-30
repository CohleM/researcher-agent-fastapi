from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    # hashed_password = Column(String)
    # is_active = Column(Boolean, default=True)

    drafts = relationship("Draft", back_populates="owner")


class Draft(Base):
    __tablename__ = "drafts"
    id = Column(Integer, primary_key=True, index=True)
    # change the string to text or something later
    text = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="drafts")

    files = relationship("File", back_populates="corresponding_draft")
    # add another relationship


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text)

    draft_id = Column(Integer, ForeignKey("drafts.id"))

    corresponding_draft = relationship("Draft", back_populates="files")
