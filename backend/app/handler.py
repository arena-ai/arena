from app.lm.models import (
    Message as ChatCompletionMessage,
)
import base64
from typing import BinaryIO
from fastapi import HTTPException
from app.models import DocumentDataExtractor
from app.ops import tup
from app.ops.documents import as_text, as_png
from app.services.excel_reader import excel_reader
from app.services.pdf_reader import pdf_reader
from app.services.png_reader import png_reader
from enum import Enum
class ContentType(Enum):
    PDF = "application/pdf"  # PDF files
    XLS = "application/vnd.ms-excel"  # XLS files
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # XLSX (new Excel format)
    PNG = "image/png"  # PNG images

BASE64_IMAGE_PREFIX = "data:image/png;base64"

def validate_extracted_text(text: str):
    if text == "":
        raise HTTPException(
            status_code=500,
            detail="The extracted text from the document is empty. Please check if the document is corrupted.",
        ) 

async def full_prompt_from_text(file: BinaryIO, document_data_extractor: DocumentDataExtractor, upload_content_type:str) -> list[ChatCompletionMessage]:
    
    if upload_content_type == ContentType.PDF:
        prompt = pdf_reader.as_text(file)
        validate_extracted_text(prompt)
    if upload_content_type == ContentType.XLSX or upload_content_type == ContentType.XLS: 
        prompt = excel_reader.as_csv(file)
        validate_extracted_text(prompt)
        
    system_prompt = document_data_extractor.prompt

    examples = tup(
            *(
                tup(
                    as_text(
                        document_data_extractor.owner,
                        example.document_id,
                        example.start_page,
                        example.end_page,
                    ),
                    example.data,
                )
                for example in document_data_extractor.document_data_examples
            )
        )
    
    examples_text = ""
    for input_text, output_text in await examples.evaluate():
        validate_extracted_text(input_text)
        examples_text += (
            f"####\nINPUT: {input_text}\n\nOUTPUT: {output_text}\n\n"
        )
        
    full_system_content = f"{system_prompt}\n{examples_text}"
    messages = [
        ChatCompletionMessage(role="system", content=full_system_content),
        ChatCompletionMessage(
            role="user",
            content=f"Now, please apply the same analysis to the following new document:\n####\nINPUT:{prompt}",
        ),
    ]
    return messages
     
def fill_input_image(buffer: BinaryIO) -> dict:
    img_bytes = buffer.getvalue()
    base64_image=(base64.b64encode(img_bytes).decode('utf-8'))
    return {
        "type": "image_url",
        "image_url": {
            "url": f"{BASE64_IMAGE_PREFIX},{base64_image}",
        }
    }
    
#TODO rewrite with ChatCompletionMessage
#link to the OpenAI documentation specifying that only role 'user' is used for images:
#https://platform.openai.com/docs/guides/vision
async def full_prompt_from_image(file: BinaryIO, document_data_extractor: DocumentDataExtractor, upload_content_type:str) -> list[ChatCompletionMessage]:
    if upload_content_type == ContentType.PDF:
        prompt = pdf_reader.as_png(file)
    if upload_content_type == ContentType.PNG:
        prompt = png_reader.as_png(file)
    
    system_prompt = document_data_extractor.prompt
    
    examples = tup(
            *(
                tup(
                    as_png(
                        document_data_extractor.owner,
                        example.document_id,
                        example.start_page,
                        example.end_page,
                    ),
                    example.data,
                )
                for example in document_data_extractor.document_data_examples
            )
        )
    
    messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": system_prompt}
        ]
    }
    ]
    for input_text, output_text in await examples.evaluate():
        for idx, binary_io in enumerate(input_text, start=1):
            messages[0]["content"].append({
            "type": "text", 
            "text": f"####\nInput of page {idx}",
            })
        messages[0]["content"].append(fill_input_image(binary_io))

    messages[0]["content"].append({
        "type": "text", 
        "text": f"Expected Output: {output_text}\n\n"
    })

    messages[0]["content"].extend([
        {"type": "text", "text": "Now, please apply the same analysis to the following new image:"},
        fill_input_image(prompt)
    ])
    
    return messages




