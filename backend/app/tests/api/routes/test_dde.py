from unittest.mock import patch
from fastapi.testclient import TestClient
from app.core.config import settings
from app.models import DocumentDataExtractorOut
from app.services.object_store import Documents
import pytest
import json
from typing import Generator, Any

@pytest.fixture(scope="module")
def document_data_extractor(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> Generator[dict[str, Any], None, None]:
    fake_name = "Test_dde"
    fake_prompt = "Extract the adresse from document"
    response_template = {"adresse": ["str", "required"]}

    payload = {
        "name": fake_name,
        "prompt": fake_prompt,
        "response_template": response_template,
    }

    headers = superuser_token_headers

    response = client.post(
        f"{settings.API_V1_STR}/dde",
        headers=headers,
        json=payload,
    )

    fake_dde = DocumentDataExtractorOut(
        id=1,
        name=fake_name,
        prompt=fake_prompt,
        timestamp="2024-10-03T09:31:33.748765",
        owner_id=1,
        document_data_examples=[],
        response_template=json.dumps(response_template),
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == fake_dde.id
    assert response_data["name"] == fake_dde.name
    assert response_data["prompt"] == fake_dde.prompt
    assert response_data["owner_id"] == fake_dde.owner_id
    assert response_data["response_template"] == fake_dde.response_template
    assert len(response_data["document_data_examples"]) == 0

    yield response_data

    dde_name = response_data["name"]
    id_example = response_data["document_data_examples"][0]["id"]
    with patch.object(Documents, "exists", return_value=True):
        r = client.delete(
            f"{settings.API_V1_STR}/dde/{dde_name}/example/{id_example}",
            headers=superuser_token_headers,
        )

        assert r.status_code == 200
        r_data = r.json()
        assert r_data["message"] == "DocumentDataExample deleted successfully"

    response = client.delete(
        f"{settings.API_V1_STR}/dde/{response_data['id']}",
        headers=superuser_token_headers,
    )

    assert response.status_code == 200
    response_data = response.json()
    assert (
        response_data["message"]
        == "DocumentDataExtractor deleted successfully"
    )


def test_update_document_data_extractor(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    document_data_extractor: dict[str, Any],
):
    updated_name = "Updated_dde"
    dde_id = document_data_extractor["id"]

    document_data_extractor["name"] = updated_name

    update_payload = {
        "name": updated_name,
        "prompt": document_data_extractor["prompt"],
        "response_template": json.loads(
            document_data_extractor["response_template"]
        ),
    }

    response = client.put(
        f"{settings.API_V1_STR}/dde/{dde_id}",
        headers=superuser_token_headers,
        json=update_payload,
    )

    assert response.status_code == 200

    response_data = response.json()
    assert response_data["id"] == dde_id
    assert response_data["name"] == updated_name
    assert response_data["prompt"] == document_data_extractor["prompt"]
    assert response_data["timestamp"] == document_data_extractor["timestamp"]
    assert response_data["owner_id"] == document_data_extractor["owner_id"]
    assert (
        response_data["response_template"]
        == document_data_extractor["response_template"]
    )
    assert len(response_data["document_data_examples"]) == 0


def test_create_document_data_example(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    document_data_extractor: dict[str, Any],
):
    name = document_data_extractor["name"]

    with patch.object(Documents, "exists", return_value=True):
        start_page = 0
        end_page = 2
        info_to_extract = {"adresse": "3 RUE DE ROUVRAY"}

        data_doc = {
            "document_id": "abc",
            "data": info_to_extract,
            "document_data_extractor_id": document_data_extractor["id"],
            "start_page": start_page,
            "end_page": end_page,
            "id": 1,  # id = 1 because only one example is created in the test
        }

        document_data_extractor["document_data_examples"].append(data_doc)

        response = client.post(
            f"{settings.API_V1_STR}/dde/{name}/example",
            headers=superuser_token_headers,
            json=data_doc,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["document_id"] == data_doc["document_id"]
        assert response_data["data"] == json.dumps(data_doc["data"])
        assert (
            response_data["document_data_extractor_id"]
            == data_doc["document_data_extractor_id"]
        )
        assert response_data["id"] == 1


def test_update_document_data_example(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    document_data_extractor: dict[str, Any],
):
    name_dde = document_data_extractor["name"]
    id_example = document_data_extractor["document_data_examples"][0]["id"]
    updated_data = {"adresse": "2 ALLEE DES HORTENSIAS"}

    update_payload = {
        "document_id": document_data_extractor["document_data_examples"][0][
            "document_id"
        ],
        "data": updated_data,
        "document_data_extractor_id": document_data_extractor[
            "document_data_examples"
        ][0]["document_data_extractor_id"],
        "start_page": document_data_extractor["document_data_examples"][0][
            "start_page"
        ],
        "end_page": document_data_extractor["document_data_examples"][0][
            "end_page"
        ],
    }

    document_data_extractor["document_data_examples"][0]["data"] = updated_data

    with patch.object(Documents, "exists", return_value=True):
        response = client.put(
            f"{settings.API_V1_STR}/dde/{name_dde}/example/{id_example}",
            headers=superuser_token_headers,
            json=update_payload,
        )

        assert response.status_code == 200

        response_data = response.json()
        assert response_data["document_id"] == "abc"
        assert response_data["data"] == json.dumps(updated_data)
        assert response_data["document_data_extractor_id"] == 1
        assert response_data["id"] == 1
 
# TODO: test extract_from_file
