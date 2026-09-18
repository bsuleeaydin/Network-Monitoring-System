def test_create_device(client, auth_headers):
    response = client.post(
        "/devices/",
        json={
            "name": "Test Router",
            "ip_address": "192.168.1.1",
            "device_type": "router",
            "status": "unknown"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Router"
    assert data["ip_address"] == "192.168.1.1"
    assert "id" in data


def test_get_devices_empty(client, auth_headers):
    response = client.get("/devices/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_device_not_found(client, auth_headers):
    response = client.get("/devices/999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_device(client, auth_headers):
    # önce bir cihaz oluştur
    create_response = client.post(
        "/devices/",
        json={
            "name": "Silinecek Cihaz",
            "ip_address": "192.168.1.2",
            "device_type": "pc",
            "status": "unknown"
        },
        headers=auth_headers
    )
    device_id = create_response.json()["id"]

    # sonra sil
    delete_response = client.delete(f"/devices/{device_id}", headers=auth_headers)
    assert delete_response.status_code == 200

    # tekrar sorunca bulunamamalı
    get_response = client.get(f"/devices/{device_id}", headers=auth_headers)
    assert get_response.status_code == 404