# SaaS-RESTAPI-Backend 

![CI](https://github.com/princekushwaha9142/SaaS-RESTAPI-Backend/actions/workflows/test.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)
![Tests](https://img.shields.io/badge/Tests-20%20passed-brightgreen?logo=pytest)
![License](https://img.shields.io/badge/License-MIT-yellow)

> Production-grade **Task & Project Management REST API** — built with FastAPI, PostgreSQL (async), JWT auth, Redis, Email notifications, and Docker.

🔗 **Live API:** [saas-restapi-backend.onrender.com/docs](https://saas-restapi-backend.onrender.com/docs)

---

## 🎯 Problem Statement

Most task management APIs are either too simple (no auth, no roles) or too complex to understand. This project bridges that gap — a production-grade backend with real-world patterns:

- Async database layer for high performance
- JWT with refresh tokens (not just basic auth)
- Role-based access control on every endpoint
- Rate limiting to prevent abuse
- Email notifications for key events
- Automated tests with isolated test database
- Fully containerized and deployed

---

## 📊 Metrics

| Metric | Value |
|--------|-------|
| API Endpoints | 24 |
| Automated Tests | 20 (100% pass) |
| Database Tables | 8 |
| Docker Services | 3 (API + PostgreSQL + Redis) |
| Rate Limit | 5 requests/min on `/auth/login` |
| Avg Response Time (write) | ~285ms (bcrypt hashing included) |
| Avg Response Time (read) | ~17ms (async SQLAlchemy + asyncpg) |
| Test Run Time | ~4 seconds (SQLite in-memory) |
| Email Provider | Resend (3000 emails/month free) |
| Deployment | Live on Remder + Supabase + Upstash |
| Infrastructure Cost | $0/month |

---

## ✨ Features

### 🔐 Authentication
- JWT access tokens (30 min expiry) + refresh tokens (7 days)
- bcrypt password hashing
- **Rate limiting** — 5 requests/minute on login (brute-force protection)
- OAuth2 password flow compatible with Swagger UI
- Protected routes via `Depends(get_current_user)`

### 📁 Project Management
- Create projects with auto-generated unique slugs
- Role-based membership — Owner / Admin / Member / Viewer
- Add/remove members with ownership validation
- Cascade deletes — project delete removes all tasks and members

### ✅ Task Management
- Full CRUD with 6 status states: `backlog → todo → in_progress → in_review → done → cancelled`
- 4 priority levels: `low / medium / high / urgent`
- Many-to-many **Tags** — auto-created on first use, reused across tasks
- **Assignee** support — assign tasks to project members
- Due dates

### 🔍 Advanced Filtering
- Filter tasks by `status`, `priority`, `assignee_id`
- **Full-text search** on title + description (`ILIKE`)
- Pagination with `skip` + `limit`

### 💬 Threaded Comments
- Add comments to any task
- Reply to comments (parent-child threading via `parent_id`)

### 📧 Email Notifications
- Welcome email on successful registration
- Task assigned notification to assignee
- Project member added notification
- Powered by **Resend** (3000 emails/month free tier)

### 🧪 Testing
- 20 automated tests covering auth, projects, tasks
- Isolated SQLite test database — no Docker needed to run tests
- Session rollback between tests for clean state
- Rate limiter disabled during tests automatically

### 🐳 Docker
- Multi-stage Dockerfile (builder + slim final image)
- Non-root user for container security
- `docker compose up --build` — one command starts everything

---

## 🛠️ Tech Stack

| Layer | Tech |
|-------|------|
| Framework | FastAPI 0.111 |
| Database | PostgreSQL 16 + asyncpg |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Auth | python-jose + passlib/bcrypt |
| Cache | Redis 7 (Upstash) |
| Rate Limiting | SlowAPI |
| Email | Resend |
| Testing | pytest + httpx + aiosqlite |
| Containerization | Docker + docker-compose |
| Hosted DB | Supabase (PostgreSQL) |
| Hosted Cache | Upstash (Redis) |
| Deploy | Render |
| CI/CD | GitHub Actions |

---

## 🏛️ Design Decisions

**Why FastAPI over Django/Flask?**
FastAPI gives async support out of the box, automatic Swagger docs, and Pydantic validation — perfect for a production API with zero boilerplate.

**Why async SQLAlchemy + asyncpg?**
Blocking DB calls kill performance under load. Async SQLAlchemy + asyncpg gives non-blocking DB queries — the entire stack is async from HTTP to DB.

**Why 4-layer architecture?**
Routers only handle HTTP. Services handle business logic. Models handle DB. Schemas handle validation. Each layer is independently testable and replaceable.

**Why separate access + refresh tokens?**
Short-lived access tokens (30 min) limit exposure if stolen. Refresh tokens (7 days) let users stay logged in without re-entering credentials.

**Why Redis + Rate Limiting?**
Redis enables rate limiting on auth endpoints. Login is limited to 5 requests/minute per IP — prevents brute-force attacks in production.

**Why Resend for emails?**
Resend has a simple API, 3000 free emails/month, and reliable delivery. Email failures are silently caught so they never break the main API flow.

**Why Alembic?**
Schema changes need versioning just like code. Alembic gives reversible, trackable migrations — `alembic upgrade head` / `alembic downgrade -1`.

**Why Supabase + Upstash + Render (free stack)?**
Zero cost, production-grade infrastructure. Supabase = managed PostgreSQL, Upstash = serverless Redis, Render = auto-deploy from GitHub.

---

## 🌍 Live Deployment

| Service | Provider | URL |
|---------|----------|-----|
| API | Render | https://saas-restapi-backend.onrender.app |
| API Docs | Render | https://saas-restapi-backend.onrender.com/docs |
| Database | Supabase | PostgreSQL (managed, free) |
| Cache | Upstash | Redis (managed, free) |
| Email | Resend | 3000 emails/month (free) |

---

## 🚀 Quick Start (Local)

```bash
# Clone
git clone https://github.com/princekushwaha9142/SaaS-RESTAPI-Backend.git
cd SaaS-RESTAPI-Backend

# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env me apne values daalo

# DB + Redis start karo
docker run -d --name saas-db \
  -e POSTGRES_DB=taskmanager \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=pass \
  -p 5432:5432 postgres:16-alpine

docker run -d --name saas-redis -p 6379:6379 redis:7-alpine

# Migrate + Run
alembic upgrade head
uvicorn app.main:app --reload
```

**API Docs →** http://localhost:8000/docs

## 🐳 Docker (One Command)

```bash
docker compose up --build
docker exec saas-restapi-backend-api-1 python -m alembic upgrade head
```

---

## 🧪 Tests

```bash
pytest -v
# 20 passed in 4.36s
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register + welcome email |
| `POST` | `/auth/login` | Login → JWT (rate limited) |
| `GET` | `/auth/me` | Current user |
| `GET/POST` | `/projects/` | List / Create project |
| `GET/PATCH/DELETE` | `/projects/{id}` | Project CRUD |
| `POST/DELETE` | `/projects/{id}/members` | Membership + email notification |
| `GET/POST` | `/projects/{id}/tasks` | List / Create task |
| `GET/PATCH/DELETE` | `/tasks/{id}` | Task CRUD + assignment email |
| `GET/POST` | `/tasks/{id}/comments` | Comments |

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL async URL |
| `REDIS_URL` | ✅ | Redis connection URL |
| `SECRET_KEY` | ✅ | JWT signing secret |
| `ALGORITHM` | ❌ | JWT algorithm (default: HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | Default: 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | ❌ | Default: 7 |
| `ENVIRONMENT` | ❌ | development / production |
| `RESEND_API_KEY` | ❌ | Resend API key for emails |
| `FROM_EMAIL` | ❌ | Sender email address |

---

## 📁 Structure

```text
SaaS-RESTAPI-Backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, rate limiter, error handlers
│   ├── config.py            # Typed config via pydantic-settings
│   ├── dependencies.py      # get_db(), get_current_user()
│   ├── models/
│   │   ├── base.py          # Async engine + session factory
│   │   ├── user.py          # User ORM model
│   │   ├── project.py       # Project + ProjectMember models
│   │   └── task.py          # Task, Tag, Comment, task_tags (M2M)
│   ├── schemas/
│   │   ├── token.py         # Token, TokenData
│   │   ├── user.py          # UserCreate, UserRead, UserUpdate
│   │   ├── project.py       # Project + Member schemas
│   │   └── task.py          # Task + Comment + Filter schemas
│   ├── services/
│   │   ├── auth.py          # JWT create/decode, bcrypt hashing
│   │   ├── user.py          # User DB operations
│   │   ├── email.py         # Resend email notifications
│   │   ├── project.py       # Project CRUD + slug + membership
│   │   └── task.py          # Task CRUD + filters + tags + comments
│   └── routers/
│       ├── auth.py          # /auth endpoints
│       ├── projects.py      # /projects CRUD + members
│       └── tasks.py         # /tasks CRUD + filters + comments
├── migrations/
│   ├── env.py               # Async Alembic environment
│   └── versions/            # Migration scripts
├── tests/
│   ├── conftest.py          # SQLite fixtures + async HTTP client
│   ├── test_auth.py         # 7 auth tests
│   ├── test_projects.py     # 6 project tests
│   └── test_tasks.py        # 7 task tests
├── .github/
│   └── workflows/
│       └── test.yml         # GitHub Actions CI pipeline
├── Dockerfile               # Multi-stage production build
├── docker-compose.yml       # API + PostgreSQL + Redis
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## 👨‍💻 Author

**Prince Kushwaha** — [@princekushwaha9142](https://github.com/princekushwaha9142)

---

<div align="center">
  <em>24 endpoints · 20 tests · Email notifications · Rate limited · Live on Railway · Production-ready</em>
</div>
