
import pytest

from app.migrations.response_templates import convert_to_json_schema
import json

@pytest.fixture
def old_json_schema():
    return {
    "source": [
      "str",
      "required"
    ],
    "year": [
      "int",
      "required"
    ],
    "resultat d exploitation (I-II)": [
      "int",
      "optional"
    ],
    "resultat d exploitation (I-II) - previous year": [
      "int",
      "optional"
    ],
    "dotations aux amortissements": [
      "int",
      "optional"
    ],
    "dotations aux amortissements - previous year": [
      "int",
      "optional"
    ],
    "title": [
      "str",
      "optional"
    ],
    "revenu net ou deficit": [
      "int",
      "optional"
    ],
    "revenu net ou deficit previous year": [
      "int",
      "optional"
    ]
}
@pytest.fixture
def new_json_schema():
    return {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "source": {
        "title": "Source",
        "type": "string"
        },
        "year": {
        "title": "Year",
        "type": "integer"
        },
        "resultat d exploitation (I-II)": {
        "anyOf": [
            {
            "type": "integer"
            },
            {
            "type": "null"
            }
        ],
        "title": "Resultat D Exploitation (I-Ii)"
        },
        "resultat d exploitation (I-II) - previous year": {
        "anyOf": [
            {
            "type": "integer"
            },
            {
            "type": "null"
            }
        ],
        "title": "Resultat D Exploitation (I-Ii) - Previous Year"
        },
        "dotations aux amortissements": {
        "anyOf": [
            {
            "type": "integer"
            },
            {
            "type": "null"
            }
        ],
        "title": "Dotations Aux Amortissements"
        },
        "dotations aux amortissements - previous year": {
        "anyOf": [
            {
            "type": "integer"
            },
            {
            "type": "null"
            }
        ],
        "title": "Dotations Aux Amortissements - Previous Year"
        },
        "title": {
        "anyOf": [
            {
            "type": "string"
            },
            {
            "type": "null"
            }
        ],
        "title": "Title"
        },
        "revenu net ou deficit": {
        "anyOf": [
            {
            "type": "integer"
            },
            {
            "type": "null"
            }
        ],
        "title": "Revenu Net Ou Deficit"
        },
        "revenu net ou deficit previous year": {
        "anyOf": [
            {
            "type": "integer"
            },
            {
            "type": "null"
            }
        ],
        "title": "Revenu Net Ou Deficit Previous Year"
        }
    },
    "required": [
        "source",
        "year",
        "resultat d exploitation (I-II)",
        "resultat d exploitation (I-II) - previous year",
        "dotations aux amortissements",
        "dotations aux amortissements - previous year",
        "title",
        "revenu net ou deficit",
        "revenu net ou deficit previous year"
    ]
    }
    
    
def test_convert_to_json_schema(old_json_schema, new_json_schema):
    dynamic_model = convert_to_json_schema(json.dumps(old_json_schema))
    
    assert dynamic_model == json.dumps(new_json_schema, indent=2)