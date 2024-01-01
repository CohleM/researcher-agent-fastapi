from fastapi import APIRouter, HTTPException, status, Depends
from jose import JWTError, jwt
import json
import requests
from .. import schemas, crud
from datetime import datetime, timedelta
from typing import Optional, Annotated
from ..database import SessionLocal, engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2AuthorizationCodeBearer


router = APIRouter()

load_dotenv()

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "your-secret-key"  # Change this to a secure random key
ALGORITHM = "HS256"


# Replace "authorization-code" and "token" with your actual endpoint URLs
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="authorization-code", tokenUrl="token"
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_user(user: schemas.UserBase, db: Session):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        return db_user
    return crud.create_user(db=db, user=user)


def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=5)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.get("/token/{token}")
def verify_magic_link_token(token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials gg",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        user = create_user(schemas.UserBase(email=email), db)
        # return {"isValid": "true", "message": "Magic link verified successfully"}
        access_token = create_token(
            {"sub": user.email}, expires_delta=timedelta(hours=4)
        )
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        print("there was some errorr ggg")
        raise credentials_exception

    # raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/magic-link")
def send_magic_link(user: schemas.UserBase):
    # Generate a unique token
    token = create_token({"sub": user.email})

    # Send the token via email (replace with your email sending logic)
    send_email(
        user.email,
        "Log into OkProfessor",
        f"Click on this link to authenticate: http://localhost:3000/authentication?token={token}",
    )
    return {"message": f"Sent the verification email to {user.email}"}


def send_email(to_email: str, subject: str, text_content: str):
    url = "https://api.brevo.com/v3/smtp/email"
    payload = json.dumps(
        {
            "sender": {"name": "Manish", "email": "manisrocker@gmail.com"},
            "to": [{"email": f"{to_email}"}],
            "subject": subject,
            "textContent": text_content,
        }
    )
    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_TOKEN"),
        "content-type": "application/json",
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # user = get_user(fake_users_db, username=token_data.username)
    user = crud.get_user_by_email(db=db, email=email)
    if user is None:
        raise credentials_exception
    return user


@router.get("/userinfo", response_model=schemas.UserResponse)
async def get_private_data(
    current_user: Annotated[schemas.UserResponse, Depends(get_current_user)]
):
    print(current_user)
    return current_user
