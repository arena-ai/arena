from app.lm.models import (
    Message as ChatCompletionMessage,
)
import base64
from io import BytesIO
from typing import TypedDict, BinaryIO
from app.models import DocumentDataExtractor
from app.ops import tup
from app.ops.documents import as_png
from app.services.pdf_reader import pdf_reader
from app.services.png_reader import png_reader
from app.models import ContentType
from app.lm.models.chat_completion import ContentTypes, ImageUrlContent, TextContent

BASE64_IMAGE_PREFIX = "data:image/png;base64"

     
def fill_input_image(image_input: BytesIO | list[tuple[int, BytesIO]]) -> list[ContentTypes]:

    def create_image_url_content(image: BytesIO) -> ImageUrlContent:
        img_bytes = image.getvalue()
        base64_image = (base64.b64encode(img_bytes).decode('utf-8'))
        return ImageUrlContent(
            type="image_url",
            image_url={"url": f"{BASE64_IMAGE_PREFIX},{base64_image}"}
        )

    if isinstance(image_input, BytesIO):
        return [create_image_url_content(image_input)]
    elif isinstance(image_input, list):
        content_list = []
        for idx, img in image_input:
            content_list.append(TextContent(type="text", text=f"####\nInput of page {idx}"))
            content_list.append(create_image_url_content(img))
        return content_list
    else:
        raise ValueError("Invalid input type for image_input")
    
#TODO rewrite with ChatCompletionMessage
#link to the OpenAI documentation specifying that only role 'user' is used for images:
#https://platform.openai.com/docs/guides/vision
async def full_prompt_from_image(file: BinaryIO, document_data_extractor: DocumentDataExtractor, upload_content_type: ContentType) -> list[ChatCompletionMessage]:
    if upload_content_type == ContentType.PDF:
        prompt = pdf_reader.as_pngs(file)
    elif upload_content_type == ContentType.PNG:
        prompt = png_reader.as_png(file)
    else:
        raise NotImplementedError(f'Content type {upload_content_type} not supported')
    
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
        ChatCompletionMessage(
            role="user",
            content=[
                TextContent(type="text", text=system_prompt)
            ]
        )
    ]
    for input_images, output_text in await examples.evaluate():
        for idx, image in enumerate(input_images, start=1):
            messages[0].content.append(
                TextContent(type="text", text=f"####\nInput of page {idx}")
            )
            messages[0].content.extend(fill_input_image(image))

        messages[0].content.append(
            TextContent(type="text", text=f"Expected Output: {output_text}\n\n")
        )

    messages[0].content.append(
        TextContent(type="text", text="Now, please apply the same analysis to the following new image:")
    )
    messages[0].content.extend(fill_input_image(prompt))
    
    return messages
