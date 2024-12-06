from datamodel_code_generator.model import DataModelSet, pydantic_v2
from datamodel_code_generator.parser.jsonschema import JsonSchemaParser
from pydantic import BaseModel, Field
import json
from typing import List

def create_pydantic_model(json_schema: str) -> BaseModel:
      data_model_types=DataModelSet(
                  data_model=pydantic_v2.BaseModel,
                  root_model=pydantic_v2.RootModel,
                  field_model=pydantic_v2.DataModelField,
                  data_type_manager=pydantic_v2.DataTypeManager,
                  dump_resolve_reference_action=pydantic_v2.dump_resolve_reference_action,
            )
      parser = JsonSchemaParser(
      json_schema,
      data_model_type=data_model_types.data_model,
      data_model_root_type=data_model_types.root_model,
      data_model_field_type=data_model_types.field_model,
      data_type_manager_type=data_model_types.data_type_manager,
      dump_resolve_reference_action=data_model_types.dump_resolve_reference_action,
      class_name= "MainModel",              #name of the class to be generated
      use_standard_collections=True,        #ensures that the parser uses standard Python collections
      use_union_operator=True)              #allows the use of the modern `|` operator for type unions 
      
      result = parser.parse()               #create a string out of the code
      exec (result)                         #write all the functions that are in the string in the context dictionary
      model=locals()['MainModel']
      model.model_rebuild()                 #necessary because annotations are defined at runtime
      return model

      
