from uuid import uuid4 as uuid
from typing import Any, Annotated

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from app.api.deps import CurrentUser
from app.services.object_store import Documents


router = APIRouter()

class Document(BaseModel):
    name: str
    filename: str
    content_type: str


@router.post("/file")
async def create_file(*, current_user: CurrentUser, upload: UploadFile) -> Document:
    user_id = current_user.id
    docs = Documents()
    name: str = str(uuid())
    docs.put(f"{user_id}/{name}/data", upload.file)
    docs.puts(f"{user_id}/{name}/content_type", upload.content_type)
    return Document(name=name, filename=upload.filename, content_type=upload.content_type)


@router.get("/file/{name}")
async def create_upload_file(*, current_user: CurrentUser, name: str):
    user_id = current_user.id
    docs = Documents()
    docs.get(f"{user_id}/{name}/data")
    return StreamingResponse()