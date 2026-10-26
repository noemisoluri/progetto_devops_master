## Struttura del Progetto
- `app/`: Servizio FastAPI con endpoint `/predict`, `/metrics` e `/healthz`
- `monitoring/`: Configurazione di Prometheus e metriche dei container
- `tests/`: Test unitari e di integrazione (Pytest)
- `Dockerfile`: Immagine Docker multi-stage per produzione
- `docker-compose.yml`: Ambiente completo locale (App, Prometheus, cAdvisor, Grafana)
- `Jenkinsfile`: Pipeline CI/CD declarativa completa


## Quickstart Locale

1. **Avvio dello stack:**
   ```bash
   docker compose up -d --build
   ```

2. **Test degli endpoint:**
   - Predizione:
     ```bash
     curl -X POST http://localhost:8000/predict \
       -H "Content-Type: application/json" \
       -d '{"review": "This product is amazing! I love it."}'
     ```
   - Metriche: `curl http://localhost:8000/metrics`
   - Grafana UI: `http://localhost:3000` (admin/admin)
   - Prometheus UI: `http://localhost:9090`
  
  Per testare gli endpoint esposti dall'applicazione è possibile anche consultare lo swagger presente alla pagina http://localhost:8000/docs.

## Esecuzione Test

```bash
pip install -r requirements.txt
pytest tests/ -v
```
