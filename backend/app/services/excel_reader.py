from typing import BinaryIO
from dataclasses import dataclass
import pandas as pd

@dataclass
class XLSXReader:
    def as_csv(
        self,
        pdf_data: BinaryIO
    ) -> str:
        
        df = pd.read_excel(pdf_data)
        #formatting decimal numbers to 3 digits to reduce text length.
        text = df.to_csv(index=False, float_format="%.3f")
        
        return text

# A default instance
excel_reader = XLSXReader()