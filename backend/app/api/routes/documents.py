from uuid import uuid4 as uuid
from io import BytesIO

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pymupdf

from app.api.deps import CurrentUser
from app.services.object_store import documents
from app.ops.documents import path, paths, as_text


router = APIRouter()

class Document(BaseModel):
    name: str
    filename: str
    content_type: str


class Documents(BaseModel):
    data: list[Document]
    count: int


@router.post("/")
async def create_file(*, current_user: CurrentUser, upload: UploadFile) -> Document:
    name: str = str(uuid())
    document = Document(name=name, filename=upload.filename, content_type=upload.content_type)
    documents.put(f"{current_user.id}/{name}/data", upload.file)
    documents.puts(f"{current_user.id}/{name}/metadata", document.model_dump_json())
    documents.puts(f"{current_user.id}/{name}/content_type", upload.content_type)
    return document


@router.get("/")
async def read_files(*, current_user: CurrentUser) -> Documents:
    document_paths = await paths(current_user).evaluate()
    return Documents(data=[Document.model_validate_json(documents.gets(f"{path}metadata")) for path in document_paths], count=len(document_paths))


@router.get("/{name}")
async def read_file(*, current_user: CurrentUser, name: str) -> StreamingResponse:
    document_path = await path(current_user, name).evaluate()
    data = documents.get(f"{document_path}data")
    return StreamingResponse(content=data.stream(), media_type='application/octet-stream')


@router.get("/{name}/as_text")
async def read_file_as_text(*, current_user: CurrentUser, name: str, start_page: int = 0, end_page: int | None = None) -> str:
    return await as_text(current_user, name, start_page, end_page).evaluate()