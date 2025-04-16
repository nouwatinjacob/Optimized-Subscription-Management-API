import pytest
from decimal import Decimal

@pytest.fixture
def payload():
    return {
        "name": "Pro Plan",
        "description": "Access to all premium features",
        "price": "19.99"
    }

def test_create_plan_success(client, payload):
    response = client.post('/plan/create', json=payload)
    data = response.get_json()

    assert response.status_code == 201
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert Decimal(data["price"]) == Decimal(payload["price"])
    assert "id" in data
    assert "created_at" in data


def test_create_plan_validation_error(client):
    invalid_payload = {
        "name": "A",
        "price": "-5.00"
    }

    response = client.post('/plan/create', json=invalid_payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "errors" in data
    assert "description" in data["errors"]
    assert "name" in data["errors"] or "price" in data["errors"]


def test_list_plans(client, payload):
    # Create a plan first
    client.post('/plan/create', json=payload)

    response = client.get('/plan/')
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(p["name"] == payload["name"] for p in data)
