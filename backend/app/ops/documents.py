from typing import Mapping
from io import BytesIO
from pydantic import Field, ConfigDict
from faker import Faker
from sqlmodel import Session
import pymupdf

from app.models import User
from app.services.masking import Analyzer, AnalyzerRequest, Anonymizer, AnonymizerRequest, Anonymizers, Replace, Redact, Mask, Hash, Encrypt, Keep
from app.ops import Op
from app.api.deps import CurrentUser
from app.services.object_store import documents, Documents

class Paths(Op[User, list[str]]):
    async def call(self, user: User) -> list[str]:
        prefixes = documents.list() if user.is_superuser else [f"{user.id}/"]
        return [path for prefix in prefixes for path in documents.list(prefix=prefix)]

paths = Paths()


class Path(Op[tuple[User, str], str]):
    async def call(self, user: User, name: str) -> str:
        """Get the path of a document from its name"""
        if user.is_superuser:
            return next(path for path in await paths.call(user) if path.split("/")[1]==name)
        else:
            return f"{user.id}/{name}/"

path = Path()


class AsText(Op[tuple[User, str], str]):
    async def call(self, user: User, name: str, start_page: int = 0, end_page: int | None = None) -> str:
        source_path = await path.call(user, name)
        input = BytesIO(documents.get(f"{source_path}data").read())
        content_type = documents.gets(f"{source_path}content_type")
        if end_page:
            path_as_text = f"{source_path}as_text_from_page_{start_page}_to_{end_page}"
        elif start_page>0:
            path_as_text = f"{source_path}as_text_from_page_{start_page}"
        else:
            path_as_text = f"{source_path}as_text"
        if not documents.exists(path_as_text):
            # The doc should be created
            if content_type=='application/pdf':
                doc = pymupdf.Document(stream=input)
                output = BytesIO()
                pages = [page for page_num, page in enumerate(doc) if page_num>=start_page and (not end_page or page_num<end_page)]
                for page in pages: # iterate the document pages
                    text = page.get_text().encode('utf8') # get plain text (is in UTF-8)
                    output.write(text) # write text of page
                    output.write(bytes((12,))) # write page delimiter (form feed 0x0C)
                output.seek(0)
                documents.put(path_as_text, output)
            else:
                documents.puts(path_as_text, "Error: Could not read as text")
        # output the file
        output = documents.get(path_as_text)
        return output.read().decode('utf8')

as_text = AsText()
