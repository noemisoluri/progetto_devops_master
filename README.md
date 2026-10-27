# Sentiment Analysis Microservice & DevOps Infrastructure

Repository GitHub: [progetto_devops_master](https://github.com/noemisoluri/progetto_devops_master.git)  

---

## 📌 Panoramica del Progetto

Il progetto implementa un'architettura completa di Continuous Integration, Continuous Deployment (CI/CD) e osservabilità in produzione per un microservizio basato su **FastAPI** utilizzato per analizzare il sentiment di recensioni testuali (Positive, Negative, Neutral).

L'infrastruttura automatizza l'intero ciclo di vita del software:
- **Build & Test automatici** a ogni commit tramite **Jenkins**.
- **Deploy continuo** del container applicativo.
- **Raccolta e visualizzazione metriche** real-time tramite **Prometheus**, **cAdvisor** e **Grafana**.

---

## Componenti dell'Infrastruttura

### 1. Microservizio (`app/main.py`)
- Framework web asincrono **FastAPI**.
- Endpoint REST `/predict` per l'inferenza del sentiment con calcolo della confidenza.
- Endpoint `/metrics` conforme allo standard OpenMetrics/Prometheus basato su registro globale standard (`REGISTRY`).
- Endpoint di sanità `/healthz` per il monitoraggio dello stato operativo e del modello.


 **Metriche Prometheus personalizzate esposte:**
  - `model_predictions_total`: Counter per il conteggio totale delle predizioni per classe di sentiment (label: `sentiment`).
  - `model_prediction_duration_seconds`: Histogram per il monitoraggio della latenza di inferenza e il calcolo dei percentili (P50, P95, P99) con bucket dedicati (`0.01s` - `2.5s`).
  - `model_prediction_errors_total`: Counter per il tracciamento degli errori suddivisi per tipologia (label: `error_type` con valori `empty_text`, `low_confidence`, `internal_error`).


### 2. Suite di Test Automatici (`tests/`)
La qualità e l'affidabilità del microservizio sono garantite da una suite di test automatici basata su **Pytest** e sul client di test di FastAPI (`TestClient`). I test vengono eseguiti sia in locale sia in maniera completamente isolata all'interno del container Docker durante lo stage `Test Automatici` della pipeline Jenkins.

I test coprono la validazione dell'input, il comportamento del modello di machine learning, il controllo di integrità e l'esposizione delle metriche di monitoraggio.

# Esecuzione della suite completa tramite Pytest
pytest tests/ -v

# Esecuzione isolata nel container Docker (come eseguito da Jenkins)
docker run --rm -e PYTHONPATH=/app sentiment-service:latest pytest tests/ -v

### 3. Pipeline CI/CD (`Jenkinsfile`)
Pipeline dichiarativa orchestrata su Jenkins strutturata nei seguenti stage:
1. **Checkout**: Download automatico del codice sorgente su commit tramite trigger `pollSCM('* * * * *')`.
2. **Docker Build**: Compilazione dell'immagine Docker locale etichettata con numero di build e tag `latest`.
3. **Test Automatici**: Esecuzione dei test Pytest all'interno di un container usa-e-getta (`docker run --rm`). In caso di test fallito, la pipeline interrompe il flusso impedendo il rilascio.
4. **Deploy**: Riavvio forzato del container `sentiment-service` collegato alla rete condivisa `progetto_modulo_deploy_default` del docker compose.
5. **Post-Actions (Notifiche)**: Gestione delle notifiche di esito (Success / Failure) con blocco `mail` protetto da gestione delle eccezioni.

### 4. Stack di Monitoraggio (`docker-compose.yml`)
- **Prometheus** (`:9090`): Raccoglie a intervalli regolari i dati esposti dagli scrape target `sentiment-service:8000/metrics` e `cadvisor:8080/metrics`.
- **cAdvisor** (`:8090` / interna `:8080`): Analizzatore di utilizzo delle risorse hardware (CPU, RAM, Network I/O) a livello container.
- **Grafana** (`:3000`): Dashboard interattiva per l'osservabilità dello stato del microservizio.

---

## Dashboard Grafana e Query PromQL

I pannelli della dashboard sono configurati con le seguenti metriche:

| # | Titolo Pannello | Query PromQL | Descrizione |
|---|---|---|---|
| **1** | Throughput Predizioni | `sum(rate(model_predictions_total[1m]))` | Frequenza delle richieste al secondo (req/s) |
| **2** | Totale Predizioni per Sentiment | `sum by (sentiment) (model_predictions_total)` | Volume totale delle predizioni raggruppate per etichetta |
| **3** | Latenza Media Predizione| `rate(model_prediction_duration_seconds_sum[1m]) / rate(model_prediction_duration_seconds_count[1m])` | Tempo medio di elaborazione delle risposte |
| **4** | Latenza 95° Percentile | `histogram_quantile(0.95, sum(rate(model_prediction_duration_seconds_bucket[1m])) by (le))` | P95 della latenza (SLA/Performance) |
 **5** | Latenza 99° Percentile | `histogram_quantile(0.99, sum(rate(model_prediction_duration_seconds_bucket[1m])) by (le))` | P99 della latenza (SLA/Performance) |
| **5** | Errori di predizione | `sum by (error_type) (rate(model_prediction_errors_total[1m]))` | Frequenza degli errori applicativi per tipologia (`empty_text`, `low_confidence`, `internal_error`) |
| **6** | Utilizzo RAM | `process_resident_memory_bytes` | Memoria fisica impiegata dal servizio |
| **7** | Utilizzo CPU | `sum(rate(container_cpu_usage_seconds_total{id="/"}[1m])) * 100` | Percentuale di CPU consumata |


La configurazione della dashboard in JSON è salvata nel file `dashboard.json`, mentre nella cartella `screenshot` sono presenti alcuni screenshot della dashboard.
---

## Guida all'Installazione ed Esecuzione

### Prerequisiti
- Docker e Docker Compose installati

### 1. Avvio dei Servizi di Supporto
Dalla root di progetto avviare lo stack composto da Prometheus, cAdvisor, Grafana e Jenkins:
```bash
docker compose up -d
```

### 2. Endpoint dei Servizi
- **FastAPI Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Metrics Endpoint**: [http://localhost:8000/metrics](http://localhost:8000/metrics)
- **Prometheus UI**: [http://localhost:9090](http://localhost:9090)
- **Prometheus Targets**: [http://localhost:9090/targets](http://localhost:9090/targets)
- **cAdvisor Dashboard**: [http://localhost:8090](http://localhost:8090)
- **Grafana Dashboard**: [http://localhost:3000](http://localhost:3000) (Login: `admin` / `admin`)
- **Jenkins CI/CD**: [http://localhost:8080](http://localhost:8080)

