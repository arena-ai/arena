import io
from anyio import run

from app.models import UserOut
from app.ops.documents import Paths


def test_paths() -> None:
    paths = Paths()
    run(paths(UserOut(      
        email='admin@example.com',
        is_active=True,
        is_superuser=True,
        password='foo',
        id=1,
        )))