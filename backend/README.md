# Backend — Entorno de datos

Fuente canónica para preparar el entorno Python, configurar la conexión, gestionar migraciones y ejecutar pruebas. Todos los comandos de este documento parten de `backend/`.

## Entorno virtual

La compatibilidad de Python y las dependencias declaradas se consultan en [pyproject.toml](pyproject.toml).

```bash
python -m venv venv
```

Activar el entorno según el sistema:

```powershell
.\venv\Scripts\Activate.ps1
```

```bash
source venv/bin/activate
```

Instalar el proyecto y las herramientas necesarias para el flujo actual:

```bash
python -m pip install -e ".[dev]" fastapi uvicorn ruff mypy
```

El manifiesto todavía no declara FastAPI, Uvicorn, Ruff ni mypy: la instalación explícita cubre las pruebas HTTP, el arranque de desarrollo y las comprobaciones estáticas. Este documento no modifica las declaraciones de dependencias.

## Configuración local

Copiar [.env.example](.env.example) a `.env` una sola vez, sin sobrescribir una configuración existente:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

```bash
test -e .env || cp .env.example .env
```

Editar `DATABASE_URL` con la conexión PostgreSQL del entorno. Usar el esquema `postgresql+psycopg://` y una base existente accesible para el usuario configurado. El valor de ejemplo no es una credencial de producción.

La configuración se carga desde variables de proceso o el archivo local mediante [Settings](src/core/config.py). Ejecutar desde esta carpeta para que la ruta relativa de `.env` sea correcta. No versionar credenciales ni publicar el archivo local.

Para migraciones, PostgreSQL debe estar iniciado y la base creada. Este procedimiento usa una instancia ya provisionada; no configura un servicio del sistema ni contenedores.

## Migraciones con Alembic

La configuración reside en [alembic.ini](alembic.ini) y [alembic/env.py](alembic/env.py), que obtiene la URL desde Settings.

```bash
python -m alembic upgrade head
python -m alembic current
python -m alembic history
```

Después de modificar deliberadamente el esquema ORM, generar y revisar una migración:

```bash
python -m alembic revision --autogenerate -m "describir cambio de esquema"
```

Revisar el SQL y las operaciones generadas antes de aplicar la revisión. Alembic no sustituye el análisis de pérdida de datos.

Para probar la reversión de una revisión en una base local desechable:

```bash
python -m alembic downgrade -1
```

El downgrade puede eliminar datos; no aplicarlo a una base compartida sin un procedimiento de recuperación.

## Pruebas con Pytest

Con el entorno virtual y una `DATABASE_URL` sintácticamente válida disponibles:

```bash
python -m pytest tests/ -q
python -m pytest tests/use_cases/ -q
python -m pytest tests/infrastructure/ -q
```

La suite actual usa fakes para los casos de uso y las pruebas HTTP, y SQLite en memoria para los repositorios. Las pruebas HTTP importan la configuración de conexión, pero sustituyen sus repositorios. Pasar esta suite no demuestra por sí solo conectividad ni migraciones correctas en PostgreSQL; esas operaciones se verifican separadamente con Alembic.
