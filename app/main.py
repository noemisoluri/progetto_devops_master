
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import uvicorn
import os

import pickle
import logging

#Imposto il logger in modo tale che scriva sia su console che su un file. Voglio loggare tutte le richieste quindi utilizzo il livello debug.
logging.basicConfig(level=logging.DEBUG, format=" %(name)s - %(asctime)s - %(message)s", datefmt="%d/%m/%Y %H:%M:%S",
                    handlers=[logging.FileHandler("audit.log", mode="a", encoding="utf-8"), logging.StreamHandler()]
                    )
logger = logging.getLogger(__name__)

# metriche prometheus
REQUEST_LATENCY = Histogram(
    "model_prediction_duration_seconds",
    "Tempo di risposta per la predizione del sentiment in secondi",
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

PREDICTION_TOTAL = Counter(
    "model_predictions_total",
    "Conteggio totale delle predizioni per classe di sentiment",
    ["sentiment"]
)

PREDICTION_ERRORS = Counter(
    "model_prediction_errors_total",
    "Conteggio errori durante la predizione",
    ["error_type"]
)

#Definisco i modelli dati.

#Il body sarà composto da un attributo text obbligatorio
class PredictBody(BaseModel):
    review: str = Field(..., title="Testo di cui identificare il sentiment", example="This product is amazing! I love it.")

#L'output sarà un oggetto contenente  il codice della lingua e la probabilità associata
class PredictionOutput(BaseModel):
    sentiment: str = Field(..., title="Sentiment predetto")
    confidence: float = Field(..., title="Probabilità associata alla predizione")


#Carico il modello di Machine Learning pubblicato su github precedentemento scaricato nella mia cartella di lavoro
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
path_model = os.path.join(CURRENT_DIR, "sentiment_analysis_model.pkl")

with open(path_model, 'rb') as f:
    model = pickle.load(f)


#Inizializzo l'API usando la libreira FastAPI
app = FastAPI(title="SentimentAnalysisAPI",description="API per il Riconoscimento del sentiment di un testo")


#Creo l'endpoind di tipo post che prende in input un oggetto di tipo PredictBody e restituisce un output di tipo PredictionOutput
@app.post("/predict", tags=["SentimentAnalysisAPI"])
def predict_sentiment(body: PredictBody):

    """Endopoint per la predizione del sentiment della recensione"""
    # Controllo se il testo è vuoto o composto solo da spazi
    if body.review is None or body.review.strip() == '':
        logger.error("Ricevuto input con testo vuoto")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST ,detail="Il testo ricevuto è vuoto")

    logger.info(f"Ricevuto il messaggio {body.review}")

    try:
        # Predizione del sentiment
        predict_sentiment = model.predict([body.review])[0]

        # Calcolo della probabilità
        predicted_sentiment_proba = model.predict_proba([body.review])[0]
        confidence = round(float(predicted_sentiment_proba.max()),
                           2)  # Arrotondato a 2 decimali come da esempio della traccia

       
        #Se lìil valore di confidence è minore del 50%, decido anche in questo caso di lanciare un errore,
        # in quantò la probabilità è troppo bassa
        if confidence<0.5:
            logger.error(f"Sentiment identificato: {predict_sentiment} - Confidence: {confidence}. La confidence è troppo bassa!!")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Il testo ricevuto non è sufficientemente adeguato per predire il sentiment")

        # Creazione dell'output
        response_data = PredictionOutput(sentiment=predict_sentiment, confidence=confidence)

        # Loggo la risposta
        logger.info(f"Sentiment identificato: {predict_sentiment} - Confidence: {confidence}")

        return response_data
    except HTTPException as e:
        # Gestione errore nel caso in cui la lingua non possa essere identificata
        logger.error(f"Errore di identificazione del sentiemnt: {str(e)}")
        raise e
    except Exception as e:
        # Gestione errore generico
        logger.error(f"Errore generico: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Si è verificato un errore imprevisto"
        )



@app.get("/metrics", tags=["Monitoring"])
def get_metrics():
    """Endpoint per lo scrape delle metriche da parte di Prometheus."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)