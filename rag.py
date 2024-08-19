from typing import List

from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing_extensions import Annotated
from uuid import uuid4
import os
import shutil
import random
from rag_model import *


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIRECTORY = "/app/uploads"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
user_sessions = {}


@app.post("/uploadfiles/")
async def create_upload_files(
    files: Annotated[
        List[UploadFile], File(description="Multiple files as UploadFile")
    ],
):
    # user_sessions = {}
    session_id = str(uuid4())
    user_sessions[session_id] = {"token": random.random()}
    SESSION_DIRECTORY = UPLOAD_DIRECTORY + f"/{session_id}"
    os.makedirs(SESSION_DIRECTORY, exist_ok=True)
    for file in files:
        file_location = os.path.join(SESSION_DIRECTORY, file.filename)
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
    return {"session_id": session_id}


class Quest(BaseModel):
    session_id: str
    question: str


@app.post("/question")
async def ask_question(quest: Quest):
    if quest.session_id not in user_sessions:
        return {"error": "Invalid session ID"}

    # Add the question to the session
    user_sessions[quest.session_id]["question"] = quest.question
    return {"status": "Processing"}


@app.get("/event/{session_id}")
async def sse_stream(session_id: str):
    print(user_sessions, "sedddd")
    return StreamingResponse(return_query(user_sessions[session_id]["question"], session_id), media_type="text/event-stream")


@app.get("/get-waypoints")
async def root():
    return StreamingResponse(waypoints_generator(), media_type="text/event-stream")


@app.get("/")
async def main():
    content = """
<body>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post" multiple>
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
