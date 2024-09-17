import io
from anyio import run
from sqlmodel import Session

from app import crud
from app.models import UserCreate
from app.ops.session import session, user
from app.ops.documents import Paths
from app.tests.utils.utils import random_email, random_lower_string


def test_paths(db: Session) -> None:
    paths = Paths()
    ses = session()
    random_user = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    usr = user(ses, random_user.id)
    val = paths(usr)
    async def test_eval():
        return await val.evaluate(session=db)
    print(run(test_eval))