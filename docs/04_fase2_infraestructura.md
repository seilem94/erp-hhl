# Roadmap: Fase 2 - Infraestructura y Persistencia (PostgreSQL & FastAPI)

Esta fase implementa la capa de persistencia real en PostgreSQL (modelos ORM, mappers y repositorios concretos), la configuración de base de datos, migraciones con Alembic y la exposición de endpoints HTTP en FastAPI.

---

## 📐 Principios y Reglas de la Fase
1. **Desacoplamiento Estricto:** Las entidades del dominio (`domain/entities`) y los casos de uso (`use_cases`) se mantienen 100% agnósticas de SQLAlchemy, bases de datos o frameworks web.
2. **Aislamiento mediante Mappers:** Ningún modelo ORM (`ProjectORM`, `ExpenseORM`) se expone fuera de la capa de infraestructura. Toda lectura retorna `@dataclass` del dominio.
3. **Control Transaccional en Sesión:** Los repositorios sincronizan el estado con `session.flush()`; la confirmación (`commit()`) o reversión (`rollback()`) es gestionada automáticamente a nivel de petición en la dependencia generadora `get_db()`.
4. **Tipado Estricto:** Mypy y Ruff deben pasar sin errores en modo estricto en cada paso. Prohibido el uso de `Any`.

---

## 📋 Estado de Tareas y Pasos a Seguir

### ✅ Hito 1: Modelado y Repositorios (Completado)
- [x] **Modelos ORM:** `src/infrastructure/database/models.py` (`Base`, `ProjectORM`, `ExpenseORM`).
- [x] **Mappers Bidireccionales:** `src/infrastructure/database/mappers.py` (conversiones puras `@dataclass` ⇄ ORM).
- [x] **Repositorio de Proyectos:** `src/infrastructure/database/repositories/sqlalchemy_project_repository.py`.
- [x] **Repositorio de Gastos:** `src/infrastructure/database/repositories/sqlalchemy_expense_repository.py`.

---

### ✅ Hito 2: Conexión de Base de Datos y Dependencias (Completado)

#### Paso 1: Declaración e Instalación de Dependencias de Persistencia
- **Dependencias instaladas:** `sqlalchemy>=2.0.0`, `psycopg[binary]>=3.1.0`, `alembic>=1.13.0`, `pydantic-settings>=2.0.0`.
- **Criterio de Aceptación:** `check.ps1` valida sin conflictos en entorno virtual.

#### Paso 2: Configuración Centralizada y Conexión de Base de Datos
- `backend/src/core/config.py`: Clase `Settings` con `pydantic-settings` tipada estrictamente con `PostgresDsn`.
- `backend/src/infrastructure/database/session.py`:
  - `engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)`
  - `sessionmaker` síncrono configurado (`autocommit=False, autoflush=False`).
  - Dependencia generadora `get_db() -> Generator[Session, None, None]` con gestión transaccional automática (`try / yield / commit / rollback / close`).

---

### ✅ Hito 3: Migraciones y Pruebas de Integración (Completado)

#### Paso 3: Inicialización y Configuración de Alembic
- Configuración de `backend/alembic/env.py` enlazando metadatos y configuración dinámica de `settings`.
- Primera migración reversible generada y aplicada: `0001_create_projects_and_expenses_tables.py`.

#### Paso 4: Suite de Pruebas de Integración para Repositorios
- `backend/tests/infrastructure/test_sqlalchemy_repositories.py`: Fixture en memoria (`StaticPool`), CRUD completo de `SQLAlchemyProjectRepository` y `SQLAlchemyExpenseRepository`.

---

### ✅ Hito 4: Capa de Presentación HTTP con FastAPI (Completado)

#### Paso 5: Esquemas de Transporte (DTOs HTTP) y Manejador de Errores
- **Archivos creados:**
  - `backend/src/infrastructure/http/schemas/project.py`: `CreateProjectRequest`, `UpdateProjectRequest`, `ProjectResponse`.
  - `backend/src/infrastructure/http/schemas/expense.py`: `RegisterExpenseRequest`, `ExpenseResponse`.
  - `backend/src/infrastructure/http/schemas/error.py`: `ErrorResponse`.
  - `backend/src/infrastructure/http/error_handlers.py`: Exception handler `domain_exception_handler` para mapear `DomainException`, `ProjectNotFoundError` (404), violaciones de negocio `InvalidExpenseAmountError`, `InvalidExpenseDateError`, `ProjectCancelledError` (422) y genéricas (400).

#### Paso 6: Routers e Inyección de Dependencias
- **Archivos creados:**
  - `backend/src/use_cases/update_project.py`: `UpdateProjectDTO` y `UpdateProjectUseCase` para modificación parcial de obras (nombre, cliente, presupuesto, estado y descripción).
  - `backend/src/infrastructure/http/dependencies.py`: Factorías para repositorios (`SQLAlchemyProjectRepository`, `SQLAlchemyExpenseRepository`) y casos de uso (`CreateProjectUseCase`, `UpdateProjectUseCase`, `ListProjectsUseCase`, `RegisterDailyExpenseUseCase`, etc.) inyectando `Session` con tipado `Annotated`.
  - `backend/src/infrastructure/http/routers/projects.py`:
    - `POST /api/v1/projects` (Crear obra en estado inicial PLANNING)
    - `GET /api/v1/projects` (Listar obras, filtro por status opcional)
    - `PATCH /api/v1/projects/{project_id}` (Actualización parcial de campos de la obra)
  - `backend/src/infrastructure/http/routers/expenses.py`:
    - `POST /api/v1/expenses` (Registrar gasto diario en terreno o de obra)
    - `GET /api/v1/expenses/project/{project_id}` (Consultar gastos directos CapEx de una obra)
    - `GET /api/v1/expenses/operational` (Consultar gastos operativos OPEX)
  - `backend/src/main.py`: Configuración de la aplicación FastAPI, middlewares (CORS), documentación OpenAPI 100% en español y montaje de routers.
  - `backend/tests/infrastructure/test_http_api.py`: 12 pruebas de integración con `TestClient`.

---

### ⏸️ Hito 5: Entorno Docker Local y Datos Semilla (En pausa temporal)
> **Nota de estado:** Pausado temporalmente por decisión técnica del usuario. Para el desarrollo actual se utiliza PostgreSQL nativo instalado localmente. Este hito se retomará al preparar el despliegue al servidor de producción final (Debian).

#### Paso 7: Docker Compose y Script de Seed (Pendiente para producción)
- **Archivos a crear:**
  - `docker-compose.yml`: Servicio `postgres:16-alpine` con healthcheck, volumen `postgres_data` y red interna.
  - `backend/scripts/seed.py`: Script para cargar datos iniciales de prueba (proyectos ficticios y gastos representativos de obras eléctricas).
