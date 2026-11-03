# PROJECT_STATE.md (Última actualización: 2026-11-02)

## 📌 Estado Actual
- **Fase Activa:** Fase 2 - Infraestructura y Persistencia (Backend).
- **Rama:** `feat/backend-projects-domain`
- **Últimos hitos completados:**
  - **Hito 1 (Modelado y Repositorios):** Modelos ORM (`ProjectORM`, `ExpenseORM`), mappers bidireccionales puros (`mappers.py`) y repositorios concretos (`SQLAlchemyProjectRepository`, `SQLAlchemyExpenseRepository`).
  - **Hito 2 (Configuración y Dependencias):** Declaración e instalación de dependencias en `pyproject.toml` (`sqlalchemy`, `psycopg[binary]`, `alembic`, `pydantic-settings`), configuración centralizada con `pydantic-settings` (`src/core/config.py`) y sesión de base de datos con factoría y dependencia generadora `get_db` (`src/infrastructure/database/session.py`).
  - **Hito 3 (Migraciones y Pruebas de Integración):**
    - Configuración de Alembic y generación de la primera migración de esquema (`0001_create_projects_and_expenses_tables.py`).
    - Suite completa de pruebas de integración en `tests/infrastructure/test_sqlalchemy_repositories.py` (65 tests pasando).
  - **Hito 4 (Capa de Presentación HTTP con FastAPI):**
    - Esquemas Pydantic v2 DTO en `src/infrastructure/http/schemas/`: `CreateProjectRequest`, `ProjectResponse`, `RegisterExpenseRequest`, `ExpenseResponse` con `model_config = ConfigDict(from_attributes=True)` para serialización directa desde dataclasses de dominio.
    - Manejador global de excepciones en `src/infrastructure/http/error_handlers.py`: `domain_exception_handler` mapeando `ProjectNotFoundError` a 404, validaciones de negocio (`InvalidExpenseAmountError`, `InvalidExpenseDateError`, `ProjectCancelledError`) a 422 y `DomainException` genéricas a 400.
    - Inyección de dependencias en `src/infrastructure/http/dependencies.py`: factorías para repositorios (`get_project_repo`, `get_expense_repo`) y casos de uso (`get_create_project_uc`, `get_list_projects_uc`, `get_register_expense_uc`, `get_project_expenses_uc`, `get_operational_expenses_uc`) utilizando `typing.Annotated`.
    - Routers modulares en `src/infrastructure/http/routers/`:
      - `routers/projects.py`: `POST /api/v1/projects` (201) y `GET /api/v1/projects` (filtro por status opcional).
      - `routers/expenses.py`: `POST /api/v1/expenses` (201), `GET /api/v1/expenses/project/{project_id}` y `GET /api/v1/expenses/operational`.
      - Desacoplamiento total: los routers ejecutan exclusivamente casos de uso sin tocar base de datos ni ORM directamente.
    - Aplicación FastAPI principal en `src/main.py`: middleware CORS permisivo para desarrollo local, registro de manejador de excepciones de dominio, montaje de routers y endpoint `GET /health`.
    - Documentación OpenAPI/Swagger/ReDoc 100% en español:
      - Esquema `ErrorResponse` en `schemas/error.py` para tipar respuestas de error (`{"detail": "..."}`).
      - Declaración explícita de códigos de respuesta HTTP en cada endpoint (`200`, `201`, `400`, `404`, `422`).
      - Descripciones, resúmenes, parámetros y ejemplos de campos en español para facilitar pruebas e integración con frontend.
    - Suite de pruebas de integración HTTP en `tests/infrastructure/test_http_api.py` (10 tests con `TestClient` sobre fakes en memoria).
  - Validación completa con `check.ps1`: Ruff check/format limpio (48 archivos), Mypy estricto sin errores (37 archivos) y 75 tests de Pytest pasando al 100%.
- **En progreso:** Hito 5 - Entorno Docker Local y Datos Semilla (`docker-compose.yml`, `backend/scripts/seed.py`).

