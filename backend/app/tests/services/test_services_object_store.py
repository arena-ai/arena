import io
from minio import Minio
from app.services.object_store import Documents


def test_documents(object_store: Minio) -> None:
    docs = Documents(object_store=object_store)
    f = io.BytesIO(b"some initial binary data: \x00\x01")
    docs.put("test", f)
    with docs.get("test") as g:
        print(f"We wrote the following data {g.read()}")
    # Add more files
    for i in range(10):
        f = io.BytesIO(b"some initial binary data: \x00\x01 "+f"{i}".encode())
        docs.put(f"obj_{i}", f)
    print(f"We wrote the following objects {docs.list()}")
    # Add more files
    for i in range(10):
        f = io.BytesIO(b"some initial binary data: \x00\x01 "+f"{i}".encode())
        docs.put(f"user/obj_{i}", f)
    print(f"We wrote the following objects {docs.list(prefix='user/')}")

