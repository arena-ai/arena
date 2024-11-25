from typing import Any, Literal
from fastapi import APIRouter, HTTPException, status, UploadFile
from fastapi.responses import JSONResponse
from sqlmodel import func, select
from sqlalchemy.exc import IntegrityError
import json
import io
import re
from pydantic import create_model, ValidationError
from app.api.deps import CurrentUser, SessionDep
from app.services import crud
from app.lm.models import (
    ChatCompletionRequest,
    Message as ChatCompletionMessage,
    TokenLogprob,
)
from app.services.object_store import documents
from app.services.pdf_reader import pdf_reader
from app.services.excel_reader import excel_reader
from app.services.png_reader import png_reader
from app.lm.handlers import ArenaHandler
from app.ops import tup
from app.ops.documents import as_text, as_png
from app.models import (
    Message,
    DocumentDataExtractorCreate,
    DocumentDataExtractorUpdate,
    DocumentDataExtractor,
    DocumentDataExtractorOut,
    DocumentDataExtractorsOut,
    DocumentDataExampleCreate,
    DocumentDataExampleUpdate,
    DocumentDataExample,
    DocumentDataExampleOut,
)
from openai.lib._pydantic import to_strict_json_schema
from app.handler import full_prompt_from_text, full_prompt_from_image

router = APIRouter()