## 🧱 Decisiones Técnicas Tomadas (Inmutables)
- Clean Architecture pragmática sin sobreingeniería (entidades puras sin decorators de ORM).
- Clean Architecture estricta: `domain/` y `use_cases/` no dependen de frameworks ni ORM (uso de `@dataclass` nativo).
- Tipado estricto verificado con Mypy y Ruff vía `.\check.ps1` (prohibido `Any`/`any`).
- Identificadores con UUIDv4 generados a nivel de caso de uso.
- Proyectos inician siempre en estado `PLANNING` con timestamps `created_at` y `updated_at` en UTC (`datetime.now(UTC)`).
- Soporte de Gastos Operacionales (OPEX): `Expense.project_id: UUID | None = None` y propiedad `is_project_expense -> bool`. En base de datos, `ForeignKey("projects.id", ondelete="SET NULL", nullable=True)`.
- Manejo de comprobantes: `has_receipt: bool` y `receipt_url: str | None`. Si se suministra `receipt_url`, se normaliza automáticamente `has_receipt = True`.
- Regla de negocio para proyectos en gastos: Se permiten gastos rezagados en proyectos `COMPLETED`. Solo se rechaza el registro si el proyecto está en estado `CANCELLED`.
- Desacoplamiento temporal: Inyección de `date_provider: Callable[[], date] = date.today` en casos de uso que requieran determinismo de fecha.
- Tests unitarios aislados con `pytest` usando fakes en memoria (`tests/fakes.py`) sin bases de datos ni I/O.
- SQLAlchemy 2.0 / Pydantic v2 (reservados para capas de infraestructura/API).
- Los repositorios de infraestructura reciben `Session` en constructor, aplican `flush()` para sincronización y nunca realizan `commit()`.
- Prohibición de filtrado de modelos ORM: todo dato saliente de los repositorios de infraestructura pasa obligatoriamente por `mappers.py` retornando `@dataclass` puro del dominio.
- Los routers HTTP ejecutan exclusivamente casos de uso mediante inyección de dependencias `Depends()` y no acceden directamente a la base de datos ni a los repositorios.

## 📋 Tareas de la Fase 1 y Fase 2
- [x] Crear entidades de dominio (`Expense`, `Project`) y enums.
- [x] Crear interfaces abstractas de repositorios (`ExpenseRepository`, `ProjectRepository`).
- [x] Crear excepciones de dominio (`DomainException` y subtipos).
- [x] Implementar el caso de uso `RegisterDailyExpenseUseCase` y su DTO.
- [x] Implementar repositorios en memoria (`tests/fakes.py`) y suite de tests con `pytest`.
- [x] Implementar casos de uso de consulta de gastos (`GetProjectExpensesUseCase`, `GetOperationalExpensesUseCase`).
- [x] Implementar casos de uso de proyectos (`CreateProjectUseCase`, `ListProjectsUseCase`) y tests unitarios.
- [x] Hito 1 (Infraestructura): Modelos ORM SQLAlchemy 2.0 (`ProjectORM`, `ExpenseORM`) en `infrastructure/database/models.py`.
- [x] Hito 1 (Infraestructura): Mappers bidireccionales puros en `infrastructure/database/mappers.py`.
- [x] Hito 1 (Infraestructura): Repositorios PostgreSQL `SQLAlchemyProjectRepository` y `SQLAlchemyExpenseRepository`.
- [x] Hito 2: Declaración e instalación de dependencias de persistencia (`sqlalchemy`, `psycopg[binary]`, `alembic`, `pydantic-settings`).
- [x] Hito 2: Configuración centralizada (`src/core/config.py`) y sesión de base de datos (`src/infrastructure/database/session.py`).
- [x] Hito 3: Inicialización y primera migración con Alembic.
- [x] Hito 3: Suite de pruebas de integración para repositorios SQLAlchemy (`tests/infrastructure/`).
- [x] Hito 4: Esquemas DTO de transporte, exception handlers y routers de FastAPI (`projects`, `expenses`).
- [ ] Hito 5: Docker Compose para PostgreSQL local y script de seed (`scripts/seed.py`).

## 🛑 Bloqueos o Pendientes Inmediatos
- Ninguno. Hitos 1 al 4 de la Fase 2 completados y validados.
- **Pendiente:** Implementar Hito 5 (Entorno Docker Local y Datos Semilla).

## 📋 Próximo Paso para el Agente
- Ejecutar el Hito 5: Configurar `docker-compose.yml` con servicio `postgres:16-alpine`, healthcheck y red interna, y desarrollar el script de inicialización de datos de prueba (`backend/scripts/seed.py`).
