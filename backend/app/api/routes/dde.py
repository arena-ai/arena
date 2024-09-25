from typing import Any, Literal

from fastapi import APIRouter, HTTPException, status, UploadFile
from fastapi.responses import JSONResponse
from sqlmodel import func, select
from sqlalchemy.exc import IntegrityError
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.csv as pc

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

@router.post("/extract/{name}", response_model=ChatCompletionResponse)
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
    prompt = pdf_reader.as_text(upload.file.read())
    system_prompt = document_data_extractor.prompt
    examples_text = ""
    for example in await examples.evaluate():
        input_text = example[0]  
        output_text = example[1]  
        examples_text += f"####\nINPUT: {input_text}\n\nOUTPUT: {output_text}\n\n"
    full_system_content = f"{system_prompt}\n\nHere are some examples of inputs and outputs:\n{examples_text}"
    messages = [
            ChatCompletionMessage(role="system", content=full_system_content),  
            ChatCompletionMessage(role="user", content=f"Here is the next input:\n####\nINPUT:{prompt}")  
        ]
    chat_completion_request = ChatCompletionRequest(   
            model='gpt-4o',
            messages=messages,
            max_tokens=2000,
            temperature=0.1,
            logprobs=True,
            top_logprobs= 5
        ).model_dump(exclude_unset=True)
    print(chat_completion_request)
    chat_completion_response = await ArenaHandler(session, current_user, chat_completion_request).process_request()
    print(chat_completion_response)
    return chat_completion_response

