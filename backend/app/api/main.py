from fastapi import APIRouter

from app.api.routes import (
    dde,
    documents,
    settings,
    events,
    login,
    users,
    utils,
)
from app.lm.api.routes import chat_completion, evaluation

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(
    settings.router, prefix="/settings", tags=["settings"]
)
# Documents
api_router.include_router(
    documents.router, prefix="/documents", tags=["documents"]
)
# Document Data Extraction
api_router.include_router(
    dde.router, prefix="/dde", tags=["document-data-extractors"]
)
# Include language_models
api_router.include_router(
    chat_completion.router,
    prefix="/lm",
    tags=["language-models-chat-completion"],
)
api_router.include_router(
    evaluation.router, prefix="/lm", tags=["language-models-evaluation"]
)
