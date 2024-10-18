from unittest.mock import patch
from fastapi.testclient import TestClient
from app.core.config import settings
from app.models import DocumentDataExtractorOut
from app.services.object_store import Documents
import pytest
from typing import Generator, Any
from app.api.routes.dde import find_indices_for_keys, extract_logprobs_from_indices

@pytest.fixture(scope="module")
def document_data_extractor(client: TestClient, superuser_token_headers: dict[str, str]) ->  Generator[dict[str, Any], None, None]:

    fake_name = "Test dde"
    fake_prompt = "Extract the name from document"
    
    payload = {
        "name": fake_name,
        "prompt": fake_prompt
    }
    
    headers = superuser_token_headers

    fake_dde = DocumentDataExtractorOut(
        id=1,
        name=fake_name,
        prompt=fake_prompt,
        timestamp="2024-10-03T09:31:33.748765", 
        owner_id=1, 
        document_data_examples=[]
    )
    response = client.post(
                f"{settings.API_V1_STR}/dde",   
                headers=headers,
                json=payload,  
    )
            
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == fake_dde.id
    assert response_data["name"] == fake_dde.name
    assert response_data["prompt"] == fake_dde.prompt
    assert response_data["owner_id"] == fake_dde.owner_id
    assert len(response_data["document_data_examples"]) == 0
    
    yield response_data
    
    dde_name = response_data["name"]
    id_example = response_data["document_data_examples"][0]['id']
    with patch.object(Documents, 'exists', return_value=True):
        r = client.delete(
            f"{settings.API_V1_STR}/dde/{dde_name}/example/{id_example}",
            headers=superuser_token_headers,
        )
        
        assert r.status_code == 200
        r_data = r.json()
        assert r_data['message'] == 'DocumentDataExample deleted successfully' 
    
    response = client.delete(
        f"{settings.API_V1_STR}/dde/{response_data['id']}",     
        headers=superuser_token_headers,
    )
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['message'] == 'DocumentDataExtractor deleted successfully'
    
     
        
def test_update_document_data_extractor(client: TestClient, superuser_token_headers: dict[str, str], document_data_extractor: dict[str, Any]):

    updated_name = "Updated dde"
    dde_id = document_data_extractor["id"]
    
    document_data_extractor["name"] = updated_name

    update_payload = {
        "name": updated_name,
        "prompt": document_data_extractor["prompt"]
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/dde/{dde_id}",
        headers=superuser_token_headers,
        json=update_payload
    )

    assert response.status_code == 200

    response_data = response.json()
    assert response_data["id"]== dde_id
    assert response_data["name"] == updated_name
    assert response_data["prompt"] == document_data_extractor["prompt"]
    assert response_data["timestamp"] == document_data_extractor["timestamp"]
    assert response_data["owner_id"] == document_data_extractor["owner_id"]
    assert len(response_data["document_data_examples"]) == 0

def test_read_document_data_extractor(document_data_extractor: dict[str, Any]):
    assert document_data_extractor['id']== 1     #id_dde = 1 because only one dde has been created in the fixture
    assert document_data_extractor["name"] == "Updated dde"
    assert document_data_extractor["prompt"] == "Extract the name from document"
    assert document_data_extractor["owner_id"] == 1

    
def test_create_document_data_example(client: TestClient, superuser_token_headers: dict[str, str], document_data_extractor: dict[str, Any]):
    
    name = document_data_extractor["name"]

    with patch.object(Documents, 'exists', return_value=True):
        start_page = 0
        end_page = 2
        info_to_extract = {"name": "Marta"}
        
        data_doc = {
            "document_id": "abc",
            "data": str(info_to_extract),
            "document_data_extractor_id": document_data_extractor["id"],
            "start_page": start_page,   
            "end_page": end_page,     
            "id": 1                   # id = 1 because only one example is created in the test
        }
        
        document_data_extractor["document_data_examples"].append(data_doc)    
        
        response = client.post(
            f"{settings.API_V1_STR}/dde/{name}/example",
            headers=superuser_token_headers,
            json=data_doc
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["document_id"] == data_doc["document_id"]
        assert response_data["data"] == data_doc["data"]
        assert response_data["document_data_extractor_id"] == data_doc["document_data_extractor_id"]
        assert response_data["id"] == 1
        
def test_update_document_data_example(client: TestClient, superuser_token_headers: dict[str, str], document_data_extractor: dict[str, Any]):

    name_dde = document_data_extractor["name"]
    id_example = document_data_extractor["document_data_examples"][0]['id']
    updated_data = "{'name': 'Sarah'}"
 

    update_payload = {
        "document_id" : document_data_extractor["document_data_examples"][0]['document_id'],
        "data" : updated_data,
        "document_data_extractor_id" : document_data_extractor["document_data_examples"][0]['document_data_extractor_id']
    }
    
    document_data_extractor["document_data_examples"][0]['data'] = updated_data
  
    with patch.object(Documents, 'exists', return_value=True):
        response = client.put(
            f"{settings.API_V1_STR}/dde/{name_dde}/example/{id_example}",
            headers=superuser_token_headers,
            json=update_payload
        )
        
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["document_id"] == 'abc'
        assert response_data["data"] == updated_data
        assert response_data["document_data_extractor_id"] == 1
        assert response_data["id"] == 1

class TopLogprob:
    def __init__(self, logprob: float):
        self.logprob = logprob

class Token:
    def __init__(self, token: str, top_logprobs: list[TopLogprob]):
        self.token = token
        self.top_logprobs = top_logprobs 
        
@pytest.fixture()
def token_list() -> list[Token]:
    tokens = ['{', 'na', 'me', '":"', 'Mart', 'a', '","', 'cer', 'ri', '","', 'age', '":', '25', ',"' , 'natio', 'nality', '":"', 'italy', '}']
    token_list = [Token(token, []) for token in tokens]
    return token_list

@pytest.fixture()
def token_logprobs_list() -> list[Token]:
    tokens = ['{', 'na', 'me', '":"', 'Mart', 'a', '","', 'cer', 'ri', '","', 'age', '":', '25', ',"' , 'natio', 'nality', '":"', 'italy', '}']
    logprobs = [-5.42e-05, -10.50, -11.50, -12.50, -13.750]
    logprobs_list = [TopLogprob(logprob) for logprob in logprobs]
    token_list = [Token(token, logprobs_list) for token in tokens]

    return token_list
    
def test_find_indices_for_keys(token_list: list[Token]):
    keys = ['name', 'age', 'nationality']
    expected_result = {
        'name': [4, 8],
        'age': [12, 12],
        'nationality': [17]
    }
    result = find_indices_for_keys(keys, token_list)
    
    assert result == expected_result

def test_extract_logprobs_from_indices(token_logprobs_list: list[Token]):
    expected_value_indices = {
        'name': [4, 8],
        'age': [12, 12],
        'nationality': [17]
    }
    expected_logprobs = [-5.42e-05, -10.50, -11.50, -12.50, -13.750]
    expected_result = {
        'name': [expected_logprobs] * 5,    
        'age': [expected_logprobs],         
        'nationality': [expected_logprobs]  
    }
    result = extract_logprobs_from_indices(expected_value_indices, token_logprobs_list)

    assert result == expected_result
    
#TODO: test extract_from_file
   


    
    