from fastapi import APIRouter, HTTPException, status, Depends
from jose import JWTError, jwt, ExpiredSignatureError
import json
import requests as magic_link_request
from .. import schemas, crud
from datetime import datetime, timedelta
from typing import Optional, Annotated
from ..database import SessionLocal, engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2AuthorizationCodeBearer

from starlette.requests import Request
from google.oauth2 import id_token 
from google.auth.transport import requests 

router = APIRouter(tags=["auth"])

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
        detail="expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        print("trying this ")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("also trying this")
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        user = create_user(schemas.UserBase(email=email), db)
        # return {"isValid": "true", "message": "Magic link verified successfully"}
        access_token = create_token(
            {"sub": user.email}, expires_delta=timedelta(minutes=120)
        )
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        print("causethis exception")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/magic-link")
def send_magic_link(user: schemas.UserBase):
    # Generate a unique token
    token = create_token({"sub": user.email}, expires_delta=timedelta(minutes=30))

    # Send the token via email (replace with your email sending logic)
    ## http://localhost:3000/authentication?token={token}
    response = send_email(
        user.email,
        "Sign in to Okprofessor",
        f"""
        Hello <br><br>We received a request to sign in to Okprofessor using this email address.<br>

        If you want to sign in, click the below link: <br><br>

        <a href='{os.getenv('FRONTEND_URL')}/authentication?token={token}'>Log in to Okprofessor</a><br><br>

        The link will expire in 30 minutes. If it expires, you can request a new link again.<br><br>

        If you did not request this link, you can safely ignore this email.<br><br><br>

        Thanks,<br><br>

        Team Okprofessor

        """,
    )

    print('RESPONSE of sending email', response)
    print('RESPONSE of sending email', response.content)
    print('RESPONSE of sending email', response.status_code)

    if response.status_code >= 400 and response.status_code < 500:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldnt send requests")

    return {"message": f"Verification email sent to {user.email}. If you can't find the mail in your inbox, please check your spam section."}


def send_email(to_email: str, subject: str, text_content: str):
    url = "https://api.brevo.com/v3/smtp/email"
    payload = json.dumps(
        {
            "sender": {"name": "login@okprofessor.com", "email": "no-reply@okprofessor.com"},
            "to": [{"email": f"{to_email}"}],
            "subject": subject,
            "htmlContent": text_content,
        }
    )
    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_TOKEN"),
        "content-type": "application/json",
    }
    response = magic_link_request.request("POST", url, headers=headers, data=payload)
    print(response.text)

    return response


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    print("get_current_user executed")
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

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except JWTError:
        raise credentials_exception

    # user = get_user(fake_users_db, username=token_data.username)
    user = crud.get_user_by_email(db=db, email=email)
    if user is None:
        print("this time its me")
        raise credentials_exception
    return user


async def get_current_user_websocket(
    token, db
):
    print("get_current_user executed")
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

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except JWTError:
        raise credentials_exception

    # user = get_user(fake_users_db, username=token_data.username)
    user = crud.get_user_by_email(db=db, email=email)
    if user is None:
        print("this time its me")
        raise credentials_exception
    return user






@router.get("/userinfo", response_model=schemas.User)
async def get_user_info(
    current_user: Annotated[schemas.UserResponse, Depends(get_current_user)]
):
    print("yooo")
    if current_user:
        print(current_user)
        return current_user

    else:
        print("heheh")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


## Login with google 
  
@router.get("/google-auth") 
def authentication(request: Request,token:str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="NOT Authorized by Google",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try: 
        # Specify the CLIENT_ID of the app that accesses the backend: 
        user =id_token.verify_oauth2_token(token, requests.Request(), os.getenv('GOOGLE_CLIENT_ID')) 
        print('USER', user)
        # request.session['user'] = dict({ 
        #     "email" : user["email"]  
        # }) 
        # return user['name'] + ' Logged In successfully'
    except Exception as e:
        print('ERROR', e)
        raise credentials_exception

    try:
        email: str = user['email'] 
        if email is None:
            raise credentials_exception

        user = create_user(schemas.UserBase(email=email), db)
        # return {"isValid": "true", "message": "Magic link verified successfully"}
        access_token = create_token(
            {"sub": user.email}, expires_delta=timedelta(minutes=120)
        )
        print(' Google login this is executed')
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
 