from typing import Any, Annotated

from fastapi import APIRouter, File, UploadFile

from app.api.deps import CurrentUser
from app.services.object_store import Documents

router = APIRouter()

@router.post("/uploadfile/")
async def create_upload_file(*, current_user: CurrentUser, upload: UploadFile):
    user_id = current_user.id
    docs = Documents()
    docs.put(f"{user_id}/{upload.filename}/data", upload.file)
    docs.puts(f"{user_id}/{upload.filename}/content_type", upload.content_type)
    return docs.list(recursive=True)
