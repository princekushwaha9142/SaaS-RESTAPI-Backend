# SaaS-RESTAPI-Backend 

![CI](https://github.com/princekushwaha9142/SaaS-RESTAPI-Backend/actions/workflows/test.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)
![Tests](https://img.shields.io/badge/Tests-20%20passed-brightgreen?logo=pytest)
![License](https://img.shields.io/badge/License-MIT-yellow)

> Production-grade **Task & Project Management REST API** — built with FastAPI, PostgreSQL (async), JWT auth, and Docker.

---

## Features

### Authentication
- JWT access tokens (30 min expiry) + refresh tokens (7 days)
- bcrypt password hashing
- OAuth2 password flow compatible with Swagger UI
- Protected routes via `Depends(get_current_user)`

### Project Management
- Create projects with auto-generated unique slugs
- Role-based membership — Owner / Admin / Member / Viewer
- Add/remove members with ownership validation
- Cascade deletes — project delete removes all tasks and members

### Task Management
- Full CRUD with 6 status states: `backlog → todo → in_progress → in_review → done → cancelled`
- 4 priority levels: `low / medium / high / urgent`
- Many-to-many **Tags** — auto-created on first use, reused across tasks
- **Assignee** support — assign tasks to project members
- Due dates

### Advanced Filtering
- Filter tasks by `status`, `priority`, `assignee_id`
- **Full-text search** on title + description (`ILIKE`)
- Pagination with `skip` + `limit`

### Threaded Comments
- Add comments to any task
- Reply to comments (parent-child threading via `parent_id`)

### Testing
- 20 automated tests covering auth, projects, tasks
- Isolated SQLite test database — no Docker needed to run tests
- Session rollback between tests for clean state

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
| Testing | pytest + httpx + aiosqlite |
| Deploy | Docker + docker-compose |
| CI/CD | GitHub Actions |

---

## Quick Start

```bash
# Clone
git clone https://github.com/princekushwaha9142/SaaS-RESTAPI-Backend.git
cd SaaS-RESTAPI-Backend

# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# DB start karo
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
# 20 passed in 8.95s
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register |
| `POST` | `/auth/login` | Login → JWT |
| `GET` | `/auth/me` | Current user |
| `GET/POST` | `/projects/` | List / Create project |
| `GET/PATCH/DELETE` | `/projects/{id}` | Project CRUD |
| `POST/DELETE` | `/projects/{id}/members` | Membership |
| `GET/POST` | `/projects/{id}/tasks` | List / Create task |
| `GET/PATCH/DELETE` | `/tasks/{id}` | Task CRUD |
| `GET/POST` | `/tasks/{id}/comments` | Comments |

---

## 📁 Structure

SaaS-RESTAPI-Backend/

├── app/
│   ├── main.py              # FastAPI app, CORS, error handlers
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
│   │   ├── project.py       # Project + Member schema
│   │   └── task.py          # Task + Comment + Filter schemas
│   ├── services/
│   │   ├── auth.py          # JWT create/decode, bcrypt hashing
│   │   ├── user.py          # User DB operations
│   │   ├── project.py       # Project CRUD + slug + membership
│   │   └── task.py          # Task CRUD + filters + tags + comments
│   └── routers/
│       ├── auth.py          # POST /auth/register, login, refresh, me
│       ├── projects.py      # /projects CRUD + members
│       └── tasks.py         # /tasks CRUD + filters + comments
├── migrations/
│   ├── env.py               # Async Alembic env
│   └── versions/            # Auto-generated migration scripts
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
└── requirements.txt
└── Readme.md

---

## 👨‍💻 Author

**Prince Kushwaha** — [@princekushwaha9142](https://github.com/princekushwaha9142)

---

<div align="center">
  <em>24 endpoints · 20 tests · Production-ready</em>
</div>