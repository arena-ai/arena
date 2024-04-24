from fastapi import APIRouter

from app.api.routes import settings, events, login, users, utils
from app.lm.api.routes import chat_completion

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
# Include language_models
api_router.include_router(chat_completion.router, prefix="/lm", tags=["language-models"])
