# Real-Time Chat API — Full DevOps Pipeline

A production-grade real-time messaging application built with **FastAPI + Redis Pub/Sub**, containerized with Docker, and deployed through a fully automated **CI/CD pipeline** using GitHub Actions, SonarCloud, Trivy, Snyk, and a GitOps-based delivery model.

> Built to demonstrate end-to-end DevOps engineering: secure image builds, automated quality gates, vulnerability scanning, and GitOps-driven deployment.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  GitHub Repository                  │
│                 (push / pull request)               │
└──────────────────────┬──────────────────────────────┘
                       │ triggers
                       ▼
┌─────────────────────────────────────────────────────┐
│              GitHub Actions CI Pipeline             │
│                                                     │
│  1. Run Pytest unit tests                           │
│  2. SonarCloud static analysis                      │
│  3. Docker multi-stage image build                  │
│  4. Trivy container vulnerability scan              │
│  5. Snyk dependency vulnerability scan              │
│  6. Push image to Docker Hub                        │
│  7. Update image tag in GitOps config repo          │
└──────────────────────┬──────────────────────────────┘
                       │ image tag update
                       ▼
┌─────────────────────────────────────────────────────┐
│         GitOps Config Repo (chat-api-config)        │
│         manifests/deployment.yaml                   │
│         (watched by ArgoCD / Flux for CD)           │
└─────────────────────────────────────────────────────┘

Runtime (Docker Compose):
  ┌─────────────┐     pub/sub      ┌─────────────┐
  │  FastAPI    │ ◄──────────────► │    Redis    │
  │  :8000      │                  │   :6379     │
  └─────────────┘                  └─────────────┘
        ▲
        │ REST API
  ┌─────────────┐
  │  Streamlit  │
  │  UI :8501   │
  └─────────────┘
```

---

## Tech Stack

| Layer | Tool / Technology |
|---|---|
| **API** | FastAPI, Uvicorn, WebSockets |
| **Messaging** | Redis Pub/Sub (async) |
| **Frontend** | Streamlit |
| **Containerization** | Docker (multi-stage build), Docker Compose |
| **CI** | GitHub Actions |
| **Testing** | Pytest, pytest-asyncio, HTTPX |
| **Static Analysis** | SonarCloud |
| **Container Security** | Trivy (CRITICAL CVEs, patchable only) |
| **Dependency Security** | Snyk |
| **Observability** | Prometheus (`/metrics` endpoint) |
| **Registry** | Docker Hub |
| **GitOps** | Config repo + image tag promotion |

---

## Key Features

- **Real-time messaging** via Redis Pub/Sub — supports multiple named chat rooms simultaneously
- **WebSocket + REST** dual interface — clients can use WebSocket for live updates or REST for stateless access
- **Message history** — last 50 messages per room persisted in Redis
- **Prometheus metrics** — `/metrics` endpoint exposes per-room message counters, ready to scrape
- **Multi-stage Docker build** — builder stage installs dependencies, runtime stage is minimal `python:3.11-slim`
- **Full security pipeline** — container image scanned by Trivy, dependencies scanned by Snyk, code quality gated by SonarCloud
- **GitOps delivery** — CI bot automatically updates the image tag in the config repo on every successful build; no manual deployment steps

---

## CI/CD Pipeline (GitHub Actions)

Every push or PR to `main` triggers the full pipeline:

```
Checkout → Install deps → Pytest → SonarCloud → Docker Build
→ Trivy Scan → Snyk Scan → Docker Push → GitOps Tag Update
```

**Security gates:**
- Trivy fails the build on any **patchable CRITICAL** CVE in the container image
- Snyk fails the build on any **critical** severity dependency vulnerability
- SonarCloud enforces code quality — build fails if quality gate is not met

**GitOps step:** CI clones `itzbhav/chat-api-config`, patches the image tag in `manifests/deployment.yaml` to the exact commit SHA, and pushes — enabling precise, auditable deployments.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Prometheus metrics |
| `POST` | `/send?room=&username=&message=` | Send a message to a room |
| `GET` | `/history/{room}` | Get last 50 messages for a room |
| `WS` | `/chat/{room}` | Live WebSocket chat |

---

## Local Development

**Prerequisites:** Docker + Docker Compose

```bash
# Clone the repo
git clone https://github.com/itzbhav/chat-api-app.git
cd chat-api-app

# Start all services (API + Redis + Streamlit UI)
docker-compose up --build
```

| Service | URL |
|---|---|
| FastAPI (Swagger docs) | http://localhost:8000/docs |
| Prometheus metrics | http://localhost:8000/metrics |
| Streamlit UI | http://localhost:8501 |

**Run tests locally:**
```bash
pip install -r requirements.txt
pytest tests/ -v
```

---

## GitHub Secrets Required

| Secret | Description |
|---|---|
| `DOCKERHUB_USERNAME` | Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `SONAR_TOKEN` | SonarCloud authentication token |
| `SNYK_TOKEN` | Snyk authentication token |
| `CONFIG_REPO_TOKEN` | GitHub PAT with write access to config repo |
