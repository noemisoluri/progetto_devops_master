from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_predict_endpoint_positive():
    payload = {"review": "This product is amazing! I love it."}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "positive"
    assert "confidence" in data

def test_predict_endpoint_invalid_payload():
    response = client.post("/predict", json={"review": ""})
    assert response.status_code in (400, 422)

def test_metrics_endpoint():
    client.post("/predict", json={"review": "Great quality"})
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "model_predictions_total" in response.text
