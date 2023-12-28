from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from websocket_manager import WebSocketManager
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
import time
from typing import AsyncGenerator, NoReturn
from websocket_manager import WebSocketManager
from datetime import datetime, timedelta

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import requests
import json

# Initials
manager = WebSocketManager()
app = FastAPI()
client = AsyncOpenAI()

# with open("index.html") as f:
#     html = f.read()


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "your-secret-key"  # Change this to a secure random key
ALGORITHM = "HS256"


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "iamafanaticus@gmail.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


class User(BaseModel):
    email: str


def create_magic_link_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def verify_magic_link_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


@app.post("/magic-link/")
def send_magic_link(user: User):
    # Generate a unique token
    token = create_magic_link_token({"sub": user.email})

    # Send the token via email (replace with your email sending logic)
    send_email(
        user.email,
        "Log into OkProfessor",
        f"Click on this link to authenticate: {token}",
    )

    return {"message": "Magic link sent"}


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
        "api-key": "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",
        "content-type": "application/json",
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


send_email(
    to_email="manish981194@gmail.com",
    subject="Is Python SDK work done?",
    text_content="Hi Sourabh,\nIs Python SDK work complete or not?",
)


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# app = FastAPI()


# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)


# def get_password_hash(password):
#     return pwd_context.hash(password)


# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)


# def authenticate_user(fake_db, username: str, password: str):
#     user = get_user(fake_db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user


# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     user = get_user(fake_users_db, username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user


# async def get_current_active_user(
#     current_user: Annotated[User, Depends(get_current_user)]
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


# @app.post("/token", response_model=Token)
# async def login_for_access_token(
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
# ):
#     user = authenticate_user(fake_users_db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}


# @app.get("/users/me/", response_model=User)
# async def read_users_me(
#     current_user: Annotated[User, Depends(get_current_active_user)]
# ):
#     return current_user


# @app.get("/users/me/items/")
# async def read_own_items(
#     current_user: Annotated[User, Depends(get_current_active_user)]
# ):
#     return [{"item_id": "Foo", "owner": current_user.username}]


# @app.get("/users/me")
# async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
#     return current_user


## Websocket connection and streaming openai response
async def get_ai_response(message: str) -> AsyncGenerator[str, None]:
    """
    OpenAI Response
    """
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant, skilled in explaining "
                    "complex concepts in simple terms."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        stream=True,
    )

    all_content = ""
    async for chunk in response:
        content = chunk.choices[0].delta.content
        finish_reason = chunk.choices[0].finish_reason
        # print("haha", content)
        print(content)
        # if content:
        # all_content += content
        if content:
            all_content += content
        yield all_content, finish_reason


# @app.get("/")
# async def web_app() -> HTMLResponse:
#     """
#     Web App
#     """
#     return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> NoReturn:
    """
    Websocket for AI responses
    """

    await manager.connect(websocket)

    while True:
        message = await websocket.receive_text()
        print("message printing from backend", message)
        async for text, finish_reason in get_ai_response(message):
            # print(text, finish_reason)
            await websocket.send_json({"content": text, "finish_reason": finish_reason})
