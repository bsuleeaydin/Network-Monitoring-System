def test_no_api_key_rejected(client):
    response = client.get("/devices/")
    assert response.status_code in (401, 403, 422)


def test_wrong_api_key_rejected(client):
    response = client.get("/devices/", headers={"X-API-Key": "yanlis-key"})
    assert response.status_code == 403


def test_correct_api_key_accepted(client, auth_headers):
    response = client.get("/devices/", headers=auth_headers)
    assert response.status_code == 200