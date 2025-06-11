import json

from api import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_initialize(client):
    response = client.post("/initialize", json={"force": True})
    assert response.status_code == 201


def test_create_titles(client):
    response = client.post("/titles")
    assert response.status_code == 201


def test_get_titles(client):
    response = client.get("/titles")
    assert response.status_code == 200
    response = json.loads(response.data)
    assert len(response) > 0


def test_get_issue_dates(client):
    response = client.get("/titles/amendments/issue_dates/1")
    assert response.status_code == 200
    response = json.loads(response.data)
    assert len(response) > 0


def test_get_amendment_dates(client):
    response = client.get("/titles/amendments/issue_dates/2")
    assert response.status_code == 200
    response = json.loads(response.data)
    assert len(response) > 0


def test_create_agencies(client):
    response = client.post("/agencies")
    assert response.status_code == 201


def test_get_agencies(client):
    response = client.get("/agencies")
    assert response.status_code == 200
    response = json.loads(response.data)
    assert len(response) > 0


def test_get_references(client):
    response = client.get("/references")
    assert response.status_code == 200
    response = json.loads(response.data)
    assert len(response) > 0


def test_create_insights(client):
    response = client.post("/insights", json={"agency_id": 1, "date": "2025-06-03"})
    assert response.status_code == 201


def test_get_insights(client):
    response = client.get("/insights/1?from_date=2024-01-01")
    assert response.status_code == 200
    response = json.loads(response.data)
    assert len(response) == 1

    response = client.get("/insights/1?from_date=2025-12-01")
    assert response.status_code == 200
    response = json.loads(response.data)
    assert len(response) == 0
