from anyio import run
from sqlmodel import Session

from app.services import crud
from app.models import UserCreate
from app.ops.session import session, user
from app.ops.documents import path, paths, as_text
from app.ops.utils import tup
from app.tests.utils.utils import random_email, random_lower_string


def test_paths(db: Session) -> None:
    ses = session()
    random_user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(),
            password=random_lower_string(),
            is_superuser=True,
        ),
    )
    usr = user(ses, random_user.id)
    val = paths(usr)

    async def test_eval():
        return await val.evaluate(session=db)

    print(run(test_eval))


def test_path(db: Session) -> None:
    ses = session()
    random_user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(),
            password=random_lower_string(),
            is_superuser=True,
        ),
    )
    usr = user(ses, random_user.id)
    path_list = paths(usr)
    name = path_list[0].split("/")[1]
    selected_path = path(usr, name)
    result = tup(name, selected_path)

    async def test_eval():
        return await result.evaluate(session=db)

    print(run(test_eval))


def test_as_text(db: Session) -> None:
    ses = session()
    random_user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(),
            password=random_lower_string(),
            is_superuser=True,
        ),
    )
    usr = user(ses, random_user.id)
    path_list = paths(usr)
    name = path_list[0].split("/")[1]
    selected_text = as_text(usr, name)
    result = tup(name, selected_text)

    async def test_eval():
        return await result.evaluate(session=db)

    print(run(test_eval))
