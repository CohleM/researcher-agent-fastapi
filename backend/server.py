from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import traceback
# from websocket_manager import WebSocketManager
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
import time
from typing import AsyncGenerator, NoReturn

from .websocket_manager import WebSocketManager
from .routers.authentication import get_current_user,get_current_user_websocket
from datetime import datetime, timedelta

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from researcher.utils.functions import stream_output, notes_from_youtube
from researcher.config import Config
from passlib.context import CryptContext
from pydantic import BaseModel
import requests
import json
import os



##db
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from . import crud, models, schemas

from .database import SessionLocal, engine

from .routers import users, authentication, drafts, files, payments
import sys

# sys.path.append("/Users/cohlem/projects/FastAPI/")
# sys.path.append("/Users/cohlem/Projects/FastAPI/backend-fastapi")
from dotenv import load_dotenv
from researcher.core.agent import Researcher
from threading import Event

from starlette.requests import Request 
from starlette.middleware.sessions import SessionMiddleware 



models.Base.metadata.create_all(bind=engine)

load_dotenv()

# Initials
manager = WebSocketManager()
app = FastAPI()
client = AsyncOpenAI()

stop_event = Event()

app.include_router(users.router)
app.include_router(authentication.router)
app.include_router(drafts.router)
app.include_router(files.router)
app.include_router(payments.router)


# Add this before defining your FastAPI app
origins = [
    "http://localhost",
    "http://localhost:3000",
    f"{os.getenv('FRONTEND_URL')}"
]

# Add this to your FastAPI app
app.add_middleware(SessionMiddleware ,secret_key='maihoonjiyan') 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_file_details(file_state):

        enable_files = False
        # Check if we need to search files
        files_to_read = []
        all_files = []
        for item, value in file_state.items():
            if value:
                files_to_read.append(item)
                enable_files = True


        if enable_files:
            all_files = crud.get_filenames_from_ids(files_to_read, next(get_db()))

        return all_files 


@app.get("/stop-stream")
async def stop_stream(current_user: Annotated[schemas.UserResponse, Depends(get_current_user)]):
    if current_user:
        stop_event.set()
        print('yaas stopped the stream')
        return {"message": "Streaming is stopped"}



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket ) -> NoReturn:
    """
    Websocket for AI responses
    """
    # print('WEBSOCKET,', current_user)
    ## pass the token from the frontend on every request. 
    await manager.connect(websocket)

    while True:
        message = await websocket.receive_json() # message has type { 'text' : text, 'allAIOptions' : allAIOptions}

        # print('Thsii is message',message)
        token = message['allAIOptions']['Token']
        file_state = message['allAIOptions']['FileState']
        file_state = dict(file_state)

        files = get_file_details(file_state)
        search_type = 'web'
        if (len(files) > 0 and message['allAIOptions']['webSearch']==True):
            search_type = 'both'
        elif (len(files) == 0 and message['allAIOptions']['webSearch']==True):
            search_type= 'web'
        elif (len(files) > 0 and message['allAIOptions']['webSearch']==False):
            search_type = 'files'
        else:
            search_type = None



        try:
            current_user = await get_current_user_websocket(token, next(get_db()))

            if current_user:
                current_datetime = datetime.utcnow()

                if current_user.credits is None or current_user.credits < 10 or current_user.credits_expiration_date < current_datetime:
                    print('Insufficient credit')
                    await websocket.send_json({"error": "Insufficient credits or Credits have expired", 'authenticated': 'yes'})
                    continue  # Skip processing if credits are insufficient
                # allAIOptions has type type AIOptionsType = { AICommands : string, webSearch : boolean }



                query = message['allAIOptions']['Text']
                options = message['allAIOptions']
                credit_usage = 0
                stop_event.clear()


                if options['AICommands'] == '1': # 1 belongs to generate report
                    await stream_output(f"📘 Starting research for query: {query}", websocket=websocket)
                    result = Researcher(query, search_type, websocket, files=files).run_researcher_agent(stop_event)
                    credit_usage = 10
                elif options['AICommands'] == '2': # 2 belongs to generate QA
                    result = Researcher(query,search_type, websocket, files=files).run_qa_agent(stop_event)
                    credit_usage = 5
                elif options['AICommands'] == '3' and options['webSearch'] == False: # 3 belongs to Summarization 
                    credit_usage = 2 
                    result = Researcher(query,search_type, websocket).run_summarization_agent(stop_event)
                elif options['AICommands'] == '4' and options['webSearch'] == False: # 4 belongs to generate Paraphrase
                    credit_usage = 2 
                    result = Researcher(query,search_type,websocket).run_paraphrasing_agent(stop_event)
                elif options['AICommands'] == '5':
                    print('Starting YT notes')
                    link = options['Link']
                    yt_notes = await notes_from_youtube(link,cfg = Config())
                    print('\n\n YT notes', yt_notes)
                    await websocket.send_json({"content": yt_notes, "finish_reason": "stop", 'authenticated' : 'yes', 'error' : 'none'})
                    continue 

                async for text, finish_reason in result:
                    # print(text, finish_reason)
                    await websocket.send_json({"content": text, "finish_reason": finish_reason, 'authenticated' : 'yes', 'error' : 'none'})

                updated = crud.update_credits(current_user.email, (-credit_usage), db =  next(get_db()))

            else:
                await websocket.send_json({'authenticated' : 'no'})

        except Exception as e:
            print('Error occured', e)
            traceback.print_exc()
            await websocket.send_json({'authenticated' : 'no'})


# ### testing database
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud.create_user(db=db, user=user)


# @app.get("/users/", response_model=list[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users


# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=list[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items
