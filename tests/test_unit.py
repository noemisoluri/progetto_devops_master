import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthz_endpoint():
    """Verifica che l'endpoint /healthz risponda 200 e il modello sia attivo."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True

def test_predict_positive_sentiment():
    """Verifica la predizione corretta per una recensione positiva."""
    payload = {"review": "This product is fantastic, I absolutely loved it!"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data
    assert "confidence" in data
    assert data["confidence"] >= 0.5
    assert isinstance(data["sentiment"], str)

def test_predict_negative_sentiment():
    """Verifica la predizione per una recensione marcatamente negativa."""
    payload = {"review": "Terrible service, broken item, worst purchase ever."}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data
    assert "confidence" in data
    assert data["confidence"] >= 0.5

def test_predict_empty_text():
    """Verifica che un testo vuoto o composto da soli spazi restituisca HTTP 400."""
    response = client.post("/predict", json={"review": "   "})
    assert response.status_code == 400
    assert "vuoto" in response.json()["detail"].lower()

def test_predict_missing_payload():
    """Verifica che una richiesta priva del campo 'review' restituisca HTTP 422 (Unprocessable Entity)."""
    response = client.post("/predict", json={})
    assert response.status_code == 422

def test_metrics_endpoint():
    """Verifica che l'endpoint /metrics restituisca le metriche di Prometheus in formato plain text."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    content = response.text
    assert "model_prediction_duration_seconds" in content
    assert "model_predictions_total" in content