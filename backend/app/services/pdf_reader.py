from typing import BinaryIO
from dataclasses import dataclass
import pymupdf
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO

@dataclass
class PDFReader:
    sort: bool = True

    def as_text(
        self,
        pdf_data: BinaryIO,
        start_page: int = 0,
        end_page: int | None = None,
    ) -> str:
        text = ""
        doc = pymupdf.Document(stream=pdf_data)

        pages = [
            page_num
            for page_num, page in enumerate(doc)
            if page_num >= start_page and (not end_page or page_num < end_page)
        ]

        for page_num in pages:
            page = doc.load_page(page_num)
            page_text = " ".join(
                elem[4] for elem in page.get_text("words", sort=self.sort)
            )
            text += page_text

        if not text.strip():
            text = self.perform_ocr_on_page(pdf_data)

        return text

    def perform_ocr_on_page(self, pdf_data: BinaryIO) -> str:
        text = ""
        images = convert_from_bytes(pdf_data.read())
        for image in images:
            ocr_text = pytesseract.image_to_string(image)
            text += ocr_text

        return text
    
    def as_png(
        self,
        pdf_data: BinaryIO,
        start_page: int = 0,
        end_page: int | None = None,
    ) -> list[tuple[int, BinaryIO]]:
        
        doc = pymupdf.Document(stream=pdf_data)
        pages = [
            page_num
            for page_num, page in enumerate(doc)
            if page_num >= start_page and (not end_page or page_num < end_page)
        ]
        page_buffer_pairs = []

        for page_num in pages:
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=96, colorspace="csRGB", alpha=False)      
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            buffer = BytesIO()
            img.save(buffer, format="PNG", optimize=True, compress_level=0)
            page_buffer_pairs.append((page_num, buffer))

        return page_buffer_pairs


# A default instance
pdf_reader = PDFReader()
