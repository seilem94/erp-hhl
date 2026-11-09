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

`ENV=development`, incluido en `.env.example`, selecciona automáticamente la
[identidad Dummy de desarrollo](src/infrastructure/identity/providers.py) para las
dependencias nuevas. Su actor es estable entre peticiones y simula el acceso
financiero de un socio local; no constituye una sesión autenticada. No se acepta
un actor elegido mediante encabezados o cuerpo de la petición.

El valor predeterminado de `ENV` es `production`. Tanto `production` como `testing`
mantienen deshabilitado el Dummy y requieren un proveedor real o una sustitución
explícita en las pruebas. La selección está centralizada en las
[dependencias HTTP](src/infrastructure/http/dependencies.py).

Para migraciones, PostgreSQL debe estar iniciado y la base creada. Este procedimiento usa una instancia ya provisionada; no configura un servicio del sistema ni contenedores.

## Migraciones con Alembic

La configuración reside en [alembic.ini](alembic.ini) y [alembic/env.py](alembic/env.py), que obtiene la URL desde Settings.

```bash
python -m alembic upgrade head
python -m alembic current
python -m alembic history
```

La revisión `a417b6283c90` añade `projects.has_iva` como clasificación transitoria
nullable, sin valor por defecto ni backfill. Aplicar las migraciones antes de usar
esta versión del backend. El flujo vigente de altas conserva la compatibilidad y
puede dejar obras sin clasificar; la selección fiscal obligatoria y la
regularización histórica siguen el [ADR 0003](../docs/adr/0003-motor-financiero-iva.md).

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

Las pruebas de casos de uso y las HTTP anteriores usan fakes; las pruebas de
repositorios anteriores usan SQLite en memoria. Las pruebas HTTP importan la
configuración de conexión, aunque sustituyan sus repositorios.

### Integración de resúmenes con PostgreSQL

Las [pruebas de resúmenes](tests/infrastructure/test_financial_summaries_postgres.py)
ejecutan los endpoints con TestClient y repositorios SQLAlchemy reales. Requieren
`TEST_DATABASE_URL` como variable de proceso con una conexión PostgreSQL de
pruebas y permiso para crear esquemas. Cada caso genera un esquema aislado, aplica
las migraciones y lo elimina al terminar; no modifica tablas preexistentes.

```bash
TEST_DATABASE_URL='postgresql+psycopg://usuario:clave@localhost:5432/hhl_test' python -m pytest tests/infrastructure/test_financial_summaries_postgres.py -q
```

En PowerShell, definir la variable antes de ejecutar Pytest:

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://usuario:clave@localhost:5432/hhl_test"
python -m pytest tests/infrastructure/test_financial_summaries_postgres.py -q
```

Mantener también `DATABASE_URL` disponible para importar la configuración de la
aplicación. Con `TEST_DATABASE_URL` definida, `python -m pytest tests/ -q` incluye
esta integración en la suite completa. Si falta, esos casos se omiten
explícitamente; si está definida pero no permite conectarse o no es PostgreSQL,
fallan sin reemplazar la base por SQLite. Las pruebas anteriores por sí solas no
acreditan exactitud de agregados ni migraciones en PostgreSQL.
