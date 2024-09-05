import io
from minio import Minio
from app.services.object_store import Documents


def test_documents(store: Minio) -> None:
    docs = Documents(object_store=store)
    f = io.BytesIO(b"some initial binary data: \x00\x01")
    docs.put("test", f)
    with docs.get("test") as g:
        print(f"We wrote the following data {g.read()}")