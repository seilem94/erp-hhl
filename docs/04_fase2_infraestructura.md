# Roadmap: Fase 2 - Infraestructura y Persistencia (PostgreSQL & FastAPI)

Esta fase implementa la capa de persistencia real en PostgreSQL (modelos ORM, mappers y repositorios concretos), la configuración de base de datos, migraciones con Alembic y la exposición de endpoints HTTP en FastAPI.

---

## 📐 Principios y Reglas de la Fase
1. **Desacoplamiento Estricto:** Las entidades del dominio (`domain/entities`) y los casos de uso (`use_cases`) se mantienen 100% agnósticas de SQLAlchemy, bases de datos o frameworks web.
2. **Aislamiento mediante Mappers:** Ningún modelo ORM (`ProjectORM`, `ExpenseORM`) se expone fuera de la capa de infraestructura. Toda lectura retorna `@dataclass` del dominio.
3. **Control Transaccional Externo:** Los repositorios sincronizan el estado con `session.flush()`; el `commit()` o `rollback()` es responsabilidad exclusiva del llamador (Unit of Work, middleware o dependencia de FastAPI).
4. **Tipado Estricto:** Mypy y Ruff deben pasar sin errores en modo estricto en cada paso. Prohibido el uso de `Any`.

---

## 📋 Estado de Tareas y Pasos a Seguir

### ✅ Hito 1: Modelado y Repositorios (Completado)
- [x] **Modelos ORM:** `src/infrastructure/database/models.py` (`Base`, `ProjectORM`, `ExpenseORM`).
- [x] **Mappers Bidireccionales:** `src/infrastructure/database/mappers.py` (conversiones puras `@dataclass` ⇄ ORM).
- [x] **Repositorio de Proyectos:** `src/infrastructure/database/repositories/sqlalchemy_project_repository.py`.
- [x] **Repositorio de Gastos:** `src/infrastructure/database/repositories/sqlalchemy_expense_repository.py`.

---

### ⏳ Hito 2: Conexión de Base de Datos y Dependencias (Siguiente Paso Inmediato)

#### Paso 1: Declaración e Instalación de Dependencias de Persistencia
- **Acción:** Declarar en `backend/pyproject.toml` las dependencias requeridas e instalarlas en el entorno virtual (requiere autorización explícita según `AGENT.md`):
  - `sqlalchemy>=2.0.0`
  - `psycopg[binary]>=3.1.0` (driver PostgreSQL nativo y moderno)
  - `alembic>=1.13.0` (gestión de migraciones)
  - `pydantic-settings>=2.0.0` (gestión de configuración por variables de entorno)
- **Criterio de Aceptación:** `pip list` en `backend/venv` confirma la instalación y `check.ps1` valida sin conflictos.

#### Paso 2: Configuración Centralizada y Conexión de Base de Datos
- **Archivos a crear/modificar:**
  - `backend/.env.example` y `backend/.env`: Definir `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/erp_hhl` y variables de entorno.
  - `backend/src/core/config.py`: Clase `Settings` con `pydantic-settings` tipada estrictamente.
  - `backend/src/infrastructure/database/session.py`:
    - `engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)`
    - `sessionmaker` síncrono configurado (`autocommit=False, autoflush=False`).
    - Dependencia generadora `get_db() -> Generator[Session, None, None]` con gestión de `try / yield / commit / rollback / close` para inyectar en FastAPI.
- **Criterio de Aceptación:** Conexión probada con engine y sesión transaccional segura.

---

### ⏳ Hito 3: Migraciones y Pruebas de Integración

#### Paso 3: Inicialización y Configuración de Alembic
- **Acción:**
  - Inicializar entorno de migraciones con `alembic init -t generic backend/alembic`.
  - Configurar `backend/alembic/env.py` para enlazar `target_metadata = Base.metadata` desde `src.infrastructure.database.models` y la URL dinámica desde `src.core.config.settings`.
  - Generar la primera migración automática: `0001_create_projects_and_expenses_tables.py`.
- **Criterio de Aceptación:** Migración reversible que crea las tablas `projects` y `expenses` con llaves foráneas e índices apropiados.

#### Paso 4: Suite de Pruebas de Integración para Repositorios
- **Archivo a crear:** `backend/tests/infrastructure/test_sqlalchemy_repositories.py`.
- **Acción:**
  - Configurar fixture de base de datos en memoria (SQLite con `StaticPool` o Postgres temporal) ejecutando `Base.metadata.create_all`.
  - Probar `SQLAlchemyProjectRepository` (crear, actualizar, listar por estado, eliminar).
  - Probar `SQLAlchemyExpenseRepository` (gasto de proyecto con FK, gasto OPEX sin proyecto, filtros de rango de fechas).
- **Criterio de Aceptación:** 100% de tests pasando en pytest, cubriendo tanto inserciones válidas como restricciones relacionales.

---

### ⏳ Hito 4: Capa de Presentación HTTP con FastAPI

#### Paso 5: Esquemas de Transporte (DTOs HTTP) y Manejador de Errores
- **Archivos a crear:**
  - `backend/src/infrastructure/http/schemas/project.py`: `CreateProjectRequest`, `ProjectResponse`.
  - `backend/src/infrastructure/http/schemas/expense.py`: `RegisterExpenseRequest`, `ExpenseResponse`.
  - `backend/src/infrastructure/http/error_handlers.py`: Exception handlers para mapear `DomainException`, `ProjectNotFoundException`, `InvalidExpenseDateException`, etc. a respuestas JSON HTTP (400, 404, 422).

#### Paso 6: Routers e Inyección de Dependencias
- **Archivos a crear:**
  - `backend/src/infrastructure/http/dependencies.py`: Factorías para instanciar repositorios y casos de uso inyectando `Session`.
  - `backend/src/infrastructure/http/routers/projects.py`:
    - `POST /api/v1/projects` (Crear obra)
    - `GET /api/v1/projects` (Listar obras, filtro por status opcional)
  - `backend/src/infrastructure/http/routers/expenses.py`:
    - `POST /api/v1/expenses` (Registrar gasto diario en terreno o de obra)
    - `GET /api/v1/projects/{project_id}/expenses` (Consultar gastos de una obra)
    - `GET /api/v1/expenses/operational` (Consultar gastos OPEX)
  - `backend/src/main.py`: Configuración de la aplicación FastAPI, middlewares (CORS) y montaje de routers.
- **Criterio de Aceptación:** Documentación Swagger interactiva accesible en `/docs` y endpoints testeados con `httpx.AsyncClient` o `TestClient`.

---

### ⏳ Hito 5: Entorno Docker Local y Datos Semilla

#### Paso 7: Docker Compose y Script de Seed
- **Archivos a crear:**
  - `docker-compose.yml`: Servicio `postgres:16-alpine` con healthcheck, volumen `postgres_data` y red interna.
  - `backend/scripts/seed.py`: Script para cargar datos iniciales de prueba (proyectos ficticios y gastos representativos de obras eléctricas).
