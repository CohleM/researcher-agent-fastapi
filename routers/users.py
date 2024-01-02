from fastapi import APIRouter
from .. import schemas, crud, models

from fastapi import Depends, FastAPI, HTTPException
from typing import Annotated

from sqlalchemy.orm import Session

# from . import crud, models, schemas
from ..database import SessionLocal, engine

router = APIRouter(tags=["user"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/create-user", response_model=schemas.User, tags=["user"])
def create_user(user: schemas.UserBase, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        return db_user
    return crud.create_user(db=db, user=user)
