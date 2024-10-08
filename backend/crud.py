from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import models, schemas
from fastapi import HTTPException

## Users
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


# Create a new user by email
def create_user(db: Session, user: schemas.UserBase):
    db_user = models.User(email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Create a new user by email
def update_credits( user_email, credit_usage, db: Session):
    user = db.query(models.User).filter(models.User.email == user_email).first()
    user.credits = user.credits + credit_usage
    db.commit()
    db.refresh(user)

    print('USER CREDIT', user.credits)
    return {'credit_update' : 'done'}

# Create a new user by email
def add_subscription_credits(user_email, credit_usage, db: Session):
    user = db.query(models.User).filter(models.User.email == user_email).first()
    user.credits =  credit_usage
    user.credits_expiration_date = datetime.utcnow() + timedelta(days=30)
    
    user.subscription = 'Premium'

    db.commit()
    db.refresh(user)

    print('Subscription CREDIT added', user.credits)
    return {'credit_update' : 'done'}

##Items
def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


## Drafts
def create_draft(db: Session, user: schemas.User):
    print("hehe")
    # Initially we don't have anything on the draft so text = ''
    text = ""
    db_draft = models.Draft(text=text, name="", owner_id=user.id)
    db.add(db_draft)
    db.commit()
    db.refresh(db_draft)
    return db_draft


def get_draft_by_id(db: Session, id: int):
    return db.query(models.Draft).filter(models.Draft.id == id).first()


# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item
def save_file(db: Session, name: str, url: str, user_id: int):
    file = models.File(name=name, url=url , user_id=user_id)
    db.add(file)
    db.commit()
    db.refresh(file)
    return file


def get_files_by_draft_id(db: Session, id: int):
    return db.query(models.File).filter(models.File.draft_id == id).all()


def get_file_by_id(db: Session, id: int):
    return db.query(models.File).filter(models.File.id == id).first()


def update_each_file_toggle(db:Session, id:int, value: bool):
    
    file = db.query(models.File).filter(models.File.id ==  id).first()
    file.toggle = value
    db.commit()
    db.refresh(file)

    return file

def get_filenames_from_ids(file_ids: list[int], db : Session):

    files_data = db.query(models.File).filter(models.File.id.in_(file_ids)).all()

    if not files_data:
        raise HTTPException(status_code=404, detail="Files not found")

    result = [{"name": file_data.name, "url": file_data.url} for file_data in files_data]
    return result
