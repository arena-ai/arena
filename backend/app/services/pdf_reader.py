from typing import BinaryIO
from dataclasses import dataclass
import pymupdf
import pytesseract
from io import StringIO, BytesIO
from PIL import Image
from pdf2image import convert_from_bytes

@dataclass
class PDFReader:
    sort: bool = True

    def as_text(self, pdf_data: BinaryIO, start_page: int = 0, end_page: int | None = None) -> str:
        text = ""
        output = StringIO()
        doc = pymupdf.Document(stream=pdf_data)
        
        pages = [page_num for page_num, page in enumerate(doc) if page_num >= start_page and (not end_page or page_num < end_page)]
        
        for page_num in pages:
            page = doc.load_page(page_num)
            page_text = " ".join(elem[4] for elem in page.get_text('words', sort=self.sort))
            text += page_text
        
        if not text.strip():
            text = self.perform_ocr_on_page(pdf_data)
        
        output.write(f"{text}\f") 
        return output.getvalue()


    def perform_ocr_on_page(self, pdf_data: BinaryIO) -> str:
        text = ""
        pdf_data.seek(0)  
        file_stream = BytesIO(pdf_data.read()) 
        images = convert_from_bytes(file_stream.read())
        for image in images:
            ocr_text = pytesseract.image_to_string(image)
            text += ocr_text
    
        return text
        

# A default instance
pdf_reader = PDFReader()
