from fastapi import APIRouter
from .. import schemas, crud, models
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

# from . import crud, models, schemas
from ..database import SessionLocal, engine
from .authentication import get_current_user
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import os
import io

load_dotenv()

router = APIRouter(tags=["draft"])
# Create an S3 client
s3 = boto3.client(
    service_name="s3",
    endpoint_url="https://a4063a28e18e10f62e59c10691947b30.r2.cloudflarestorage.com",
    aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("R2_ACCESS_KEY_SECRET"),
    region_name="auto",  # Must be one of: wnam, enam, weur, eeur, apac, auto
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def upload_to_s3(file_path, file_content):
    try:
        # Upload the file to S3
        # Upload/Update single file
        s3.upload_fileobj(io.BytesIO(file_content), "aiwriter", file_path)

        # s3.upload_file(file_content, S3_BUCKET_NAME, file_path)
        return True
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not available.")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error uploading file to S3: {str(e)}"
        )


@router.get("/upload-file")
def upload_file():  # let's take nothing from the response body for now
    print("hey")
    local_file_path = "sample.jpg"
    try:
        current_directory = os.getcwd()

        # List all files in the current directory
        files = [
            f
            for f in os.listdir(current_directory)
            if os.path.isfile(os.path.join(current_directory, f))
        ]

        print(files)
        # Read the local file content
        with open(local_file_path, "rb") as file:
            file_content = file.read()

        # Specify the S3 object key (path in the bucket)
        s3_file_path = f"uploads/{local_file_path}"

        # Upload the file to S3
        success = upload_to_s3(s3_file_path, file_content)

        if success:
            return {
                "message": "File uploaded successfully to S3",
                "s3_key": s3_file_path,
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to upload file to S3")

    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"File '{local_file_path}' not found."
        )
