import logging
import json
from typing import Any, Literal
from pydantic import create_model
from sqlmodel import Session, select
from app.core.db import engine
from sqlalchemy import Engine
from app.models import DocumentDataExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_old_pydantic_model(
    schema: dict[
        str,
        tuple[
            Literal["str", "int", "bool", "float"],
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
    }
    optional_field_types = {
        "str": (str | None, ...),  # ... means the field is required
        "int": (int | None, ...),
        "float": (float | None, ...),
        "bool": (bool | None, ...),
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


def convert_to_json_schema(resp_template_old:str) -> str:
    # Get the JSON schema out of the pydantic model schema
    dynamic_model = get_old_pydantic_model(json.loads(resp_template_old))
    dynamic_model_properties = dynamic_model.schema()
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": dynamic_model_properties['type'], 
        "properties": dynamic_model_properties['properties'],
        "required": dynamic_model_properties['required']
    }
    return json.dumps(json_schema)

def fix_response_template(session:Session, dde:DocumentDataExtractor):
    #get the old schema
    resp_template=dde.response_template
    try:
        get_old_pydantic_model(json.loads(resp_template))
    except Exception as e:
        logger.info(f"skipping dde {dde.name}")
        pass
    else:
        new_resp_template=convert_to_json_schema(resp_template) 
        #update the dde with the new schema 
        dde.sqlmodel_update({"response_template":new_resp_template})
        session.add(dde)
        session.commit()
        session.refresh(dde) 
    
def fix_process_as(session:Session, dde:DocumentDataExtractor):
    if dde.process_as not in ['text', 'image']:
        dde.sqlmodel_update({"process_as":'text'})
        session.add(dde)
        session.commit()
        session.refresh(dde) 
    
def migrate_dde(db_engine: Engine) -> None:
    """
    Migrates response templates stored in the database by converting them to a JSON Schema.
    """
    try:
        with Session(db_engine) as session:   
            statement = (
                    select(DocumentDataExtractor)
                    .order_by(DocumentDataExtractor.name)
                )
            document_data_extractors = session.exec(statement).all()  # get all the objects from the db 
            for dde in document_data_extractors:
                fix_response_template(session, dde)
                fix_process_as(session, dde)
                        
    except Exception as e:
            logger.error(e)
            raise e

if __name__ == "__main__":
    migrate_dde(engine)
    
    