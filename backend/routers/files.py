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

import tempfile

from langchain.document_loaders import PyMuPDFLoader
load_dotenv()

router = APIRouter(tags=["files"])
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

@router.get('/checking')
async def checking():
    files = [{'name': '5031-Article Text-8094-1-10-20190709.pdf', 'url': '8-10-8d3244c9-73b2-4ea6-ba7e-642d582abc4f.pdf'}, {'name': 'sec-guide-to-savings-and-investing.pdf', 'url': '8-10-b771aeab-6ed8-472e-b994-561e3808cfc1.pdf'}]

    return await get_file_from_r2(files)



async def get_file_from_r2(files):

    content = []

    for file in files:
        
        original_file_name = file['name']
        file_key = file['url']
        file_key = f"uploads/{file_key}"

        try:
            response = s3.get_object(Bucket=os.getenv("BUCKET_NAME"), Key=file_key)
            file_content = response['Body'].read()

            # Save the content to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            # Use PyMuPDFLoader to load the temporary file
            loader = PyMuPDFLoader(temp_file_path)
            doc = loader.load()

            for item in doc:
                item.metadata['source'] = original_file_name
                item.metadata['file_path'] = original_file_name
            # Close and delete the temporary file
            os.remove(temp_file_path)

            content += doc
    
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{e}")

    return content



@router.post("/upload-file")
async def upload_file(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
):  # let's take nothing from the response body for now
    user_id = current_user.id

    # modified filename
    original_filename = file.filename
    filename = f"{user_id}-{uuid.uuid4()}.{file.filename.split('.')[-1]}"
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
        saved_file = crud.save_file(db, original_filename, filename, user_id)
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


def delete_from_r2(filename):
    try:
        s3.delete_object(Bucket=os.getenv("BUCKET_NAME"), Key=filename)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting file to S3: {str(e)}"
        )

    return True

@router.post("/update-files-toggle", )
def update_files_toggle(file_states: schemas.DynamicFileStates, current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_db)):
    print(file_states)

    all_files = file_states.states

    for item, value in all_files.items():
        print('item', item, 'value', value)
        file = crud.update_each_file_toggle(db,int(item), value)
    
    return {'done' : 'yes'}



@router.get("/delete-file")
def delete_file(
    file_id: int,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    file = crud.get_file_by_id(db, file_id)

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    deleted = delete_from_r2(f"uploads/{file.url}")

    if deleted:
        db.delete(file)  # deleting from the database too
        db.commit()

    return {"success": True}


# get the downlaod link from s3
def get_download_link(filename):
    response = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": os.getenv("BUCKET_NAME"), "Key": filename},
        ExpiresIn=60,
    )

    return response


@router.get("/download-file")
def download_file(
    file_id: int,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    file = crud.get_file_by_id(db, file_id)

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    link = get_download_link(f"uploads/{file.url}")

    return {"link": link}

