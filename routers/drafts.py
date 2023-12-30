from fastapi import APIRouter
from .. import schemas, crud, models

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

# from . import crud, models, schemas
from ..database import SessionLocal, engine

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/create-draft")
def create_draft():
    pass
