from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Response
from sqlmodel import func, select, desc
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import coalesce
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.csv as pc

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.models import Message, Event, EventCreate, EventOut, EventsOut, EventUpdate, EventIdentifier, EventAttribute, EventAttributeCreate

router = APIRouter()


@router.get("/", response_model=EventsOut)
def read_events(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve Events.
    """
    if current_user.is_superuser:
        statement = select(func.count()).select_from(Event)
        count = session.exec(statement).one()
        statement = select(Event).order_by(desc(coalesce(Event.parent_id, Event.id)), Event.id).offset(skip).limit(limit)
        events = session.exec(statement).all()
    else:
        statement = (
            select(func.count())
            .select_from(Event)
            .where(Event.owner_id == current_user.id)
        )
        count = session.exec(statement).one()
        statement = (
            select(Event)
            .where(Event.owner_id == current_user.id)
            .order_by(desc(coalesce(Event.parent_id, Event.id)), Event.id)
            .offset(skip)
            .limit(limit)
        )
        events = session.exec(statement).all()

    return EventsOut(data=events, count=count)


@router.get("/{id}", response_model=EventOut)
def read_event(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get event by ID.
    """
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not current_user.is_superuser and (event.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return event


@router.post("/", response_model=EventOut, operation_id="create_event")
def create_event(
    *, session: SessionDep, current_user: CurrentUser, event_in: EventCreate
) -> Any:
    """
    Create new event.
    """
    event = Event.model_validate(event_in, update={"owner_id": current_user.id})
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.put("/{id}", response_model=EventOut)
def update_event(
    *, session: SessionDep, current_user: CurrentUser, id: int, event_in: EventUpdate
) -> Any:
    """
    Update an event.
    """
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not current_user.is_superuser and (event.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = event_in.model_dump(exclude_unset=True)
    event.sqlmodel_update(update_dict)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.delete("/{id}")
def delete_event(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete an event.
    """
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not current_user.is_superuser and (event.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(event)
    session.commit()
    return Message(message="Event deleted successfully")


@router.get("/identifier/{identifier}", response_model=EventOut)
def read_event_by_identifier(
    *, session: SessionDep, current_user: CurrentUser, identifier: str
) -> Any:
    """
    Get event by identifier.
    """
    statement = select(Event).join(EventIdentifier).where(EventIdentifier.id == identifier)
    event = session.exec(statement).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not current_user.is_superuser and (event.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return event


@router.get("/{id}/identifier/{identifier}", response_model=EventIdentifier)
def create_event_identifier_get(
    *, session: SessionDep, current_user: CurrentUser, id: int, identifier: str
) -> Any:
    """
    Create new event identifier.
    """
    return crud.create_event_identifier(session=session, event_identifier=identifier, event_id=id)


@router.post("/identifier", response_model=EventIdentifier, operation_id="create_event_identifier")
def create_event_identifier(
    *, session: SessionDep, current_user: CurrentUser, event_identifier: EventIdentifier
) -> Any:
    """
    Create new event identifier.
    """
    return crud.create_event_identifier(session=session, event_identifier=event_identifier.id, event_id=event_identifier.event_id)


@router.delete("/identifier/{identifier}")
def delete_event_identifier(session: SessionDep, current_user: CurrentUser, identifier: str) -> Message:
    """
    Delete an event identifier.
    """
    event_identifier = session.get(EventIdentifier, identifier)
    if not event_identifier:
        raise HTTPException(status_code=404, detail="Event identifier not found")
    if not current_user.is_superuser and (event_identifier.event.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(event_identifier)
    session.commit()
    return Message(message="Event identifier deleted successfully")


@router.get("/{id}/attribute/{name}", response_model=EventAttribute, operation_id="event_attribute")
def create_event_attribute_get(
    *, session: SessionDep, current_user: CurrentUser, id: int, name: str
) -> Any:
    """
    Create new event attribute.
    """
    return crud.create_event_attribute_from_name_value(session=session, attribute=name, event_id=id)


@router.get("/{id}/attribute/{name}/{value}", response_model=EventAttribute, operation_id="event_attribute_value")
def create_event_attribute_get_with_value(
    *, session: SessionDep, current_user: CurrentUser, id: int, name: str, value: str
) -> Any:
    """
    Create new event attribute.
    """
    return crud.create_event_attribute_from_name_value(session=session, attribute=name, value=value, event_id=id)


@router.post("/attribute", response_model=EventAttribute, operation_id="create_event_attribute")
def create_event_attribute(
    *, session: SessionDep, current_user: CurrentUser, event_attribute: EventAttributeCreate
) -> Any:
    """
    Create new event attribute.
    """
    return crud.create_event_attribute(session=session, event_attribute_in=event_attribute)


@router.delete("/{id}/attribute/{name}")
def delete_event_attribute(session: SessionDep, current_user: CurrentUser, id: int, name: str) -> Message:
    """
    Delete an event attribute.
    """
    event_attribute = crud.get_event_attribute(session=session, attribute=name, event_id=id)
    if not event_attribute:
        raise HTTPException(status_code=404, detail="Event attribute not found")
    if not current_user.is_superuser and (event_attribute.event.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(event_attribute)
    session.commit()
    return Message(message="Event attribute deleted successfully")


@router.get("/download/{format}")
def download_events(
    session: SessionDep, current_user: CurrentUser, format: Literal["arrow", "csv", "json"], skip: int = 0, limit: int = 1000000
) -> Any:
    """
    Retrieve Events.
    """
    if current_user.is_superuser:
        request = select(Event).where(Event.name == "request").offset(skip).limit(limit).cte()
    else:
        request = select(Event).where(Event.name == "request").where(Event.owner_id == current_user.id).offset(skip).limit(limit).cte()
    modified_request = select(Event).where(Event.name == "modified_request").cte()
    response = select(Event).where(Event.name == "response").cte()
    user_evaluation = select(Event).where(Event.name == "user_evaluation").cte()
    lm_judge_evaluation = select(Event).where(Event.name == "lm_judge_evaluation").cte()
    lm_config = select(Event).where(Event.name == "lm_config").cte()
    statement = (
        select(
            request.c.id,
            request.c.timestamp,
            request.c.owner_id,
            request.c.content.label("request"),
            modified_request.c.content.label("modified_request"),
            response.c.content.label("response"),
            user_evaluation.c.content.label("user_evaluation"),
            lm_judge_evaluation.c.content.label("lm_judge_evaluation"),
            lm_config.c.content.label("lm_config"),
            )
        .outerjoin(modified_request, request.c.id == modified_request.c.parent_id)
        .outerjoin(response, request.c.id == response.c.parent_id)
        .outerjoin(user_evaluation, request.c.id == user_evaluation.c.parent_id)
        .outerjoin(lm_judge_evaluation, request.c.id == lm_judge_evaluation.c.parent_id)
        .outerjoin(lm_config, request.c.id == lm_config.c.parent_id)
    )
    # Execute the query
    result = session.exec(statement)
    events = result.all()
    # Arrange them in a Table
    table = pa.Table.from_pylist([dict(zip(result.keys(), event)) for event in events])
    # Write table to a parquet format in memory
    buf = pa.BufferOutputStream()
    match format:
        case "arrow":
            pq.write_table(table, buf)
        case "csv":
            pc.write_csv(table, buf)
        case "json":
            pc.write_csv(table, buf)
    # Get the buffer value
    buf = buf.getvalue().to_pybytes()
    # Return a file as the response
    return Response(content=buf, media_type='application/octet-stream')
