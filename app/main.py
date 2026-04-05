"""FastAPI application with SSE streaming for research pipeline."""

import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from google.cloud import secretmanager

from app.models import ResearchRequest
from app.pipeline import run_pipeline_stream


def _ensure_env_var(env_name: str, secret_name: str, project_id: str = "research-agent-12345") -> str:
    """
    Make sure the required environment variable is present by fetching the
    backing Secret Manager value when not provided directly.
    """
    value = os.getenv(env_name)
    if value:
        return value

    # Try to get project identifier from environment
    project_number = (
        os.getenv("SECRET_PROJECT_NUMBER")
        or os.getenv("AIP_PROJECT_NUMBER")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or project_id  # Fall back to default project ID
    )

    if not project_number:
        raise ValueError(
            f"{env_name} missing and no project identifier found to fetch secret"
        )

    try:
        client = secretmanager.SecretManagerServiceClient()
        secret_path = f"projects/{project_number}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(name=secret_path)
        value = response.payload.data.decode("utf-8").strip()
        if not value:
            raise ValueError(f"Secret {secret_name} is empty")

        os.environ[env_name] = value
        return value
    except Exception as e:
        raise ValueError(
            f"Failed to fetch {env_name} from Secret Manager: {str(e)}"
        )


# Load environment variables
load_dotenv()

# Verify API keys (fetch from Secret Manager if not provided as env vars)
_ensure_env_var(
    "OPENAI_API_KEY",
    os.getenv("OPENAI_SECRET_NAME", "openai-api-key"),
)
_ensure_env_var(
    "TAVILY_API_KEY",
    os.getenv("TAVILY_SECRET_NAME", "tavily-api-key"),
)

# Create FastAPI app
app = FastAPI(
    title="Research Pipeline API",
    description="Multi-agent research pipeline with SSE streaming",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {
        "status": "healthy",
        "service": "research-pipeline",
        "version": "1.0.0"
    }


@app.post("/research")
async def research(request: ResearchRequest):
    """
    Research endpoint with Server-Sent Events (SSE) streaming.

    Streams progress updates as the pipeline executes.
    """
    async def event_generator():
        async for event in run_pipeline_stream(request.query):
            # Format as SSE
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Research Pipeline API",
        "endpoints": {
            "health": "/health",
            "research": "/research (POST)",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
