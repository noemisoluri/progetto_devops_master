import logging
import os
import pickle
import time
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, 
import tempfile
import uvicorn


os.environ["PROMETHEUS_MULTIPROC_DIR"] = tempfile.mkdtemp()
from prometheus_client import CollectorRegistry, generate_latest, multiprocess, CONTENT_TYPE_LATEST


# Configurazione logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s - %(asctime)s - %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    handlers=[
        logging.FileHandler("audit.log", mode="a", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Metriche Prometheus
REQUEST_LATENCY = Histogram(
    "model_prediction_duration_seconds",
    "Tempo di risposta per la predizione del sentiment in secondi",
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
)

PREDICTION_TOTAL = Counter(
    "model_predictions_total",
    "Conteggio totale delle predizioni per classe di sentiment",
    ["sentiment"],
)

PREDICTION_ERRORS = Counter(
    "model_prediction_errors_total",
    "Conteggio errori durante la predizione",
    ["error_type"],
)

# Schemi Pydantic
class PredictBody(BaseModel):
    review: str = Field(
        ...,
        title="Testo di cui identificare il sentiment",
        json_schema_extra={"example": "This product is amazing! I love it."},
    )

class PredictionOutput(BaseModel):
    sentiment: str = Field(..., title="Sentiment predetto")
    confidence: float = Field(..., title="Probabilità associata alla predizione")

# Caricamento del modello
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
path_model = os.path.join(CURRENT_DIR, "sentiment_analysis_model.pkl")

with open(path_model, "rb") as f:
    model = pickle.load(f)

# Inizializzazione FastAPI
app = FastAPI(
    title="SentimentAnalysisAPI",
    description="API per il Riconoscimento del sentiment di un testo",
)

@app.get("/healthz", tags=["Health"])
def health_check():
    """Endpoint di controllo integrità del servizio."""
    return {"status": "ok", "model_loaded": model is not None}

@app.post("/predict", response_model=PredictionOutput, tags=["SentimentAnalysisAPI"])
def predict_sentiment(body: PredictBody):
    """Endpoint per la predizione del sentiment della recensione."""
    start_time = time.time()

    # Controllo testo vuoto o composto solo da spazi
    if body.review is None or body.review.strip() == "":
        logger.error("Ricevuto input con testo vuoto")
        PREDICTION_ERRORS.labels(error_type="empty_text").inc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Il testo ricevuto è vuoto",
        )

    logger.info(f"Ricevuto il messaggio: {body.review}")

    try:
        # Predizione e calcolo confidenza
        predicted_sentiment = str(model.predict([body.review])[0])
        predicted_sentiment_proba = model.predict_proba([body.review])[0]
        confidence = round(float(predicted_sentiment_proba.max()), 2)

        # Controllo soglia minima di confidenza (50%)
        if confidence < 0.5:
            logger.error(
                f"Sentiment: {predicted_sentiment}, Confidence: {confidence} troppo bassa"
            )
            PREDICTION_ERRORS.labels(error_type="low_confidence").inc()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Il testo ricevuto non è sufficientemente adeguato per predire il sentiment",
            )

        # Registrazione metriche Prometheus
        REQUEST_LATENCY.observe(time.time() - start_time)
        PREDICTION_TOTAL.labels(sentiment=predicted_sentiment).inc()

        logger.info(
            f"Sentiment identificato: {predicted_sentiment}, Confidence: {confidence}"
        )
        return PredictionOutput(sentiment=predicted_sentiment, confidence=confidence)

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Errore generico: {str(e)}")
        PREDICTION_ERRORS.labels(error_type="internal_error").inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Si è verificato un errore imprevisto",
        )

@app.get("/metrics", tags=["Monitoring"])
def get_metrics():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return Response(content=generate_latest(registry), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)