from io import BytesIO
from typing import BinaryIO
from app.models import User
from app.ops import Op
from app.services.object_store import documents
from app.services.pdf_reader import pdf_reader
from app.services.excel_reader import excel_reader
from app.services.png_reader import png_reader

class Paths(Op[User, list[str]]):
    async def call(self, user: User) -> list[str]:
        prefixes = documents.list() if user.is_superuser else [f"{user.id}/"]
        return [
            path
            for prefix in prefixes
            for path in documents.list(prefix=prefix)
        ]


paths = Paths()


class Path(Op[tuple[User, str], str]):
    async def call(self, user: User, name: str) -> str:
        """Get the path of a document from its name"""
        if user.is_superuser:
            return next(
                path
                for path in await paths.call(user)
                if path.split("/")[1] == name
            )
        else:
            return f"{user.id}/{name}/"


path = Path()


class AsText(Op[tuple[User, str], str]):
    async def call(
        self,
        user: User,
        name: str,
        start_page: int = 0,
        end_page: int | None = None,
    ) -> str:
        source_path = await path.call(user, name)
        input = BytesIO(documents.get(f"{source_path}data").read())
        content_type = documents.gets(f"{source_path}content_type")
        if end_page:
            path_as_text = (
                f"{source_path}as_text_from_page_{start_page}_to_{end_page}"
            )
        elif start_page > 0:
            path_as_text = f"{source_path}as_text_from_page_{start_page}"
        else:
            path_as_text = f"{source_path}as_text"

        if not documents.exists(path_as_text):
            # The doc should be created
            if content_type == "application/pdf":
                documents.puts(
                    path_as_text,
                    pdf_reader.as_text(
                        input, start_page=start_page, end_page=end_page
                    ),
                )
            elif content_type == "application/vnd.ms-excel":
                documents.puts(
                    path_as_text,
                    excel_reader.as_csv(input)
                    )
            else:
                documents.puts(path_as_text, "Error: Could not read as text")
        # output the file
        output = documents.get(path_as_text)
        return output.read().decode("utf8")


as_text = AsText()

        
class AsPng(Op[tuple[User, str], str]):
    async def call(
        self,
        user: User,
        name: str,
        start_page: int = 0,
        end_page: int | None = None,
    ) -> list[BinaryIO]:
        source_path = await path.call(user, name)
        input = BytesIO(documents.get(f"{source_path}data").read())
        content_type = documents.gets(f"{source_path}content_type")

        path_as_png = f"{source_path}as_png"
        binary_buffers = []
        if content_type == "application/pdf":
            page_buffer = pdf_reader.as_png(input, start_page=start_page, end_page=end_page)
            for page, byte_stream in page_buffer:
                specific_path_as_png = f"{path_as_png}_page_{page}"
                documents.put(
                            specific_path_as_png,
                            byte_stream
                            ),
                binary_buffers.append(byte_stream)
            return binary_buffers
        
        elif content_type == "image/png":  
            page, byte_stream = png_reader.as_png(input)
            documents.put(
                        path_as_png,
                        byte_stream
                        ),
            return [byte_stream]
        else:
            documents.puts(path_as_png, "Error: Could not read as png")
            return [BytesIO(b"Error: Could not read as png")] 
         
as_png = AsPng()