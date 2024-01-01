from fastapi import APIRouter
from .. import schemas, crud, models
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

# from . import crud, models, schemas
from ..database import SessionLocal, engine
from .authentication import get_current_user

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create a new draft for new users.
@router.get("/create-draft", response_model=schemas.Draft)
def create_new_draft(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    print("yas", current_user)
    draft = crud.create_draft(db, current_user)

    return draft
