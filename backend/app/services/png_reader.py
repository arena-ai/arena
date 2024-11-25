from PIL import Image
from typing import BinaryIO
from io import BytesIO
from dataclasses import dataclass

@dataclass
class PNGReader:
    def as_png(
        self,
        png_data: BinaryIO,
    ) -> BinaryIO:

        img = Image.open(png_data)
        buffer = BytesIO()
        img.save(buffer, format="PNG", optimize=True, compress_level=0)
        return buffer

# A default instance
png_reader = PNGReader()