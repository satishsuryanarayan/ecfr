import json

from api import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_create_agencies(client):
    response = client.post("/agencies")
    assert response.status_code == 201


def test_get_agencies(client):
    response = client.get("/agencies")
    assert response.status_code == 200
    response = json.loads(response.data)
    assert len(response) > 0


def test_create_insights(client):
    response = client.post("/insights", json={"agency_id": "USDA", "date": "2025-06-03"})
    assert response.status_code == 201

    response = client.post("/insights", json={"agency_id": "USDA", "date": "2024-06-03"})
    assert response.status_code == 201


def test_get_insights(client):
    response = client.get("/insights/USDA?from_date=2024-01-01")
    assert response.status_code == 200
    response = json.loads(response.data)
    assert len(response) == 2

    response = client.get("/insights/USDA?from_date=2025-01-01")
    assert response.status_code == 200
    response = json.loads(response.data)
    assert len(response) == 1
