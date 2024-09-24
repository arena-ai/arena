from typing import BinaryIO
from dataclasses import dataclass
import pymupdf
from io import StringIO


@dataclass
class PDFReader:
    file_type: str = "pdf"
    sort: bool = True
    format_type: str = 'words'

    def as_text(self, pdf_data: BinaryIO, start_page: int = 0, end_page: int | None = None) -> str:
        text = ""
        output = StringIO()
        doc = pymupdf.Document(stream=pdf_data)
        pages = [page_num for page_num, page in enumerate(doc) if page_num>=start_page and (not end_page or page_num<end_page)] 
        for page_num in pages:
            page = doc.load_page(page_num)
            if self.format_type == 'words':
                page_text = " ".join(elem[4] for elem in page.get_text(self.format_type, sort=self.sort))
            else: 
                raise NotImplementedError('format_type not accepted')
            text += page_text
            
        #TODO add OCR           
        output.write(f"{text}\f") 

        return output.getvalue() 

# A default instance
pdf_reader = PDFReader()