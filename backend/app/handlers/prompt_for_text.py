from app.lm.models import (
    Message as ChatCompletionMessage,
)
from typing import BinaryIO
from fastapi import HTTPException
from app.models import DocumentDataExtractor
from app.ops import tup
from app.ops.documents import as_text
from app.services.excel_reader import excel_reader
from app.services.pdf_reader import pdf_reader
from app.models import ContentType

def validate_extracted_text(text: str):
    if text == "":
        raise HTTPException(
            status_code=500,
            detail="The extracted text from the document is empty. Please check if the document is corrupted.",
        ) 

async def full_prompt_from_text(file: BinaryIO, document_data_extractor: DocumentDataExtractor, upload_content_type: ContentType) -> list[ChatCompletionMessage]:
    
    if upload_content_type == ContentType.PDF:
        prompt = pdf_reader.as_text(file)
        validate_extracted_text(prompt)
    elif upload_content_type == ContentType.XLSX or upload_content_type == ContentType.XLS: 
        prompt = excel_reader.as_csv(file)
        validate_extracted_text(prompt)
    else:
        raise NotImplementedError(f'Content type {upload_content_type} not supported')
    
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