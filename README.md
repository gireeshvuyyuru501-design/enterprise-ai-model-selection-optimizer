# Enterprise AI Model Selection Optimizer — Phase 3

Phase 3 extends the Phase 2 dashboard with PostgreSQL persistence, SQLAlchemy ORM,
model catalog CRUD APIs, database seeding, and optimization history.

## Phase 3 features

- PostgreSQL database
- SQLAlchemy 2 ORM
- Persistent AI model catalog
- Create, read, update, and delete model APIs
- Persistent optimization history
- Automatic table creation
- Seed script
- Existing Phase 2 dashboard and charts

## Important

The included model names and metrics are synthetic demonstration data.

## Option A — Start PostgreSQL with Docker

From the project folder:

```powershell
docker compose up -d postgres
```

## Option B — Use local PostgreSQL

Create a database named:

```text
model_optimizer
```

Default development connection:

```text
postgresql+psycopg2://postgres:postgres@localhost:5432/model_optimizer
```

Change `DATABASE_URL` in `.env` if your PostgreSQL password is different.

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

## Seed database

```powershell
python -m app.database.seed
```

Expected output:

```text
Database seed completed. Added 5 model(s).
```

## Run

```powershell
python -m uvicorn app.main:app --reload
```

Open:

- Dashboard: http://127.0.0.1:8000/
- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## New Phase 3 APIs

- `GET /api/v1/models`
- `POST /api/v1/models`
- `GET /api/v1/models/{model_id}`
- `PUT /api/v1/models/{model_id}`
- `DELETE /api/v1/models/{model_id}`
- `GET /api/v1/history`
- `POST /api/v1/select-model`
