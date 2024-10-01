from typing import Any, Iterable
from app.lm.models.chat_completion import TokenLogprob
from app.lm.models import ChatCompletionResponse
from fastapi import APIRouter, HTTPException, status, UploadFile
from fastapi.responses import JSONResponse
from sqlmodel import func, select
from sqlalchemy.exc import IntegrityError
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.csv as pc
import json
import math
import io

from app.api.deps import CurrentUser, SessionDep
from app.services import crud
from app.lm.models import ChatCompletionResponse, ChatCompletionRequest, Message as ChatCompletionMessage
from app.services.object_store import documents
from app.services.pdf_reader import pdf_reader
from app.lm.handlers import ArenaHandler
from app.ops import tup
from app.ops.documents import as_text
from app.models import (Message, DocumentDataExtractorCreate, DocumentDataExtractorUpdate, DocumentDataExtractor, DocumentDataExtractorOut, DocumentDataExtractorsOut,
                        DocumentDataExampleCreate, DocumentDataExampleUpdate, DocumentDataExample, DocumentDataExampleOut)

router = APIRouter()


@router.get("/", response_model=DocumentDataExtractorsOut)
def read_document_data_extractors(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve DocumentDataExtractors.
    """
    if current_user.is_superuser:
        statement = select(func.count()).select_from(DocumentDataExtractor)
        count = session.exec(statement).one()
        statement = select(DocumentDataExtractor).order_by(DocumentDataExtractor.name).offset(skip).limit(limit)
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

    return DocumentDataExtractorsOut(data=document_data_extractors, count=count)


@router.get("/{id}", response_model=DocumentDataExtractorOut)
def read_document_data_extractor(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get a DocumentDataExtractor by ID.
    """
    document_data_extractor = session.get(DocumentDataExtractor, id)
    if not document_data_extractor:
        raise HTTPException(status_code=404, detail="DocumentDataExtractor not found")
    if not current_user.is_superuser and (document_data_extractor.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return document_data_extractor


@router.post("/", response_model=DocumentDataExtractorOut, operation_id="create_document_data_extractor")
def create_document_data_extractor(
    *, session: SessionDep, current_user: CurrentUser, document_data_extractor_in: DocumentDataExtractorCreate
) -> Any:
    """
    Create a new DocumentDataExtractor.
    """
    document_data_extractor = DocumentDataExtractor.model_validate(document_data_extractor_in, update={"owner_id": current_user.id})
    try:
        session.add(document_data_extractor)
        session.commit()
        session.refresh(document_data_extractor)
        return document_data_extractor
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="document data extractor already registered")


@router.put("/{id}", response_model=DocumentDataExtractorOut)
def update_document_data_extractor(
    *, session: SessionDep, current_user: CurrentUser, id: int, document_data_extractor_in: DocumentDataExtractorUpdate
) -> Any:
    """
    Update a DocumentDataExtractor.
    """
    document_data_extractor = session.get(DocumentDataExtractor, id)
    if not document_data_extractor:
        raise HTTPException(status_code=404, detail="DocumentDataExtractor not found")
    if not current_user.is_superuser and (document_data_extractor.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = document_data_extractor_in.model_dump(exclude_unset=True)
    document_data_extractor.sqlmodel_update(update_dict)
    session.add(document_data_extractor)
    session.commit()
    session.refresh(document_data_extractor)
    return document_data_extractor


@router.delete("/{id}")
def delete_document_data_extractor(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a DocumentDataExtractor.
    """
    document_data_extractor = session.get(DocumentDataExtractor, id)
    if not document_data_extractor:
        raise HTTPException(status_code=404, detail="DocumentDataExtractor not found")
    if not current_user.is_superuser and (document_data_extractor.owner_id != current_user.id):
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
    document_data_extractor = crud.get_document_data_extractor(session=session, name=name)
    if not document_data_extractor:
        raise HTTPException(status_code=404, detail="DocumentDataExtractor not found")
    if not current_user.is_superuser and (document_data_extractor.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return document_data_extractor


@router.post("/{name}/example", response_model=DocumentDataExampleOut, operation_id="create_document_data_example")
def create_document_data_example(
    *, session: SessionDep, current_user: CurrentUser, name: str, document_data_example_in: DocumentDataExampleCreate
) -> Any:
    """
    Create new DocumentDataExample.
    """
    if not documents.exists(f"{current_user.id}/{document_data_example_in.document_id}/data"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document not found")
    document_data_extractor = crud.get_document_data_extractor(session=session, name=name)
    if not document_data_extractor:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DocumentDataExtractor not found")
    if not current_user.is_superuser and (document_data_extractor.owner_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough permissions")
    document_data_example = DocumentDataExample.model_validate(document_data_example_in, update={"document_data_extractor_id": document_data_extractor.id})
    session.add(document_data_example)
    session.commit()
    session.refresh(document_data_example)
    return document_data_example


@router.put("/{name}/example/{id}", response_model=DocumentDataExampleOut, operation_id="update_document_data_example")
def update_document_data_example(
    *, session: SessionDep, current_user: CurrentUser, name: str, id: int, document_data_example_in: DocumentDataExampleUpdate
) -> Any:
    """
    Create new DocumentDataExample.
    """
    if document_data_example_in.document_id and not documents.exists(f"{current_user.id}/{document_data_example_in.document_id}/data"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    document_data_extractor = crud.get_document_data_extractor(session=session, name=name)
    if not document_data_extractor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DocumentDataExtractor not found")
    if not current_user.is_superuser and (document_data_extractor.owner_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough permissions")
    document_data_example = session.get(DocumentDataExample, id)
    if not document_data_example:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DocumentDataExample not found")
    if document_data_example.document_data_extractor_id != document_data_extractor.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DocumentDataExample not found in this DocumentDataExtractor")
    update_dict = document_data_example_in.model_dump(exclude_unset=True)
    document_data_example.sqlmodel_update(update_dict)
    session.add(document_data_example)
    session.commit()
    session.refresh(document_data_example)
    return document_data_example


@router.delete("/{name}/example/{id}")
def delete_document_data_example(*, session: SessionDep, current_user: CurrentUser, name: str, id: int) -> Message:
    """
    Delete an event identifier.
    """
    document_data_extractor = crud.get_document_data_extractor(session=session, name=name)
    if not document_data_extractor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DocumentDataExtractor not found")
    if not current_user.is_superuser and (document_data_extractor.owner_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough permissions")
    document_data_example = session.get(DocumentDataExample, id)
    if not document_data_example:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DocumentDataExample not found")
    if document_data_example.document_data_extractor_id != document_data_extractor.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DocumentDataExample not found in this DocumentDataExtractor")
    session.delete(document_data_example)
    session.commit()
    return Message(message="DocumentDataExample deleted successfully")

@router.post("/extract/{name}")
async def extract_from_file(*, session: SessionDep, current_user: CurrentUser, name: str, upload: UploadFile) -> JSONResponse:
    document_data_extractor = crud.get_document_data_extractor(session=session, name=name)
    if not document_data_extractor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DocumentDataExtractor not found")
    if not document_data_extractor.owner_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DocumentDataExtractor has no owner")
    # Build examples
    examples = tup(*(tup(as_text(document_data_extractor.owner, example.document_id, example.start_page, example.end_page), example.data) for example in document_data_extractor.document_data_examples))
    # Pull data from the file
    if upload.content_type != 'application/pdf':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This endpoint can only process pdfs")
    
    f=io.BytesIO(upload.file.read())
    prompt = pdf_reader.as_text(f)
    validate_extracted_text(prompt)
    system_prompt = document_data_extractor.prompt
    
    examples_text = ""
    for input_text, output_text in await examples.evaluate():
        validate_extracted_text(input_text)
        examples_text += f"####\nINPUT: {input_text}\n\nOUTPUT: {output_text}\n\n"
    full_system_content = f"{system_prompt}\n{examples_text}"

    messages = [
            ChatCompletionMessage(role="system", content=full_system_content),  
            ChatCompletionMessage(role="user", content=f"Maintenant, faites la même extraction sur un nouveau document d'input:\n####\nINPUT:{prompt}")  
        ]
    chat_completion_request = ChatCompletionRequest(   
            model='gpt-4o-2024-08-06',
            messages=messages,
            max_tokens=2000,
            temperature=0.1,
            logprobs=True,
            top_logprobs= 5,
            
        ).model_dump(exclude_unset=True)
    
    chat_completion_response = await ArenaHandler(session, current_user, chat_completion_request).process_request()
    extracted_info=chat_completion_response.choices[0].message.content
    # TODO: Improve the prompt to ensure the output is always a valid JSON
    json_string = extracted_info[extracted_info.find('{'):extracted_info.rfind('}')+1]
    extracted_data = {k: v for k, v in json.loads(json_string).items() if k not in ('source', 'year')}   
    logprob_data = extract_logprobs_from_response(chat_completion_response, extracted_data)
    return {'extracted_info': json.loads(json_string), 'logprob_data': logprob_data}

def validate_extracted_text(text: str):
    if text == "":
        raise HTTPException(status_code=500, detail="The extracted text from the document is empty. Please check if the document is corrupted.")
    
    
# TODO: Optimize the entire process of extracting and handling log probabilities from OpenAI for the identified tokens.
def is_equal_ignore_sign(a, b) -> bool:  
    try:
        a = float(a)
        b = float(b)
    except ValueError:
        return False
    return abs(a) == abs(b)      # necessary because logits are associated only with numerical tokens, so here values are considered in their absolute form, ignoring the sign.

def combined_token_in_extracted_data(combined_token: str, extracted_data: Iterable) -> bool: 
    try:
        combined_token = float(combined_token)
    except ValueError:
        return False
    return any(is_equal_ignore_sign(combined_token, value)  
                for value in extracted_data if isinstance(value, (int, float)))

def find_key_by_value(combined_token: str, extracted_data: dict[str, Any]) -> str | None: 
    try:
        combined_token = float(combined_token)
    except ValueError:
        return None
    return next((k for k, v in extracted_data.items() 
                    if isinstance(v, (int, float)) and is_equal_ignore_sign(combined_token, v)), None)    

def extract_logprobs_from_response(response: ChatCompletionResponse, extracted_data: dict[str, Any]) -> dict[str, float | list[float]]:
    logprob_data = {}
    tokens_info = response.choices[0].logprobs.content

    def process_numeric_values(extracted_data: dict[str, Any], path=''):

        for i in range(len(tokens_info)-1):    
            token = tokens_info[i].token
            
            if token.isdigit():          # Only process tokens that are numeric
                combined_token, combined_logprob = combine_tokens(tokens_info, i)
                if combined_token_in_extracted_data(combined_token, extracted_data.values()):     #Checks if a combined token matches any numeric values in the extracted data.

                    key = find_key_by_value(combined_token, extracted_data)                  #Finds the key in 'extracted_data' corresponding to a numeric value that matches the combined token.
                    if key:
                        full_key = path + key  
                        logprob_data[full_key + '_prob_first_token'] = math.exp(tokens_info[i].logprob)
                        logprob_data[full_key + '_prob_second_token'] = math.exp(tokens_info[i+1].logprob)

                        toplogprobs_firsttoken = tokens_info[i].top_logprobs
                        toplogprobs_secondtoken = tokens_info[i+1].top_logprobs

                        logprobs_first = [top_logprob.logprob for top_logprob in toplogprobs_firsttoken]
                        logprobs_second = [top_logprob.logprob for top_logprob in toplogprobs_secondtoken]

                        logprob_data[full_key + '_first_token_toplogprobs'] = logprobs_first
                        logprob_data[full_key + '_second_token_toplogprobs'] = logprobs_second

    def traverse_and_extract(data : dict , path=''):
        for key, value in data.items():
            if isinstance(value, dict):
                print ("value for traverse_and_extract",value )
                traverse_and_extract(value, path + key + '.')
            elif isinstance(value, (int, float)):
                print("data for process_numeric_values",data)
                process_numeric_values(data, path)
    traverse_and_extract(extracted_data)
    return logprob_data


def combine_tokens(tokens_info: list[TokenLogprob], start_index: int) -> tuple[str, float]: 
    combined_token = tokens_info[start_index].token
    combined_logprob = tokens_info[start_index].logprob

    # Keep combining tokens as long as the next token is a digit
    for i in range(start_index + 1, len(tokens_info)):
        if not tokens_info[i].token.isdigit():
            break
        combined_token += tokens_info[i].token
        combined_logprob += tokens_info[i].logprob
    
    return combined_token, combined_logprob

