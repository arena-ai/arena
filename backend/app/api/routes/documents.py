from typing import Any, Annotated

from fastapi import APIRouter, File, UploadFile

from app.api.deps import CurrentUser
from app.services.object_store import Documents

router = APIRouter()

@router.post("/uploadfile/")
async def create_upload_file(*, current_user: CurrentUser, upload: UploadFile):
    user_id = current_user.id
    content_type = upload.content_type.lower().replace("/", "_")
    name = f"{user_id}/{content_type}/{upload.filename}"
    docs = Documents()
    docs.put(name, upload.file)
    return docs.list(recursive=True)
