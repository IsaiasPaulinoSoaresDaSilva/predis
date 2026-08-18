import os

import pytest
from fastapi.testclient import TestClient

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "disaster_model.joblib")

pytestmark = pytest.mark.skipif(
    not os.path.exists(MODEL_PATH),
    reason="disaster_model.joblib não encontrado — rode `python -m backend.model` antes dos testes.",
)


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Usa um banco SQLite temporário e isolado por teste, para não sujar
    # (nem depender de) backend/predis.db.
    from backend import database
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test_predis.db"))

    from backend.main import app
    with TestClient(app) as test_client:
        yield test_client


def test_root_message(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "PreDis" in response.json()["message"]
    assert "São José dos Campos" in response.json()["message"]


def test_predict_known_region_returns_valid_response(client):
    response = client.post("/predict", json={"region": "leste"})
    assert response.status_code == 200
    body = response.json()
    assert body["risk_level"] in (0, 1, 2)
    assert 0.0 <= body["risk_probability"] <= 1.0
    assert isinstance(body["feature_importance"], dict)
    assert len(body["feature_importance"]) > 0


def test_predict_unknown_region_falls_back_and_still_responds(client):
    # DataManager cai para 'default' quando a região não existe no
    # location_map — a API não deve quebrar, deve responder normalmente.
    response = client.post("/predict", json={"region": "regiao-inexistente"})
    assert response.status_code == 200
    assert response.json()["risk_level"] in (0, 1, 2)


def test_predict_persists_to_history(client):
    client.post("/predict", json={"region": "sul"})
    response = client.get("/predictions", params={"region": "sul"})
    assert response.status_code == 200
    records = response.json()
    assert len(records) >= 1
    assert records[0]["region"] == "sul"


def test_historical_data_endpoint_returns_records(client):
    response = client.get("/historical_data", params={"region": "centro"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "precipitacao_mm" in data[0]


def test_predictions_endpoint_respects_limit(client):
    for _ in range(3):
        client.post("/predict", json={"region": "oeste"})
    response = client.get("/predictions", params={"region": "oeste", "limit": 2})
    assert response.status_code == 200
    assert len(response.json()) == 2
