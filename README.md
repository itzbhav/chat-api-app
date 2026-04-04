# Real-Time Chat API

A scalable real-time messaging microservice built with FastAPI and Redis Pub/Sub,
deployed via a full GitOps CI/CD pipeline.

## Tech Stack
- **App**: FastAPI + Redis Pub/Sub
- **Containerization**: Docker + Docker Compose
- **CI**: GitHub Actions + Pytest + Trivy + SonarQube
- **CD**: Argo CD (handled by partner in Config Repo)
- **Orchestration**: Kubernetes with HPA
- **Monitoring**: Prometheus + Grafana

## Local Development

### Run with Docker Compose
```bash
docker-compose up --build
```

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /send?room=&username=&message= | Send a message |
| GET | /history/{room} | Get last 50 messages |
| WS | /chat/{room} | Live WebSocket chat |

### Run Tests Locally
```bash
pip install -r requirements.txt
pytest tests/ -v
```

## GitHub Secrets Required
| Secret | Description |
|--------|-------------|
| DOCKERHUB_USERNAME | Docker Hub username |
| DOCKERHUB_TOKEN | Docker Hub access token |
| SONAR_TOKEN | SonarCloud token |
| CONFIG_REPO_TOKEN | GitHub PAT to push to config repo |
