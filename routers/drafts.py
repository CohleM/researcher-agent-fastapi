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
    print("create-new-draft", current_user)
    draft = crud.create_draft(db, current_user)
    return draft


@router.get("/draft", response_model=schemas.Draft)
def get_draft(
    id: int,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    print("yas", current_user)
    draft = crud.get_draft_by_id(db, id)

    return draft


@router.post("/edit-draft/{draft_id}", response_model=schemas.Draft)
def edit_draft(
    draft_id: int,
    draft_update: schemas.DraftBase,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    draft = crud.get_draft_by_id(db, draft_id)

    if draft:
        draft.text = draft_update.text
        draft.name = draft_update.name
        db.commit()
        db.refresh(draft)
        return draft

    raise HTTPException(status_code=404, detail="could not find the draft with that id")


@router.get("/get-drafts", response_model=schemas.AllDrafts)
def get_drafts(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    print(current_user.drafts)
    return current_user.drafts
