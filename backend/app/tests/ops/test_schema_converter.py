import pytest
from app.ops.schema_converter import create_pydantic_model
from app.migrations.response_templates import convert_to_json_schema
import json

@pytest.fixture
def sample_json_schema():
   return {
    "$schema": "https://json-schema.org/draft-07/schema",
    "type": "object",
    "properties": {
        "blocks": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
            "name": {
                "type": ["string", "null"]
            },
            "ownership": { "type": "number" },
            "estate": {
                "type": "array",
                "items": {
                "type": "object",
                "properties": {
                    "adresse": {
                    "type": ["string", "null"]
                    },
                    "Valeur du bien": {
                    "type": ["number", "null"]
                    },
                    "loyers annuels": {
                    "type": ["number", "null"]
                    },
                    "Échéances annuelles": {
                    "type": ["number", "null"]
                    },
                    "Capital restant du": {
                    "type": ["number", "null"]
                    }
                },
                "required": []
                }
            }
            },
            "required": ["ownership", "estate"]
        }
        }
    },
    "required": ["blocks"]
    }

@pytest.fixture
def model_class():
    return {
        "$defs": {
            "Block": {
                "properties": {
                    "name": {
                        "anyOf": [
                            {"type": "string"},
                            {"type": "null"}
                        ],
                        "default": None,
                        "title": "Name"
                    },
                    "ownership": {
                        "title": "Ownership",
                        "type": "number"
                    },
                    "estate": {
                        "items": {
                            "$ref": "#/$defs/EstateItem"
                        },
                        "title": "Estate",
                        "type": "array"
                    }
                },
                "required": ["ownership", "estate"],
                "title": "Block",
                "type": "object"
            },
            "EstateItem": {
                "properties": {
                    "adresse": {
                        "anyOf": [
                            {"type": "string"},
                            {"type": "null"}
                        ],
                        "default": None,
                        "title": "Adresse"
                    },
                    "Valeur du bien": {
                        "anyOf": [
                            {"type": "number"},
                            {"type": "null"}
                        ],
                        "default": None,
                        "title": "Valeur Du Bien"
                    },
                    "loyers annuels": {
                        "anyOf": [
                            {"type": "number"},
                            {"type": "null"}
                        ],
                        "default": None,
                        "title": "Loyers Annuels"
                    },
                    "Échéances annuelles": {
                        "anyOf": [
                            {"type": "number"},
                            {"type": "null"}
                        ],
                        "default": None,
                        "title": "Échéances Annuelles"
                    },
                    "Capital restant du": {
                        "anyOf": [
                            {"type": "number"},
                            {"type": "null"}
                        ],
                        "default": None,
                        "title": "Capital Restant Du"
                    }
                },
                "title": "EstateItem",
                "type": "object"
            }
        },
        "properties": {
            "blocks": {
                "items": {
                    "$ref": "#/$defs/Block"
                },
                "title": "Blocks",
                "type": "array"
            }
        },
        "required": ["blocks"],
        "title": "MainModel",
        "type": "object"
    }
    
def test_create_pydantic_model(sample_json_schema, model_class):             
    result = create_pydantic_model(json.dumps(sample_json_schema))

    assert result.schema()==model_class



    