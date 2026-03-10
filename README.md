# CS 499 Eventful Backend

This backend uses FastAPI.

## Setting up

```bash
pip install -r requirements.txt
```

## Running development server

```bash
fastapi dev app/main.py
```

... and wait for PaddleOCR to load completely.

The backend URL should be localhost:8000.

## Updating the database

If the database models in `/app/db/models.py` are changed, the database must also be upgraded using Alembic

```bash
alembic revision --autogenerate -m "<revision-message>"
alembic upgrade head
```
