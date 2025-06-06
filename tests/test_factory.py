import json

from api import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_register_user(client):
    response = client.post("/users",
                           json={"username": "test_test", "password": "password_password", "email": "name@domain.com"})
    assert response.status_code == 201
    response_dict = json.loads(response.data)
    assert response_dict["username"] == "test_test"
    assert response_dict["email"] == "name@domain.com"


def test_create_customer(client, basic_auth_header):
    response = client.post("/customers", json={"name": "Satish"}, headers=basic_auth_header)
    assert response.status_code == 201
    response_dict = json.loads(response.data)
    assert response_dict["name"] == "Satish"

    response = client.post("/customers", json={"name": "Christian"}, headers=basic_auth_header)
    assert response.status_code == 201
    response_dict = json.loads(response.data)
    assert response_dict["name"] == "Christian"


def test_get_all_customers(client, basic_auth_header):
    response = client.get("/customers", headers=basic_auth_header)
    assert response.status_code == 200
    response = json.loads(response.data)
    assert len(response) == 6
    assert response[0]["id"] == 1
    assert response[0]["name"] == "Arisha Barron"
    assert response[1]["id"] == 2
    assert response[1]["name"] == "Branden Gibson"
    assert response[2]["id"] == 3
    assert response[2]["name"] == "Rhonda Church"
    assert response[3]["id"] == 4
    assert response[3]["name"] == "Georgina Hazel"
    assert response[4]["id"] == 5
    assert response[4]["name"] == "Satish"
    assert response[5]["id"] == 6
    assert response[5]["name"] == "Christian"


def test_get_customer(client, basic_auth_header):
    response = client.get("/customers/55", headers=basic_auth_header)
    assert response.status_code == 422

    response = client.get("/customers/3", headers=basic_auth_header)
    assert response.status_code == 200
    response_dict = json.loads(response.data)
    assert response_dict["id"] == 3
    assert response_dict["name"] == "Rhonda Church"

    response = client.get("/customers/4", headers=basic_auth_header)
    assert response.status_code == 200
    response_dict = json.loads(response.data)
    assert response_dict["id"] == 4
    assert response_dict["name"] == "Georgina Hazel"


def test_create_customer_account(client, basic_auth_header):
    response = client.post("/accounts", json={"customer_id": 500, "amount": 1000}, headers=basic_auth_header)
    assert response.status_code == 422

    response = client.post("/accounts", json={"customer_id": 1, "amount": 1000}, headers=basic_auth_header)
    assert response.status_code == 201
    response_dict = json.loads(response.data)
    assert response_dict["id"] == 1
    assert response_dict["customer_id"] == 1

    response = client.post("/accounts", json={"customer_id": 2, "amount": 1000}, headers=basic_auth_header)
    assert response.status_code == 201
    response_dict = json.loads(response.data)
    assert response_dict["id"] == 2
    assert response_dict["customer_id"] == 2


def test_get_accounts_for_customer(client, basic_auth_header):
    response = client.get("/accounts/customer/1", headers=basic_auth_header)
    assert response.status_code == 200
    response_dict = json.loads(response.data)[0]
    assert response_dict["id"] == 1
    assert response_dict["customer_id"] == 1

    response = client.get("/accounts/customer/2", headers=basic_auth_header)
    assert response.status_code == 200
    response_dict = json.loads(response.data)[0]
    assert response_dict["id"] == 2
    assert response_dict["customer_id"] == 2


def test_get_all_accounts(client, basic_auth_header):
    response = client.get("/accounts", headers=basic_auth_header)
    assert response.status_code == 200
    response = json.loads(response.data)
    assert len(response) == 2
    assert response[0]["id"] == 1
    assert response[0]["customer_id"] == 1
    assert response[1]["id"] == 2
    assert response[1]["customer_id"] == 2


def test_get_account(client, basic_auth_header):
    response = client.get("/accounts/500", headers=basic_auth_header)
    assert response.status_code == 422

    response = client.get("/accounts/1", headers=basic_auth_header)
    assert response.status_code == 200
    response_dict = json.loads(response.data)
    assert response_dict["id"] == 1
    assert response_dict["customer_id"] == 1


def test_get_account_balance(client, basic_auth_header):
    response = client.get("/accounts/balance/500", headers=basic_auth_header)
    assert response.status_code == 422

    response = client.get("/accounts/balance/1", headers=basic_auth_header)
    assert response.status_code == 200
    response_dict = json.loads(response.data)
    assert response_dict["amount"] == "1000.00"

    response = client.get("/accounts/balance/2", headers=basic_auth_header)
    assert response.status_code == 200
    response_dict = json.loads(response.data)
    assert response_dict["amount"] == "1000.00"


def test_transfer_money(client, basic_auth_header):
    response = client.post("/transfers", json={"from_account_id": 1, "to_account_id": 1, "amount": 100},
                           headers=basic_auth_header)
    assert response.status_code == 422

    response = client.post("/transfers", json={"from_account_id": 99, "to_account_id": 3, "amount": 100},
                           headers=basic_auth_header)
    assert response.status_code == 422

    response = client.post("/transfers", json={"from_account_id": 2, "to_account_id": 1, "amount": -100},
                           headers=basic_auth_header)
    assert response.status_code == 422

    response = client.post("/transfers", json={"from_account_id": 2, "to_account_id": 1, "amount": 100},
                           headers=basic_auth_header)
    assert response.status_code == 201
    response_dict = json.loads(response.data)
    assert response_dict["id"] == 1
    assert response_dict["from_account_id"] == 2
    assert response_dict["to_account_id"] == 1
    assert response_dict["amount"] == "100"

    response = client.get("/accounts/balance/2", headers=basic_auth_header)
    assert response.status_code == 200
    response_dict = json.loads(response.data)
    assert response_dict["amount"] == "900.00"

    response = client.get("/accounts/balance/1", headers=basic_auth_header)
    assert response.status_code == 200
    response_dict = json.loads(response.data)
    assert response_dict["amount"] == "1100.00"

    response = client.post("/transfers", json={"from_account_id": 2, "to_account_id": 1, "amount": 1000},
                           headers=basic_auth_header)
    assert response.status_code == 422


def test_get_transfers_for_account(client, basic_auth_header):
    response = client.get("/transfers/account/1", headers=basic_auth_header)
    assert response.status_code == 200
    response_dict = json.loads(response.data)[0]
    assert response_dict["id"] == 1
    assert response_dict["from_account_id"] == 2
    assert response_dict["to_account_id"] == 1
    assert response_dict["amount"] == "100.00"

    response = client.get("/transfers/account/2", headers=basic_auth_header)
    assert response.status_code == 200
    response_dict = json.loads(response.data)[0]
    assert response_dict["id"] == 1
    assert response_dict["from_account_id"] == 2
    assert response_dict["to_account_id"] == 1
    assert response_dict["amount"] == "100.00"


def test_get_transfer(client, basic_auth_header):
    response = client.get("/transfers/55", headers=basic_auth_header)
    assert response.status_code == 422

    response = client.get("/transfers/1", headers=basic_auth_header)
    assert response.status_code == 200
    response_dict = json.loads(response.data)
    assert response_dict["id"] == 1
    assert response_dict["from_account_id"] == 2
    assert response_dict["to_account_id"] == 1
    assert response_dict["amount"] == "100.00"
