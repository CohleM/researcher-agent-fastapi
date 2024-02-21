from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import func
from .database import Base
from datetime import datetime, timedelta


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    # hashed_password = Column(String)
    # is_active = Column(Boolean, default=True)
    subscription = Column(String, default='free')  # Assuming subscription is a string type
    credits = Column(Integer, default=50)  # Assuming credits is an integer type
    credits_expiration_date = Column(DateTime, server_default=func.now() + timedelta(days=30))

    drafts = relationship("Draft", back_populates="owner")
    random = Column(String, default='gg')
    files = relationship("File", back_populates="corresponding_user")
    



class Draft(Base):
    __tablename__ = "drafts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    text = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="drafts")
    last_updated = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    # files = relationship("File", back_populates="corresponding_draft")
    # add another relationship


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, index=True)
    url = Column(Text)
    # draft_id = Column(Integer, ForeignKey("drafts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    # corresponding_draft = relationship("Draft", back_populates="files")
    corresponding_user = relationship("User", back_populates="files")
    last_updated = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    # toggle = Column(Boolean, default=False)
    
