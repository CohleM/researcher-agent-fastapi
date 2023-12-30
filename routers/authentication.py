from fastapi import APIRouter, HTTPException
from jose import JWTError, jwt
import json
import requests
from .. import schemas


router = APIRouter()


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


def create_magic_link_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


@router.get("/token/{token}")
def verify_magic_link_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        # Perform additional user verification or authentication here
        # Example: authenticate_user(email)
        return {"isValid": "true", "message": "Magic link verified successfully"}
    except JWTError:
        return {"isValid": "false", "message": "Invalid token"}
        # raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/magic-link")
def send_magic_link(user: schemas.UserBase):
    # Generate a unique token
    token = create_magic_link_token({"sub": user.email})

    # Send the token via email (replace with your email sending logic)
    send_email(
        user.email,
        "Log into OkProfessor",
        f"Click on this link to authenticate: http://localhost:3000/authentication?token={token}",
    )
    return {"message": f"Magic link sent to your {user.email}"}


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
