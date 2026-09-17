# 🚀 Production-Ready URL Shortener API

A high-performance, asynchronous RESTful API built with **Python 3.13**, **FastAPI**, **SQLAlchemy 2.0 (Async)**, **PostgreSQL**, **Alembic**, **Docker**, **Pytest**, and **GitHub Actions**.

This project implements clean architecture principles, real-time analytics tracking, and automated CI/CD pipelines. It is designed to serve as a showcase project for Backend Developer internships and junior software engineering roles.

🌐 **Live Render Deployment**: [https://url-shortener-api-wbsi.onrender.com](https://url-shortener-api-wbsi.onrender.com)  
📖 **Interactive OpenAPI Docs**: [https://url-shortener-api-wbsi.onrender.com/docs](https://url-shortener-api-wbsi.onrender.com/docs)

---

## 📌 Table of Contents

- [Features](#-features)
- [Tech Stack & Architecture](#-tech-stack--architecture)
- [Project Directory Structure](#-project-directory-structure)
- [API Documentation](#-api-documentation)
  - [1. Create Short URL](#1-create-short-url)
  - [2. Redirect to Original URL](#2-redirect-to-original-url)
  - [3. Get URL Basic Stats](#3-get-url-basic-stats)
  - [4. Get Advanced Analytics](#4-get-advanced-analytics)
  - [5. List Short URLs](#5-list-short-urls)
  - [6. Delete Short URL](#6-delete-short-url)
- [Getting Started (Local Development)](#-getting-started-local-development)
- [Docker & Docker Compose Setup](#-docker--docker-compose-setup)
- [Database Migrations (Alembic)](#-database-migrations-alembic)
- [Running Automated Tests](#-running-automated-tests)
- [Deployment Guide (Vercel + Managed PostgreSQL)](#-deployment-guide-vercel--managed-postgresql)
- [Deployment Guide (Render + PostgreSQL)](#-deployment-guide-render--postgresql)
- [Resume & Architectural Deep Dive](#-resume--architectural-deep-dive)

---

## ✨ Features

- **⚡ Asynchronous Performance**: Full async pipeline utilizing FastAPI and SQLAlchemy 2.0 with `asyncpg` for PostgreSQL.
- **🔗 Unique Short Code Generator**: Base62 (0-9, a-z, A-Z) cryptographically secure random short codes with custom alias support and collision handling.
- **🚀 High-Speed Redirects**: HTTP `307 Temporary Redirect` responses with background click logging.
- **📊 Real-Time Advanced Analytics**:
  - Total Clicks
  - Clicks Today
  - Last 7 Days Clicks
  - Last 30 Days Clicks
  - User-Agent & IP address recording
- **🛡️ Data Validation & Error Handling**: Strict Pydantic v2 schemas and clean HTTP error responses (400, 404, 422).
- **🐳 Containerized & Cloud Ready**: Multi-stage `Dockerfile` and `docker-compose.yml` for instant setup.
- **🔄 CI/CD Automation**: GitHub Actions workflow running automated unit and integration tests on every push.

---

## 🛠 Tech Stack & Architecture

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Language** | Python 3.13 | Modern type hinting, GIL optimizations, fast execution. |
| **Framework** | FastAPI | Async IO, automatic OpenAPI specs (`/docs`), Pydantic validation. |
| **Database** | PostgreSQL | Robust relational engine with ACID guarantees and indexing support. |
| **ORM** | SQLAlchemy 2.0 | Asynchronous DB sessions (`AsyncSession`), modern mapped columns. |
| **Migrations** | Alembic | Version-controlled database schema changes. |
| **Testing** | Pytest & `httpx` | Fast async unit and end-to-end API integration tests. |
| **Containerization** | Docker & Compose | Multi-stage image build for production deployment. |
| **CI/CD** | GitHub Actions | Automated build & test execution pipeline. |

---

## 📂 Project Directory Structure

```
url-shortener-api/
│
├── app/
│   ├── main.py                  # FastAPI application entrypoint & middleware
│   ├── database.py              # Async SQLAlchemy engine & session factory
│   ├── core/
│   │   ├── config.py            # Environment configuration via Pydantic BaseSettings
│   │   └── logging.py           # Structured application logging
│   ├── models/
│   │   ├── url.py               # URL ORM model (UUID, original_url, short_code, click_count)
│   │   └── click_log.py         # ClickLog ORM model for analytics
│   ├── schemas/
│   │   └── url.py               # Pydantic validation models
│   ├── services/
│   │   └── url_service.py       # Core business logic layer
│   ├── routers/
│   │   ├── url.py               # Shortening, redirect, listing, and deletion endpoints
│   │   └── analytics.py         # Advanced analytics endpoints
│   ├── utils/
│   │   └── shortener.py         # Base62 generator & URL validator
│   └── dependencies/
│       └── database.py          # FastAPI database session dependency injection
│
├── tests/
│   ├── conftest.py              # Pytest fixtures & async SQLite test database
│   ├── test_shortener.py        # Unit tests for code generation & URL validation
│   └── test_api.py              # End-to-end API integration tests
│
├── alembic/
│   ├── versions/                # Version-controlled DB migration scripts
│   ├── env.py                   # Async Alembic environment migration script
│   └── script.py.mako
│
├── .github/workflows/
│   └── ci.yml                   # GitHub Actions CI pipeline
├── Dockerfile                   # Production multi-stage Docker build
├── docker-compose.yml           # Local multi-container stack (FastAPI + PostgreSQL)
├── requirements.txt             # Project dependencies
├── alembic.ini                  # Alembic migration configuration
├── .env.example                 # Configuration template
└── README.md                    # Project documentation
```

---

## 📖 API Documentation

Interactive Swagger documentation is automatically generated and accessible at:
- **Swagger UI**: [https://url-shortener-api-wbsi.onrender.com/docs](https://url-shortener-api-wbsi.onrender.com/docs)
- **ReDoc**: [https://url-shortener-api-wbsi.onrender.com/redoc](https://url-shortener-api-wbsi.onrender.com/redoc)

### 1. Create Short URL

- **HTTP Method**: `POST`
- **Endpoint**: `/shorten` (or `/api/v1/shorten`)

#### Request Body
```json
{
  "url": "https://example.com/long-page-path",
  "custom_code": "my-alias"
}
```
*Note: `custom_code` is optional.*

#### Response (`201 Created`)
```json
{
  "short_url": "https://url-shortener-api-wbsi.onrender.com/my-alias",
  "short_code": "my-alias",
  "original_url": "https://example.com/long-page-path",
  "click_count": 0,
  "created_at": "2026-09-17T22:00:00Z"
}
```

#### cURL Example
```bash
curl -X POST "https://url-shortener-api-wbsi.onrender.com/shorten" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
```

---

### 2. Redirect to Original URL

- **HTTP Method**: `GET`
- **Endpoint**: `/{short_code}`

#### Response (`307 Temporary Redirect`)
Redirects the user directly to the original target URL and records the click event in `click_logs`.

#### cURL Example
```bash
curl -i "https://url-shortener-api-wbsi.onrender.com/abc123"
```

---

### 3. Get URL Basic Stats

- **HTTP Method**: `GET`
- **Endpoint**: `/stats/{short_code}`

#### Response (`200 OK`)
```json
{
  "short_code": "abc123",
  "original_url": "https://example.com",
  "click_count": 120,
  "created_at": "2026-09-17T22:00:00Z"
}
```

---

### 4. Get Advanced Analytics

- **HTTP Method**: `GET`
- **Endpoint**: `/analytics/{short_code}`

#### Response (`200 OK`)
```json
{
  "short_code": "abc123",
  "original_url": "https://example.com",
  "total_clicks": 120,
  "clicks_today": 15,
  "last_7_days_clicks": 65,
  "last_30_days_clicks": 118,
  "created_at": "2026-09-17T22:00:00Z"
}
```

---

### 5. List Short URLs

- **HTTP Method**: `GET`
- **Endpoint**: `/urls?skip=0&limit=50`

#### Response (`200 OK`)
```json
[
  {
    "id": "c1f7b4e2-9b2f-4c8d-8a1a-3e5f7b8c9d0e",
    "short_url": "https://url-shortener-api-wbsi.onrender.com/abc123",
    "short_code": "abc123",
    "original_url": "https://example.com",
    "click_count": 120,
    "created_at": "2026-09-17T22:00:00Z"
  }
]
```

---

### 6. Delete Short URL

- **HTTP Method**: `DELETE`
- **Endpoint**: `/{short_code}`

#### Response (`200 OK`)
```json
{
  "message": "Short URL 'abc123' successfully deleted."
}
```

---

## 💻 Getting Started (Local Development)

### Prerequisites
- Python 3.13 (or 3.10+)
- Git

### Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/narendrakp222/URL-Shortener-API.git
   cd url-shortener-api
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

5. **Run Application**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   Open `http://localhost:8000/docs` in your browser.

---

## 🐳 Docker & Docker Compose Setup

Run the full stack (FastAPI + PostgreSQL 16) with a single command:

```bash
docker compose up --build
```

The application will automatically:
- Wait for PostgreSQL to become healthy.
- Run Alembic database migrations.
- Expose the API server on `http://localhost:8000`.

To stop services:
```bash
docker compose down
```

---

## 🗄️ Database Migrations (Alembic)

To create a new migration after modifying ORM models:
```bash
alembic revision --autogenerate -m "Add new feature column"
```

To apply pending migrations:
```bash
alembic upgrade head
```

---

## 🧪 Running Automated Tests

The test suite uses `pytest` with `pytest-asyncio` and an in-memory SQLite database for rapid execution.

Run tests:
```bash
pytest -v
```

---

## ☁️ Deployment Guide (Vercel + Managed PostgreSQL)

The repository ships with a Vercel-ready serverless setup:

- `api/index.py` — ASGI entrypoint exposing `app` for `@vercel/python`.
- `vercel.json` — runs `scripts/vercel_build.py`, bundles `api/index.py` on Python 3.12, and routes every path to it.
- `requirements-vercel.txt` — slim runtime dependencies (no pytest/httpx/uvicorn) to stay under Vercel's function size limit.

### 1. Create a PostgreSQL database

Use a serverless-friendly provider (Neon, Supabase, Vercel Postgres) and copy the connection string. The API normalises `postgres://` and `postgresql://` URLs to `postgresql+asyncpg://` and strips libpq-only parameters such as `?sslmode=require`, which `asyncpg` rejects.

### 2. Import the repository into Vercel

1. [Vercel Dashboard](https://vercel.com/new) -> **Add New** -> **Project**.
2. Import your GitHub repository.
3. Framework Preset: **Other**. Leave Build/Output settings as detected — `vercel.json` overrides them.

### 3. Add environment variables

| Variable | Example value | Purpose |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host/db` | Managed Postgres connection string. |
| `BASE_URL` | `https://your-project.vercel.app` | Builds the `short_url` returned by `POST /shorten`. |
| `ENVIRONMENT` | `production` | Disables SQLAlchemy statement echo logging. |
| `LOG_LEVEL` | `INFO` | Application log level. |
| `BACKEND_CORS_ORIGINS` | `https://app.example.com,https://admin.example.com` | Comma-separated allowed origins. Defaults to `*`. |

### 4. Create the schema (required)

Startup table auto-creation is disabled when Vercel is detected (`VERCEL`/`VERCEL_ENV`) unless `DATABASE_URL` points at SQLite, so migrate explicitly from any machine that can reach the database:

```bash
DATABASE_URL="postgresql+asyncpg://user:pass@host/db" alembic upgrade head
```

---

## ☁️ Deployment Guide (Render + PostgreSQL)

### 1. Push Code to GitHub
```bash
git init
git add .
git commit -m "Initial commit of production URL shortener API"
git branch -M main
git remote add origin https://github.com/narendrakp222/URL-Shortener-API.git
git push -u origin main
```

### 2. Create PostgreSQL Database on Render
1. Log into [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **PostgreSQL**.
3. Name: `url-shortener-db`.
4. Click **Create Database**.
5. Copy the **Internal Database URL** (or External Database URL).

### 3. Deploy Web Service on Render
1. Click **New +** -> **Web Service**.
2. Connect your GitHub repository `URL-Shortener-API`.
3. Configure settings:
   - **Environment**: `Docker` or `Python`.
   - **Start Command** (if Python): `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add **Environment Variables**:
   - `DATABASE_URL`: paste your Render PostgreSQL connection string.
   - `BASE_URL`: `https://url-shortener-api-wbsi.onrender.com`
   - `ENVIRONMENT`: `production`
5. Click **Create Web Service**.

---


## 🔮 Future Improvements

- [ ] **Redis Caching Layer**: Cache hot short code mappings in Redis to bypass database reads on frequent redirects.
- [ ] **Rate Limiting**: Implement token-bucket rate limiting via `slowapi` to prevent URL spam.
- [ ] **Expiration Dates**: Allow links to expire after a specified `ttl` or date.
- [ ] **QR Code Generation**: Add `/qr/{short_code}` endpoint returning PNG QR codes.

---

Developed with ❤️ as a portfolio showcase project.
