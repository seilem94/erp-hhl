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
python -m pip install -e ".[dev]" "fastapi>=0.121.0" uvicorn ruff mypy
```

El manifiesto todavía no declara FastAPI, Uvicorn, Ruff ni mypy: la instalación explícita cubre las pruebas HTTP, el arranque de desarrollo y las comprobaciones estáticas. Este documento no modifica las declaraciones de dependencias.

FastAPI debe soportar `Depends(..., scope="function")` (desde 0.121.0): las
[dependencias HTTP](src/infrastructure/http/dependencies.py) usan ese cierre para
finalizar la sesión antes de enviar la respuesta.

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

La revisión `b528c7394d01` crea el registro de operaciones. Sus confirmaciones e
identidades de deduplicación se perderían al ejecutar su downgrade: ensayar esa
reversión únicamente en una base desechable. La futura limpieza de cuerpos puede
anular `result_payload` sin eliminar la clave, la huella ni sus referencias.

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

### Integración con PostgreSQL

Las [pruebas de resúmenes](tests/infrastructure/test_financial_summaries_postgres.py),
de [operaciones](tests/infrastructure/test_operations_postgres.py), de
[comandos HTTP](tests/infrastructure/test_commands_postgres.py) y de
[recuperación](tests/infrastructure/test_operation_recovery_postgres.py) usan
repositorios SQLAlchemy reales. Cubren TestClient, transacciones independientes,
contención concurrente y aislamiento por actor. Comandos y recuperación comparten
la fábrica de pruebas de sesiones, conservando la dependencia transaccional real
para forzar y observar fallos de commit. Requieren
`TEST_DATABASE_URL` como variable de proceso con una conexión PostgreSQL de
pruebas y permiso para crear esquemas. Cada caso genera un esquema aislado, aplica
las migraciones y lo elimina al terminar; no modifica tablas preexistentes.

```bash
TEST_DATABASE_URL='postgresql+psycopg://usuario:clave@localhost:5432/hhl_test' python -m pytest tests/infrastructure/ -q
```

En PowerShell, definir la variable antes de ejecutar Pytest:

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://usuario:clave@localhost:5432/hhl_test"
python -m pytest tests/infrastructure/ -q
```

Mantener también `DATABASE_URL` disponible para importar la configuración de la
aplicación. Con `TEST_DATABASE_URL` definida, `python -m pytest tests/ -q` incluye
esta integración en la suite completa. Si falta, esos casos se omiten
explícitamente; si está definida pero no permite conectarse o no es PostgreSQL,
fallan sin reemplazar la base por SQLite. Las pruebas anteriores por sí solas no
acreditan exactitud de agregados ni migraciones en PostgreSQL.

### Uso del registro transaccional

El [repositorio de operaciones](src/infrastructure/database/repositories/sqlalchemy_operation_repository.py)
debe compartir la sesión de negocio: reservar antes de ejecutar efectos,
confirmar con un snapshot completo y dejar commit y rollback a la dependencia de
la petición. La propiedad se verifica con el identificador de transacción de
PostgreSQL; una reserva no puede confirmarse desde otra transacción, aunque se
reutilice la misma sesión después de un commit prematuro.

La espera de reserva y lectura se limita mediante `lock_timeout_ms`, cuyo valor
predeterminado en el adaptador es 2000 ms. Si se agota, se devuelve
`OperationUnresolvedError` y la transacción queda abortada: propagar el error para
que la dependencia haga rollback antes de recuperar o repetir la misma clave.
El repositorio no confirma ni revierte por su cuenta. El ajuste local de timeout
se restaura al completar una reserva o recuperación; ante error, se revierte con
la transacción.

Un registro confirmado con payload NULL conserva su identidad. La recuperación
de su resultado exige reconciliación y nunca habilita otro efecto de negocio;
una versión de snapshot no reconocida sigue el mismo criterio.

### Integración de comandos

El [coordinador](src/use_cases/services/idempotency.py) compone los comandos de
alta y edición con ese registro. Para usar el recorrido local, aplicar las
migraciones y configurar el entorno de desarrollo descrito arriba. Sus cabeceras,
campos opcionales y errores se consultan en OpenAPI y en los contratos de
[proyectos](src/infrastructure/http/routers/projects.py) y
[gastos](src/infrastructure/http/routers/expenses.py).

La [política de adopción](../docs/adr/0002-idempotencia-offline.md#adopción-y-límites)
define la compatibilidad cuando falta clave o identidad. La cabecera de respuesta
`Idempotency-Replayed` solo aparece en el recorrido idempotente: `false` al
ejecutarlo por primera vez y `true` al recuperar el snapshot. Su ausencia no
acredita deduplicación. Un reintento conserva clave, cuerpo e identidad; un error
de incertidumbre requiere recuperar o repetir esa misma operación.

Los comandos con clave validan los importes contra la precisión persistida sin
redondearlos; la canonicalización normaliza su escala, fechas y opcionales del
contrato. Los [metadatos de adjuntos](src/use_cases/services/canonicalization.py)
permiten extenderla a archivos verificados sin entregar binarios ni streams al
servicio. La carga de archivos corresponde a su módulo posterior.

### Consulta de recuperación

El contrato de consulta está en el [router de operaciones](src/infrastructure/http/routers/operations.py)
y los [esquemas públicos](src/infrastructure/http/schemas/operation.py), también
disponibles en OpenAPI. Usa la identidad del servidor; para la comprobación local
sirve el Dummy configurado arriba. La compatibilidad de las escrituras sin
identidad no se aplica a esta lectura.

El [caso de uso](src/use_cases/get_operation_result.py) consulta primero las
referencias para autorización y después el snapshot. El resultado usa los mismos
esquemas públicos de las escrituras y las respuestas indican `Cache-Control:
no-store`. La interpretación de una operación todavía no visible se mantiene en
el [ADR de recuperación](../docs/adr/0002-idempotencia-offline.md#recuperación-y-conservación).
