from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

from app.services import crud
from app.models import UserCreate, Setting, SettingCreate
from app.tests.utils.utils import random_email, random_lower_string

def test_create_setting(db: Session) -> None:
    user = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    setting = crud.create_setting(session=db, setting_in=SettingCreate(name="OPENAI_API_KEY", content=random_lower_string()), owner_id=user.id)
    assert setting.owner.id == user.id
    assert len(user.settings) == 1

def test_get_setting(db: Session) -> None:
    user = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    setting = crud.create_setting(session=db, setting_in=SettingCreate(name="OPENAI_API_KEY", content="1"), owner_id=user.id)
    setting = crud.create_setting(session=db, setting_in=SettingCreate(name="OPENAI_API_KEY", content="2"), owner_id=user.id)
    setting = crud.create_setting(session=db, setting_in=SettingCreate(name="OPENAI_API_KEY", content="3"), owner_id=user.id)
    setting = crud.get_setting(session=db, setting_name="OPENAI_API_KEY", owner_id=user.id)
    assert setting.owner.id == user.id
    assert setting.content == "3"
