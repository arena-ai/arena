from pathlib import Path
from tempfile import TemporaryDirectory
from datamodel_code_generator import InputFileType, generate
from datamodel_code_generator import DataModelType

from typing import Any
import json
import importlib.util
import sys
from pydantic import BaseModel

def create_pydantic_model(response_template: dict[str, Any]) -> dict[str, Any]:
  # Convert the input dictionary to JSON format to match the input requirements for the model generator.
  json_schema = json.dumps(response_template)
  #temporary directory to store intermediate files required for model generation
  with TemporaryDirectory() as temporary_directory_name:
    temporary_directory = Path(temporary_directory_name)
    output = Path(temporary_directory / 'model.py')
      
    generate(
          input_=json_schema,
          input_file_type=InputFileType.JsonSchema,   # Specify that the input is a JSON schema.             
          output=output,
          output_model_type=DataModelType.PydanticV2BaseModel,   #use Pydantic v2
    )

      # import dynamically the Python module generated 
    model_code = output.read_text()
    print("model_code", model_code)
    module_name = "dynamic_pydantic_model"
    spec = importlib.util.spec_from_file_location(module_name, output)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
      # Collect all generated BaseModel classes
    generated_models = [
        cls for _, cls in vars(module).items() 
        if isinstance(cls, type) and issubclass(cls, BaseModel) and cls != BaseModel
    ]
      # Combine JSON schemas for all models
      # map the name of the class with its json schema
    all_schemas = {model.__name__: model.model_json_schema() for model in generated_models}


    return all_schemas

