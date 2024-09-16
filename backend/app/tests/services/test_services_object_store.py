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
    # Remove one object
    docs.remove("test")
    docs.remove("obj_3")
    docs.remove("user/obj_3")
    docs.puts(f"user/test_string", "Hello world")
    print(docs.gets(f"user/test_string"))
    print(f"After removal we have the following objects {docs.list() + docs.list(prefix='user/')}")
    print(f'user/test_string exists: {docs.exists(f"user/test_string")}')
    print(f'user/unknown exists: {docs.exists(f"user/unknown")}')