@router.get("/", response_model=DocumentDataExtractorsOut)
def read_document_data_extractors(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve DocumentDataExtractors.
    """
    if current_user.is_superuser:
        statement = select(func.count()).select_from(DocumentDataExtractor)
        count = session.exec(statement).one()
        statement = (
            select(DocumentDataExtractor)
            .order_by(DocumentDataExtractor.name)
            .offset(skip)
            .limit(limit)
        )
        document_data_extractors = session.exec(statement).all()
    else:
        statement = (
            select(func.count())
            .select_from(DocumentDataExtractor)
            .where(DocumentDataExtractor.owner_id == current_user.id)
        )
        count = session.exec(statement).one()
        statement = (
            select(DocumentDataExtractor)
            .where(DocumentDataExtractor.owner_id == current_user.id)
            .order_by(DocumentDataExtractor.name)
            .offset(skip)
            .limit(limit)
        )
        document_data_extractors = session.exec(statement).all()

    return DocumentDataExtractorsOut(
        data=sorted(
            document_data_extractors,
            key=lambda dde: dde.timestamp,
            reverse=True,
        ),
        count=count,
    )


@router.get("/{id}", response_model=DocumentDataExtractorOut)
def read_document_data_extractor(
    session: SessionDep, current_user: CurrentUser, id: int
) -> Any:
    """
    Get a DocumentDataExtractor by ID.
    """
    document_data_extractor = session.get(DocumentDataExtractor, id)
    if not document_data_extractor:
        raise HTTPException(
            status_code=404, detail="DocumentDataExtractor not found"
        )
    if not current_user.is_superuser and (
        document_data_extractor.owner_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return document_data_extractor


@router.post(
    "/",
    response_model=DocumentDataExtractorOut,
    operation_id="create_document_data_extractor",
)
def create_document_data_extractor(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    document_data_extractor_in: DocumentDataExtractorCreate,
) -> Any:
    """
    Create a new DocumentDataExtractor.
    """
    try:
        create_pydantic_model(document_data_extractor_in.response_template)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="received incorrect response template",
        )
    document_data_extractor = DocumentDataExtractor.model_validate(
        document_data_extractor_in,
        update={
            "owner_id": current_user.id,
            "response_template": json.dumps(
                document_data_extractor_in.response_template
            ),
        },
    )
    try:
        session.add(document_data_extractor)
        session.commit()
        session.refresh(document_data_extractor)
        return document_data_extractor
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="document data extractor already registered",
        )


@router.put("/{id}", response_model=DocumentDataExtractorOut)
def update_document_data_extractor(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    document_data_extractor_in: DocumentDataExtractorUpdate,
) -> Any:
    """
    Update a DocumentDataExtractor.
    """
    document_data_extractor = session.get(DocumentDataExtractor, id)
    if not document_data_extractor:
        raise HTTPException(
            status_code=404, detail="DocumentDataExtractor not found"
        )
    if not current_user.is_superuser and (
        document_data_extractor.owner_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = document_data_extractor_in.model_dump(exclude_unset=True)
    pdyantic_dict = update_dict.pop("response_template")
    if pdyantic_dict is not None:
        try:
            create_pydantic_model(pdyantic_dict)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="received incorrect response template",
            )
    update_dict["response_template"] = json.dumps(pdyantic_dict)
    document_data_extractor.sqlmodel_update(update_dict)
    session.add(document_data_extractor)
    session.commit()
    session.refresh(document_data_extractor)
    return document_data_extractor


@router.delete("/{id}")
def delete_document_data_extractor(
    session: SessionDep, current_user: CurrentUser, id: int
) -> Message:
    """
    Delete a DocumentDataExtractor.
    """
    document_data_extractor = session.get(DocumentDataExtractor, id)
    if not document_data_extractor:
        raise HTTPException(
            status_code=404, detail="DocumentDataExtractor not found"
        )
    if not current_user.is_superuser and (
        document_data_extractor.owner_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(document_data_extractor)
    session.commit()
    return Message(message="DocumentDataExtractor deleted successfully")


@router.get("/name/{name}", response_model=DocumentDataExtractorOut)
def read_document_data_extractor_by_name(
    *, session: SessionDep, current_user: CurrentUser, name: str
) -> Any:
    """
    Get DocumentDataExtractor by name.
    """
    document_data_extractor = crud.get_document_data_extractor(
        session=session, name=name
    )
    if not document_data_extractor:
        raise HTTPException(
            status_code=404, detail="DocumentDataExtractor not found"
        )
    if not current_user.is_superuser and (
        document_data_extractor.owner_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return document_data_extractor


@router.post(
    "/{name}/example",
    response_model=DocumentDataExampleOut,
    operation_id="create_document_data_example",
)
def create_document_data_example(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    name: str,
    document_data_example_in: DocumentDataExampleCreate,
) -> Any:
    """
    Create new DocumentDataExample.
    """
    if not documents.exists(
        f"{current_user.id}/{document_data_example_in.document_id}/data"
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document not found",
        )
    document_data_extractor = crud.get_document_data_extractor(
        session=session, name=name
    )
    if not document_data_extractor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DocumentDataExtractor not found",
        )
    if not current_user.is_superuser and (
        document_data_extractor.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
        )
    # verify the example matches the template of the document data extractor
    pyd_model = create_pydantic_model(
        json.loads(document_data_extractor.response_template)
    )
    try:
        pyd_model.model_validate(document_data_example_in.data)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Example data does match DocumentDataExtractor Template",
        )
    document_data_example = DocumentDataExample.model_validate(
        document_data_example_in,
        update={
            "document_data_extractor_id": document_data_extractor.id,
            "data": json.dumps(document_data_example_in.data),
        },
    )
    session.add(document_data_example)
    session.commit()
    session.refresh(document_data_example)
    return document_data_example


@router.put(
    "/{name}/example/{id}",
    response_model=DocumentDataExampleOut,
    operation_id="update_document_data_example",
)
def update_document_data_example(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    name: str,
    id: int,
    document_data_example_in: DocumentDataExampleUpdate,
) -> Any:
    """
    Create new DocumentDataExample.
    """
    if document_data_example_in.document_id and not documents.exists(
        f"{current_user.id}/{document_data_example_in.document_id}/data"
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    document_data_extractor = crud.get_document_data_extractor(
        session=session, name=name
    )
    if not document_data_extractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DocumentDataExtractor not found",
        )
    if not current_user.is_superuser and (
        document_data_extractor.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions",
        )
    document_data_example = session.get(DocumentDataExample, id)
    if not document_data_example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DocumentDataExample not found",
        )
    if (
        document_data_example.document_data_extractor_id
        != document_data_extractor.id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DocumentDataExample not found in this DocumentDataExtractor",
        )
    update_dict = document_data_example_in.model_dump(exclude_unset=True)
    data = update_dict.pop("data")
    if data is not None:
        pyd_model = create_pydantic_model(
            json.loads(document_data_extractor.response_template)
        )
        try:
            pyd_model.model_validate(document_data_example_in.data)
        except ValidationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Example data does match DocumentDataExtractor Template",
            )
        else:
            update_dict["data"] = json.dumps(data)
    document_data_example.sqlmodel_update(update_dict)
    session.add(document_data_example)
    session.commit()
    session.refresh(document_data_example)
    return document_data_example


@router.delete("/{name}/example/{id}")
def delete_document_data_example(
    *, session: SessionDep, current_user: CurrentUser, name: str, id: int
) -> Message:
    """
    Delete an event identifier.
    """
    document_data_extractor = crud.get_document_data_extractor(
        session=session, name=name
    )
    if not document_data_extractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DocumentDataExtractor not found",
        )
    if not current_user.is_superuser and (
        document_data_extractor.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions",
        )
    document_data_example = session.get(DocumentDataExample, id)
    if not document_data_example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DocumentDataExample not found",
        )
    if (
        document_data_example.document_data_extractor_id
        != document_data_extractor.id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DocumentDataExample not found in this DocumentDataExtractor",
        )
    session.delete(document_data_example)
    session.commit()
    return Message(message="DocumentDataExample deleted successfully")


@router.post("/extract/{name}")
async def extract_from_file(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    name: str,
    upload: UploadFile,
) -> JSONResponse:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You should be an active user",
        )
    document_data_extractor = crud.get_document_data_extractor(
        session=session, name=name
    )
    if not document_data_extractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DocumentDataExtractor not found",
        )

    if not document_data_extractor.owner_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DocumentDataExtractor has no owner",
        )
        
    allowed_mime_types = [
        "application/pdf",                 # PDF files
        "application/vnd.ms-excel",        # XLS 
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # XLSX (new Excel format)
        "image/png",                       # PNG images
    ]
    #### Pull data from the file
    if upload.content_type not in allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint can only process pdfs",
        )
    
    f = io.BytesIO(upload.file.read())
#TODO pdf_reader.as_text or pdf_reader.as_png ?
    if upload.content_type == "application/pdf" and document_data_extractor.type == "text":
        prompt = pdf_reader.as_text(f)
        validate_extracted_text(prompt) 
    elif upload.content_type == "application/pdf" and document_data_extractor.type == "image":
        prompt = pdf_reader.as_png(f)
    elif upload.content_type == "application/vnd.ms-excel" or upload.content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        prompt = excel_reader.as_csv(f)
        validate_extracted_text(prompt) 
    elif upload.content_type == "image/png":
        prompt = png_reader.as_png(f)
    
    
        
    # Build examples
#TODO add in the document_data_extractor the option to set the type image or text for pdfs
    if (upload.content_type == "application/pdf" and document_data_extractor.type == "text") or upload.content_type == "application/vnd.ms-excel" or upload.content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
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
    elif (upload.content_type == "application/pdf" and document_data_extractor.type == "image") or upload.content_type == "image/png":
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
    
    system_prompt = document_data_extractor.prompt

    if document_data_extractor.type == "text":
        messages = full_prompt_from_text(system_prompt, prompt, examples)
    elif document_data_extractor.type == "image":
        messages = full_prompt_from_image(system_prompt, prompt, examples)

    pydantic_reponse = create_pydantic_model(
        json.loads(document_data_extractor.response_template)
    )
    format_response = {
        "type": "json_schema",
        "json_schema": {
            "schema": to_strict_json_schema(pydantic_reponse),
            "name": "response",
            "strict": True,
        },
    }

    chat_completion_request = ChatCompletionRequest(
        model="gpt-4o-2024-08-06",
        messages=messages,
        max_tokens=2000,
        temperature=0.1,
        logprobs=True,
        top_logprobs=5,
        response_format=format_response,
    ).model_dump(exclude_unset=True)

    chat_completion_response = await ArenaHandler(
        session, document_data_extractor.owner, chat_completion_request
    ).process_request()
    extracted_data = chat_completion_response.choices[0].message.content
    extracted_data_token = chat_completion_response.choices[0].logprobs.content
    # TODO: handle refusal or case in which content was not correctly done
    # TODO: Improve the prompt to ensure the output is always a valid JSON
    #
    json_string = extracted_data[
        extracted_data.find("{") : extracted_data.rfind("}") + 1
    ]
    token_indices=map_characters_to_token_indices(extracted_data_token)
    regex_spans=find_value_spans(extracted_data)
    logprobs_sum=get_token_spans_and_logprobs(token_indices, regex_spans, extracted_data_token)
    return {"extracted_data": json.loads(json_string), "extracted_logprobs":logprobs_sum}

def map_characters_to_token_indices(extracted_data_token: list[TokenLogprob]) -> list[int]:
    """
    Maps each character in the JSON string output to its corresponding token index.
    
    Args:
    extracted_data_token : A list of `TokenLogprob` objects, where each object represents a token and its data (such as the logprobs)

    Returns:
    A list of integers where each position corresponds to a character in the concatenated JSON string,
    and the integer at each position is the index of the token responsible for generating that specific character in the JSON string.
    
    Example:
    --------
    Given `extracted_data_token = [TokenLogprob(token='{'), TokenLogprob(token='"key1"'), TokenLogprob(token=': '), TokenLogprob(token='"value1"'), TokenLogprob(token='}')]`
    the JSON output is : '{"key1": "value1"}' and the function will return the list [0, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4]
    
    """

    json_output = "".join(token_data.token for token_data in extracted_data_token)
                    
    token_indices = [None] * len(json_output)
    current_char_pos = 0

    for token_idx, token_data in enumerate(extracted_data_token):
        token_text = token_data.token
        for char_pos in range(len(token_text)):
            token_indices[current_char_pos] = token_idx
            current_char_pos += 1

    return token_indices

def find_value_spans(json_string: str) -> list[tuple[str, tuple[int, int]]]:
    """
    Extracts spans (start and end positions) of values (both strings or numbers) within a JSON-formatted string.

    Args:
    json_string : A JSON-formatted string where values are paired with keys and separated by colons.
    
    Returns:
    A list of tuples, where each tuple contains the matched value of the key and a tuple with two integers (start, end), representing the character span of the respective value within `json_string`.

    Example:
    --------
    Given `json_string = '{"key1": "value1"}'`, the function will return:
        [("key1", (9, 17))]
    """
 
    pattern = r'"([^"\n}]+)"\s*:\s*("[^"\n]+"|[-0-9.eE]+)\s*'

    matches = []
    for match in re.finditer(pattern, json_string):
        value = match.group(1)
        start = match.start(2)  
        end = match.end(2)      
        matches.append((value, (start, end)))
    return matches


def get_token_spans_and_logprobs(
    token_indices: list[int], 
    value_spans: list[tuple[str, tuple[int, int]]], 
    extracted_data_token: list[TokenLogprob]
) -> dict[str,float]:
    """
    Identifies the token indices for each value span and extracts the log probabilities for these tokens, summing them to provide an overall log probability for each value span. 

    Args:
        token_indices : A list mapping each character in the json string to a token index
        value_spans : A list of tuples, each containing the value of the key and the character sapn within the JSON string
        extracted_data_token : A list of `TokenLogprob` objects, each containing a token and its log probability data, where the index of each item corresponds to its token index.

    Returns:
    A dictionary mapping each key to the summed log probability of all the tokens that cotntains part of its value.


    Example:
    --------
    Given:
      - `token_indices = [0, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4]`, which maps each character to a token index.
      - `value_spans = [("key1", (9, 17))]`.
      - `extracted_data_token = [TokenLogprob(token="{", logprob=-1.5), TokenLogprob(token="key1", logprob=-1), TokenLogprob(token=": ", logprob=-1), TokenLogprob(token="value1", logprob=-1.5), TokenLogprob(token="}", logprob=-0.8)]`
   
    The function will return:
      {"key1": -1.5} 
    """
    logprobs_for_values = {}

    for value, (start, end) in value_spans:
        token_start = token_indices[start]
        token_end = token_indices[end] 
        logprobs = [
            extracted_data_token[token_idx].logprob
            for token_idx in range(token_start, token_end)
        ]
        logprobs_for_values[value] = sum(logprobs)

    return logprobs_for_values


def create_pydantic_model(
    schema: dict[
        str,
        tuple[
            Literal["str", "int", "bool", "float", "dict", "list"],
            Literal["required", "optional"],
        ],
    ],
) -> Any:
    """Creates a pydantic model from an input dictionary where
    keys are names of entities to be retrieved, each value is a tuple specifying
    the type of the entity and whether it is required or optional"""
    # Convert string type names to actual Python types
    field_types = {
        "str": (str, ...),  # ... means the field is required
        "int": (int, ...),
        "float": (float, ...),
        "bool": (bool, ...),
        "dict": (dict[str,float], ...),
        "list": (list[dict[str,Any]], ...)
    }
    optional_field_types = {
        "str": (str | None, ...),  # ... means the field is required
        "int": (int | None, ...),
        "float": (float | None, ...),
        "bool": (bool | None, ...),
        "dict": (dict[str,float], ...),
        "list": (list[dict[str,Any]], ...)
    }

    # Dynamically create a Pydantic model using create_model
    fields = {
        name: field_types[ftype[0]]
        if ftype[1] == "required"
        else optional_field_types[ftype[0]]
        for name, ftype in schema.items()
    }
    dynamic_model = create_model("DataExtractorSchema", **fields)
    return dynamic_model


def validate_extracted_text(text: str):
    if text == "":
        raise HTTPException(
            status_code=500,
            detail="The extracted text from the document is empty. Please check if the document is corrupted.",
        )
