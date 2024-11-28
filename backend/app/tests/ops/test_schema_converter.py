import pytest
from app.ops.schema_converter import create_pydantic_model

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
def estate_item_class():
    return {
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
    }

@pytest.fixture
def block_class():
    return {
        "$defs": {
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
        "title": "Model",
        "type": "object"
    }
    
def test_schema_converter(sample_json_schema, estate_item_class, block_class, model_class):             
    result = create_pydantic_model(sample_json_schema)

    assert len(result) == 3
    assert result["EstateItem"]["properties"] == estate_item_class
    assert result["Block"] == block_class
    assert result["Model"] == model_class
    