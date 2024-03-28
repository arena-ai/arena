from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.models import Message, SettingCreate, Setting, SettingsOut, SettingOut

router = APIRouter()


@router.get("/", response_model=SettingsOut)
def read_settings(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve Settings.
    """

    if current_user.is_superuser:
        statement = select(func.count()).select_from(Setting)
        count = session.exec(statement).one()
        statement = select(Setting).offset(skip).limit(limit)
        settings = session.exec(statement).all()
    else:
        statement = (
            select(func.count())
            .select_from(Setting)
            .where(Setting.owner_id == current_user.id)
        )
        count = session.exec(statement).one()
        statement = (
            select(Setting)
            .where(Setting.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        settings = session.exec(statement).all()

    return SettingsOut(data=settings, count=count)


@router.get("/{name}", response_model=SettingOut)
def read_setting(session: SessionDep, current_user: CurrentUser, name: str) -> Any:
    """
    Get setting by name.
    """
    setting = crud.get_setting(session=session, setting_name=name, owner_id=current_user.id)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    if not current_user.is_superuser and (setting.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return setting


@router.post("/", response_model=SettingOut)
def create_setting(
    *, session: SessionDep, current_user: CurrentUser, setting_in: SettingCreate
) -> Any:
    """
    Create new setting.
    """
    setting = Setting.model_validate(setting_in, update={"owner_id": current_user.id})
    session.add(setting)
    session.commit()
    session.refresh(setting)
    return setting


@router.post("/{name}/{content}", response_model=SettingOut)
def create_setting_get(
    *, session: SessionDep, current_user: CurrentUser, name: str, content: str
) -> Any:
    """
    Create new setting.
    """
    setting = Setting(name=name, content=content, owner_id=current_user.id)
    session.add(setting)
    session.commit()
    session.refresh(setting)
    return setting