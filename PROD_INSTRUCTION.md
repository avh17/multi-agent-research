# PROD_INSTRUCTION.MD

Convert the research pipeline notebook into a production-ready **FastAPI app with SSE streaming, deployed on Google Cloud Run**.

## What to build

1. `app/main.py` → FastAPI, CORS, GET `/health`, POST `/research` (SSE)
2. `app/pipeline.py` → async generator yielding stage events
3. `app/models.py` → `ResearchRequest` + `FinalReport` models
4. `Dockerfile`, `cloudbuild.yaml`, `requirements.txt`

## Key details

- Reuse same agents from notebook
- Unique `SQLiteSession` per request (uuid-based)
- API keys loaded from environment (via Secret Manager or env vars)
- Containerized with Docker and deployed to **Google Cloud Run** as a managed container service

## Deployment steps

1. **Dockerize** the FastAPI app — ensure the container listens on port `8080` (required by Cloud Run).
2. **Push image** to Google Artifact Registry:
   ```
   gcloud builds submit --tag gcr.io/{PROJECT_ID}/research-pipeline
   ```
3. **Deploy to Cloud Run** as a managed service:
   ```
   gcloud run deploy research-pipeline \
     --image gcr.io/{PROJECT_ID}/research-pipeline \
     --region={REGION} \
     --platform=managed \
     --allow-unauthenticated \
     --port=8080 \
     --set-secrets=OPENAI_API_KEY=openai-api-key:latest,TAVILY_API_KEY=tavily-api-key:latest
   ```
4. **Environment variables** (`OPENAI_API_KEY`, `TAVILY_API_KEY`) injected via Cloud Run service config (`--set-secrets`) or pulled from **Google Secret Manager** during runtime.
5. **Health check** — Cloud Run routes traffic to containers listening on the provided `PORT`; ensure `GET /health` returns `200 OK`.
