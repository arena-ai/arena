from uuid import uuid4 as uuid
from io import BytesIO
from datetime import datetime, UTC
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pymupdf

from app.api.deps import CurrentUser
from app.services.object_store import documents
from app.ops.documents import path, paths, as_text
from app.models import Message


router = APIRouter()

class Document(BaseModel):
    name: str
    filename: str
    content_type: str
    timestamp: datetime


class Documents(BaseModel):
    data: list[Document]
    count: int


@router.post("/")
async def create_file(*, current_user: CurrentUser, upload: UploadFile) -> Document:
    name: str = str(uuid())
    document = Document(name=name, filename=upload.filename, content_type=upload.content_type, timestamp=datetime.now(UTC))
    documents.put(f"{current_user.id}/{name}/data", upload.file)
    documents.puts(f"{current_user.id}/{name}/metadata", document.model_dump_json())
    documents.puts(f"{current_user.id}/{name}/content_type", upload.content_type)
    return document


@router.get("/")
async def read_files(*, current_user: CurrentUser) -> Documents:
    document_paths = await paths(current_user).evaluate()
    return Documents(data=sorted([Document.model_validate_json(documents.gets(f"{path}metadata")) for path in document_paths], key=lambda doc: doc.timestamp, reverse=True), count=len(document_paths))


@router.get("/{name}")
async def read_file(*, current_user: CurrentUser, name: str) -> StreamingResponse:
    document_path = await path(current_user, name).evaluate()
    data = documents.get(f"{document_path}data")
    return StreamingResponse(content=data.stream(), media_type='application/octet-stream')


@router.delete("/{name}")
async def delete_file(*, current_user: CurrentUser, name: str) -> Message:
    """
    Delete a file.
    """
    document_path = await path(current_user, name).evaluate()
    documents.remove_all(f"{document_path}")
    return Message(message="Document deleted successfully")


@router.get("/{name}/as_text")
async def read_file_as_text(*, current_user: CurrentUser, name: str, start_page: int = 0, end_page: int | None = None) -> str:
    return await as_text(current_user, name, start_page, end_page).evaluate()