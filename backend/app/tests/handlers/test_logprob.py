from typing import Any
import json
import pytest
from app.handlers.logprobs import extract_json_data, map_characters_to_token_indices

class TokenLogprob:
    def __init__(self, token: str, logprob: float):
        self.token = token
        self.logprob = logprob
        
@pytest.fixture
def data_token():
    return [
        TokenLogprob(token='{',  logprob = -1.9365e-07),          # Token index 0
        TokenLogprob(token='"a"',  logprob =  -0.01117),       # Token index 1
        TokenLogprob(token=': "',  logprob = -0.00279),            # Token index 2
        TokenLogprob(token='he', logprob = -1.1472e-06),        # Token index 3
        TokenLogprob(token='llo"', logprob = -0.00851),           # Token index 4
        TokenLogprob(token=', "', logprob = -0.00851),            # Token index 5
        TokenLogprob(token='b', logprob = -0.00851),           # Token index 6
        TokenLogprob(token='": ', logprob = -0.00851),            # Token index 7
        TokenLogprob(token='12', logprob = -0.00851),             # Token index 8
        TokenLogprob(token=', "', logprob = -1.265e-07),            # Token index 9
        TokenLogprob(token='c"', logprob = -0.00851),            # Token index 10
        TokenLogprob(token=': [{"', logprob = -0.00851),             # Token index 11
        TokenLogprob(token='d', logprob = -1.265e-07),            # Token index 12
        TokenLogprob(token='":', logprob = -0.00851),            # Token index 13
        TokenLogprob(token='42', logprob = -0.00851),             # Token index 14
        TokenLogprob(token='}, ', logprob = -1.265e-07),         # Token index 15
        TokenLogprob(token='11', logprob = -0.00851),             # Token index 16
        TokenLogprob(token=']}', logprob = -1.265e-07)           # Token index 17
    ]
simple_json = {"a": "hello", "b": 12, "c": [{"d":42}, 11]}

@pytest.fixture
def token_indices():
    return [0,             
            1, 1, 1, 
            2, 2, 2,           
            3, 3,  
            4, 4, 4, 4, 
            5, 5, 5,
            6, 
            7, 7, 7,
            8, 8,
            9, 9, 9,
            10, 10,
            11, 11, 11, 11, 11,
            12,
            13, 13,
            14, 14,
            15, 15, 15,
            16, 16,
            17, 17
            ] 
    
def test_map_characters_to_token_indices(data_token, token_indices):             
    result = map_characters_to_token_indices(data_token)

    assert result == token_indices
    assert result.count(1) == len(data_token[1].token)

@pytest.fixture
def simple_json_string():
    return json.dumps({"a":"hello", "b": 12, "c": [{"d":42}, 11]})

@pytest.fixture
def json_data():
    return json.dumps({"a": "hello", "a_logprob": -0.0113011472, "a_probability": 98.8762470886041, "b": 12.0, "b_logprob": -0.00851, "b_probability": 99.15261075523148, "c": [{"d": 42.0, "d_logprob": -0.00851, "d_probability": 99.15261075523148}, 11.0]})

def test_extract_json_data(simple_json_string, data_token, token_indices, json_data):
    extracted_json_data = extract_json_data(simple_json_string, data_token, token_indices)
    assert extracted_json_data == json.loads(json_data)