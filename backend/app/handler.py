from abc import ABC, abstractmethod
from app.lm.models import (
    ChatCompletionRequest,
    Message as ChatCompletionMessage,
)
import base64
from typing import BinaryIO
from app.api.routes.dde import validate_extracted_text

#two methonds that create the message out of an image or a text 

##add a logic to choose between text or png when i have a pdf 
    #start extracting information from text and if the logprob are too low use png
    #add a setting in the dde when i upload examples

##add a logic of looking up the type and converting the input into text or png 

async def full_prompt_from_text(system_prompt:str, prompt:str, examples)-> list[ChatCompletionMessage]:
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
            content=f"Maintenant, faites la même extraction sur un nouveau document d'input:\n####\nINPUT:{prompt}",
        ),
    ]
    return messages

def fill_input_image(buffer: BinaryIO) -> dict:
    img_bytes = buffer.getvalue()
    base64_image=(base64.b64encode(img_bytes).decode('utf-8'))
    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/png;base64,{base64_image}",
        }
    }
    
#rewrite with ChatCompletionMessage
#link to the OpenAI documentation specifying that only role 'user' is used for images.
#https://platform.openai.com/docs/guides/vision
async def full_prompt_from_image(system_prompt:str, prompt: BinaryIO, examples) -> list[ChatCompletionMessage]:
    
    messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": system_prompt}
        ]
    }
    ]
    for input_text, output_text in examples:
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




