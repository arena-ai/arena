from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Response, status
from sqlmodel import func, select
from sqlalchemy.exc import IntegrityError
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.csv as pc

from app.api.deps import CurrentUser, SessionDep
from app import crud
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
    document_data_extractor = session.get(DocumentDataExtractorOut, id)
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
    finally:
        session.close()


@router.put("/{id}", response_model=DocumentDataExtractorOut)
def update_document_data_extractor(
    *, session: SessionDep, current_user: CurrentUser, id: int, document_data_extractor_in: DocumentDataExtractorUpdate
) -> Any:
    """
    Update a DocumentDataExtractor.
    """
    document_data_extractor = session.get(DocumentDataExtractorUpdate, id)
    if not document_data_extractor:
        raise HTTPException(status_code=404, detail="DocumentDataExtractor not found")
    if not current_user.is_superuser and (document_data_extractor.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = document_data_extractor_in.model_dump(exclude_unset=True)
    document_data_extractor.sqlmodel_update(update_dict)
    try:
        session.add(document_data_extractor)
        session.commit()
        session.refresh(document_data_extractor)
        return document_data_extractor
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="document data extractor already registered")
    finally:
        session.close()


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
    document_data_extractor = crud.get_document_data_extractor(session, name)
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
    document_data_extractor = crud.get_document_data_extractor(session, name)
    if not document_data_extractor:
        raise HTTPException(status_code=404, detail="DocumentDataExtractor not found")
    if not current_user.is_superuser and (document_data_extractor.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    document_data_example = DocumentDataExample.model_validate(document_data_example_in, update={"document_data_extractor_id": document_data_extractor.id})
    session.add(document_data_example)
    session.commit()
    session.refresh(document_data_example)
    return document_data_example


@router.delete("/{name}/example/{id}")
def delete_document_data_example(session: SessionDep, current_user: CurrentUser, name: str, id: int) -> Message:
    """
    Delete an event identifier.
    """
    document_data_extractor = crud.get_document_data_extractor(session, name)
    if not document_data_extractor:
        raise HTTPException(status_code=404, detail="DocumentDataExtractor not found")
    if not current_user.is_superuser and (document_data_extractor.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    document_data_example = session.get(DocumentDataExample, id)
    if not document_data_example:
        raise HTTPException(status_code=404, detail="Event not found")
    if document_data_example.document_data_extractor_id != document_data_extractor.id:
        raise HTTPException(status_code=400, detail="This DocumentDataExample does nort exist for this DocumentDataExtractor")
    session.delete(document_data_example)
    session.commit()
    return Message(message="DocumentDataExample deleted successfully")
