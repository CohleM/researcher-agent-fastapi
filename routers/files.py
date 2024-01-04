from fastapi import APIRouter, File, UploadFile
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
import uuid

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
        s3.upload_fileobj(io.BytesIO(file_content), os.getenv("BUCKET_NAME"), file_path)
        return True
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not available.")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error uploading file to S3: {str(e)}"
        )


@router.post("/upload-file")
async def upload_file(
    draft_id: int,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
):  # let's take nothing from the response body for now
    print("draft id gg ", draft_id)
    user_id = current_user.id

    # modified filename
    original_filename = file.filename
    filename = f"{user_id}-{draft_id}-{uuid.uuid4()}.{file.filename.split('.')[-1]}"
    print(filename)
    # Read the files
    file = await file.read()

    try:
        # Specify the S3 object key (path in the bucket)
        s3_file_path = f"uploads/{filename}"
        # Upload the file to S3
        success = upload_to_s3(s3_file_path, file)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found.")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload file to S3")

    ## save the data to the database.
    if success:
        saved_file = crud.save_file(db, original_filename, filename, draft_id)
        return {
            "message": "File uploaded successfully to S3",
            "s3_key": s3_file_path,
            "file_info": saved_file,
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to upload file to S3")


@router.get("/get-files", response_model=schemas.AllFiles)
def get_files(
    draft_id: int,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    files = crud.get_files_by_draft_id(db, draft_id)

    for file in files:
        print("hmm", file.name)
    return {"files": files}
