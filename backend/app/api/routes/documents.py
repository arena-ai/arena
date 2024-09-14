from uuid import uuid4 as uuid
from typing import Any, Annotated

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.deps import CurrentUser
from app.services.object_store import Documents


router = APIRouter()

class Document(BaseModel):
    name: str
    filename: str
    content_type: str


@router.post("/")
async def create_file(*, current_user: CurrentUser, upload: UploadFile) -> Document:
    user_id = current_user.id
    docs = Documents()
    name: str = str(uuid())
    docs.put(f"{user_id}/{name}/data", upload.file)
    docs.puts(f"{user_id}/{name}/content_type", upload.content_type)
    return Document(name=name, filename=upload.filename, content_type=upload.content_type)


def list_paths(docs: Documents, current_user: CurrentUser):
    prefixes = docs.list() if current_user.is_superuser else [f"{current_user.id}/"]
    return [path for prefix in prefixes for path in docs.list(prefix=prefix)]

@router.get("/")
async def read_files(*, current_user: CurrentUser):
    return [path.split('/')[1] for path in list_paths(Documents(), current_user)]


def get_path(docs: Documents, current_user: CurrentUser, name: str):
    if current_user.is_superuser:
        return next(path for path in list_paths(docs, current_user) if path.split("/")[1]==name)
    else:
        return f"{current_user.id}/{name}/"

@router.get("/{name}")
async def read_file(*, current_user: CurrentUser, name: str):
    user_id = current_user.id
    docs = Documents()
    path = get_path(docs, current_user, name)
    data = docs.get(f"{path}data")
    content_type = docs.gets(f"{path}content_type")
    return StreamingResponse(content=data.stream(), media_type=content_type)