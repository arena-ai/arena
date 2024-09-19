from typing import BinaryIO
from dataclasses import dataclass
import pymupdf
from io import StringIO



@dataclass
class PDFReader:
    sorted: bool = True

    def as_text(self, pdf_data: BinaryIO, start_page: int = 0, end_page: int | None = None) -> str:
        doc = pymupdf.Document(stream=pdf_data)
        output = StringIO()
        pages = [page for page_num, page in enumerate(doc) if page_num>=start_page and (not end_page or page_num<end_page)]
        for page in pages: # iterate the document pages
            text = page.get_text(sorted=self.sorted)
            output.write(f"{text}\f") # write text of page
        return output.getvalue()

# A default instance
pdf_reader = PDFReader()