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
        text = df.to_csv(index=False)
        
        return text

# A default instance
excel_reader = XLSXReader()