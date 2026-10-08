from fastapi.testclient import TestClient

from app import api


client = TestClient(api.app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }


def test_list_meters(monkeypatch):
    def mock_search_meters(query="", page=1):
        return {
            "data": [
                {
                    "meterId": "J100000",
                    "serialNo": "SE33962",
                    "make": "HPL",
                    "phaseType": "single",
                    "installStatus": "Decommissioned",
                    "dtCode": "DT-001",
                }
            ],
            "total": 1,
            "page": page,
            "pageSize": 20,
        }

    monkeypatch.setattr(
        api.client,
        "session_established",
        lambda: True,
    )

    monkeypatch.setattr(
        api.client,
        "search_meters",
        mock_search_meters,
    )

    response = client.get("/meters?q=&page=1")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["page"] == 1
    assert data["meters"][0]["meter_id"] == "J100000"
    assert data["meters"][0]["serial_no"] == "SE33962"


def test_meter_energy(monkeypatch):
    def mock_get_meter_energy(meter_id):
        return {
            "data": [
                {
                    "timestamp": "01/01/2026 00:00",
                    "kwh": "1000.5",
                    "kvarh": "120.2",
                    "voltR": "230.4",
                }
            ]
        }

    monkeypatch.setattr(
        api.client,
        "session_established",
        lambda: True,
    )

    monkeypatch.setattr(
        api.client,
        "get_meter_energy",
        mock_get_meter_energy,
    )

    response = client.get(
        "/meters/J100000/energy"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["meter_id"] == "J100000"
    assert len(data["readings"]) == 1
    assert data["readings"][0]["kwh"] == 1000.5
    assert data["readings"][0]["kvarh"] == 120.2
    assert data["readings"][0]["volt_r"] == 230.4


def test_meter_consumption(monkeypatch):
    def mock_get_meter_energy(meter_id):
        return {
            "data": [
                {
                    "timestamp": "01/01/2026 00:00",
                    "kwh": "1000.0",
                },
                {
                    "timestamp": "01/01/2026 01:00",
                    "kwh": "1012.5",
                },
                {
                    "timestamp": "01/01/2026 02:00",
                    "kwh": "1020.0",
                },
            ]
        }

    monkeypatch.setattr(
        api.client,
        "session_established",
        lambda: True,
    )

    monkeypatch.setattr(
        api.client,
        "get_meter_energy",
        mock_get_meter_energy,
    )

    response = client.get(
        "/meters/J100000/consumption"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["meter_id"] == "J100000"
    assert len(data["readings"]) == 2

    assert data["readings"][0]["consumption_kwh"] == 12.5
    assert data["readings"][1]["consumption_kwh"] == 7.5

    assert data["total_consumption_kwh"] == 20.0


def test_meter_location(monkeypatch):
    def mock_get_meter_geo(meter_id):
        return {
            "data": {
                "latitude": "26.4499",
                "longitude": "80.3319",
            }
        }

    monkeypatch.setattr(
        api.client,
        "session_established",
        lambda: True,
    )

    monkeypatch.setattr(
        api.client,
        "get_meter_geo",
        mock_get_meter_geo,
    )

    response = client.get(
        "/meters/J100000/location"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["meter_id"] == "J100000"
    assert data["location"]["latitude"] == 26.4499
    assert data["location"]["longitude"] == 80.3319