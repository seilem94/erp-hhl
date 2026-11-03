# PROJECT_STATE.md (Última actualización: 2026-11-02)

## 📌 Estado Actual
- **Fase Activa:** Fase 2 - Infraestructura y Persistencia (Backend).
- **Rama:** `feat/backend-projects-domain`
- **Último hito completado:**
  - **Hito 1 (Modelado y Repositorios):** Modelos ORM (`ProjectORM`, `ExpenseORM`), mappers bidireccionales puros (`mappers.py`) y repositorios concretos (`SQLAlchemyProjectRepository`, `SQLAlchemyExpenseRepository`).
  - **Hito 2 (Configuración y Dependencias):** Declaración e instalación de dependencias en `pyproject.toml` (`sqlalchemy`, `psycopg[binary]`, `alembic`, `pydantic-settings`), configuración centralizada con `pydantic-settings` (`src/core/config.py`) y sesión de base de datos con factoría y dependencia generadora `get_db` (`src/infrastructure/database/session.py`).
  - **Hito 3 (Migraciones y Pruebas de Integración):**
    - Configuración de Alembic y generación de la primera migración de esquema (`0001_create_projects_and_expenses_tables.py`).
    - Suite completa de pruebas de integración en `tests/infrastructure/test_sqlalchemy_repositories.py`:
      - Fixture de SQLite en memoria (`StaticPool`) con aislamiento transaccional por test.
      - CRUD completo para `SQLAlchemyProjectRepository` (guardar, actualizar, listar todo, filtrar por estado, obtener por ID, eliminar).
      - Cobertura exhaustiva para `SQLAlchemyExpenseRepository` (gastos directos CapEx con FK a proyectos, gastos operacionales OPEX con `project_id = None`, filtros de rango de fechas, listar todo y eliminar).
      - Verificación rigurosa de aislamiento arquitectónico: 100% de los métodos retornan entidades `@dataclass` puras del dominio y nunca exponen modelos ORM.
  - Validación completa y limpia con `check.ps1`: Ruff check/format sin incidencias, Mypy estricto sin errores (26 archivos) y 65 tests de Pytest pasando al 100%.
- **En progreso:** Hito 4 - Capa de presentación HTTP con FastAPI (Esquemas DTO de transporte, Exception Handlers, dependencias y routers para `projects` y `expenses`).

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
- [ ] Hito 4: Esquemas DTO de transporte, exception handlers y routers de FastAPI (`projects`, `expenses`).
- [ ] Hito 5: Docker Compose para PostgreSQL local y script de seed (`scripts/seed.py`).

## 🛑 Bloqueos o Pendientes Inmediatos
- Ninguno en persistencia ni infraestructura de base de datos.
- **Pendiente:** Implementar Hito 4 (Capa de presentación HTTP con FastAPI).

## 📋 Próximo Paso para el Agente
- Ejecutar el Hito 4: Desarrollar esquemas Pydantic DTO (`CreateProjectRequest`, `ProjectResponse`, `RegisterExpenseRequest`, `ExpenseResponse`), manejadores globales de excepciones (`error_handlers.py`), dependencias de inyección (`dependencies.py`) y routers FastAPI para proyectos y gastos en `src/infrastructure/http/`.
