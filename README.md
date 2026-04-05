# AI Research Pipeline

A modular multi-agent research pipeline built with OpenAI Agents SDK, featuring web search, analysis, and automated report generation.

## Architecture

### Multi-Agent Workflow

The system uses a three-stage pipeline:

1. **Researcher Agent**: Uses Tavily to search the web and gather sources
2. **Analyst Agent**: Identifies trends, risks, and key insights
3. **Writer Agent**: Generates executive summary, markdown report, and follow-up questions

### Tech Stack

**Backend**
- **Framework**: FastAPI
- **AI/Agents**: OpenAI Agents SDK
- **LLM**: GPT-4o-mini
- **Search**: Tavily API
- **Data Models**: Pydantic
- **Streaming**: Server-Sent Events (SSE)
- **Session Storage**: SQLite (per-request)
- **Containerization**: Docker

**Frontend**
- **Framework**: React
- **Styling**: Custom CSS (Dark Theme)
- **API Communication**: EventSource (SSE)

**Infrastructure**
- **Backend Hosting**: Google Cloud Run (managed container service)
- **Frontend Hosting**: Vercel
- **Secrets Management**: Google Secret Manager
- **Container Registry**: Google Container Registry (GCR)

### Deployment Locations

- **Backend**: Deployed on Google Cloud Run
  - Serverless, auto-scaling container service
  - Port: 8080
  - Authentication: Unauthenticated (public API)

- **Frontend**: Deployed on Vercel
  - Static React app with SSE integration
  - Connects to Cloud Run backend via HTTPS

### Project Structure

```
researcher-agent/
├── app/
│   ├── main.py          # FastAPI application with SSE endpoints
│   ├── pipeline.py      # Async multi-agent orchestration
│   ├── agents.py        # Researcher, Analyst, Writer agents
│   ├── models.py        # Pydantic data models
│   └── tools.py         # Tavily search tool integration
├── frontend/
│   ├── src/
│   │   ├── App.js       # React application with SSE client
│   │   └── App.css      # Dark theme UI
│   └── package.json
├── Dockerfile           # Backend containerization
├── requirements.txt     # Python dependencies
└── README.md
```
