# 💎 MORAA GemVision — Docker

Docker configuration for the MORAA GemVision platform.

## 🚧 Status

Docker setup is **coming soon**. The planned configuration will include:

- `docker-compose.yml` with services for:
  - **Frontend** — Next.js production build served via Node
  - **Backend** — FastAPI with Uvicorn + Gunicorn
  - **Celery Worker** — Async task processing
  - **PostgreSQL** — Production database
  - **Redis** — Celery broker & cache

## 🐳 Quick Start (when available)

```bash
docker compose up --build
```

This will start all services and make them available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
