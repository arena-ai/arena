from uuid import uuid4 as uuid
from io import BytesIO

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pymupdf

from app.api.deps import CurrentUser
from app.services.object_store import Documents


router = APIRouter()

class Document(BaseModel):
    name: str
    filename: str
    content_type: str


@router.post("/")
async def create_file(*, current_user: CurrentUser, upload: UploadFile) -> Document:
    docs = Documents()
    name: str = str(uuid())
    docs.put(f"{current_user.id}/{name}/data", upload.file)
    docs.puts(f"{current_user.id}/{name}/content_type", upload.content_type)
    return Document(name=name, filename=upload.filename, content_type=upload.content_type)


def list_paths(docs: Documents, current_user: CurrentUser):
    """List the paths"""
    prefixes = docs.list() if current_user.is_superuser else [f"{current_user.id}/"]
    return [path for prefix in prefixes for path in docs.list(prefix=prefix)]

@router.get("/")
async def read_files(*, current_user: CurrentUser):
    return [path.split('/')[1] for path in list_paths(Documents(), current_user)]


def get_path(docs: Documents, current_user: CurrentUser, name: str):
    """Get the path of a document from its name"""
    if current_user.is_superuser:
        return next(path for path in list_paths(docs, current_user) if path.split("/")[1]==name)
    else:
        return f"{current_user.id}/{name}/"

@router.get("/{name}")
async def read_file(*, current_user: CurrentUser, name: str):
    docs = Documents()
    path = get_path(docs, current_user, name)
    data = docs.get(f"{path}data")
    content_type = docs.gets(f"{path}content_type")
    return StreamingResponse(content=data.stream(), media_type=content_type)


@router.get("/{name}/as_text")
async def read_file_as_text(*, current_user: CurrentUser, name: str):
    user_id = current_user.id
    docs = Documents()
    path = get_path(docs, current_user, name)
    input = BytesIO(docs.get(f"{path}data").read())
    content_type = docs.gets(f"{path}content_type")
    if not docs.exists(f"{path}as_text"):
        # The doc should be created
        if content_type=='application/pdf':
            doc = pymupdf.Document(stream=input)
            output = BytesIO()
            for page in doc: # iterate the document pages
                text = page.get_text().encode("utf8") # get plain text (is in UTF-8)
                output.write(text) # write text of page
                output.write(bytes((12,))) # write page delimiter (form feed 0x0C)
            output.seek(0)
            docs.put(f"{path}as_text", output)
        else:
            docs.puts(f"{path}as_text", "Error: Could not read as text")
    # output the file
    input = docs.get(f"{path}as_text")
    return StreamingResponse(content=input.stream(), media_type='text/plain')