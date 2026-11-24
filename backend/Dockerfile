FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    ENV=production \
    PYTHONPATH=/app:/app/src

WORKDIR /app

# /app/src permite los imports de Alembic en Linux sin depender del
# separador de rutas de Windows usado en alembic.ini.
COPY pyproject.toml ./
COPY src/ ./src/

# El manifiesto aun no declara FastAPI ni Uvicorn; scope="function"
# requiere FastAPI >= 0.121.0 (ver README.md).
RUN python -m pip install . "fastapi>=0.121.0" uvicorn

COPY alembic/ ./alembic/
COPY alembic.ini ./

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home \
        --home-dir /nonexistent --shell /usr/sbin/nologin app

USER 10001:10001

# DATABASE_URL se proporciona al ejecutar el contenedor.
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
