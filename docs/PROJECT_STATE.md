# PROJECT_STATE.md (Última actualización: 2026-11-02)

## 📌 Estado Actual
- **Fase Activa:** Fase 2 - Infraestructura y Persistencia (Backend).
- **Rama:** `feat/backend-projects-domain`
- **Último hito completado:** Implementación de la capa de persistencia PostgreSQL (SQLAlchemy 2.0) sin acoplar el dominio:
  - Modelos ORM en `src/infrastructure/database/models.py`:
    - `Base(DeclarativeBase)` como base compartida tipada para SQLAlchemy 2.0.
    - `ProjectORM` (`projects`): Mapeo con `Mapped` y `mapped_column` para identificador UUID, atributos de texto, fechas, timestamps UTC y presupuesto (`Numeric(12, 2)`).
    - `ExpenseORM` (`expenses`): Mapeo con clave foránea a `projects.id` (`nullable=True`, `ondelete="SET NULL"`) para soportar gastos operativos (OPEX) y costos directos de obra (CapEx).
  - Funciones puras de mapeo bidireccional en `src/infrastructure/database/mappers.py`:
    - `project_to_domain(orm: ProjectORM) -> Project` y `domain_to_project_orm(project: Project) -> ProjectORM`.
    - `expense_to_domain(orm: ExpenseORM) -> Expense` y `domain_to_expense_orm(expense: Expense) -> ExpenseORM`.
    - Traducción segura entre `StrEnum` de dominio (`ProjectStatus`, `ExpenseCategory`) y cadenas de texto en persistencia.
  - Repositorios concretos de PostgreSQL en `src/infrastructure/database/repositories/`:
    - `SQLAlchemyProjectRepository` (`sqlalchemy_project_repository.py`): Implementa `ProjectRepository` (`save`, `update`, `delete`, `get_by_id`, `list_all`, `list_by_status`).
    - `SQLAlchemyExpenseRepository` (`sqlalchemy_expense_repository.py`): Implementa `ExpenseRepository` (`save`, `delete`, `get_by_id`, `list_all`, `get_by_project`, `get_operational_expenses`).
    - Todos los métodos de lectura devuelven entidades `@dataclass` puras del dominio vía mappers; los modelos ORM nunca se exponen al exterior.
    - Ciclo de vida transaccional delegado: los repositorios ejecutan `session.flush()` para materializar identidades sin hacer `commit()`, delegando el control de la transacción al llamador (UoW / middleware / FastAPI dependency).
  - Validación estricta con `check.ps1` limpia (Ruff check/format, Mypy en 23 archivos y 32 tests de Pytest pasando).
- **En progreso:** Configuración de conexión de base de datos (engine/sessionmaker), migraciones con Alembic y exposición de endpoints API en FastAPI.

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
- [ ] Hito 2: Declaración e instalación de dependencias de persistencia (`sqlalchemy`, `psycopg[binary]`, `alembic`, `pydantic-settings`).
- [ ] Hito 2: Configuración centralizada (`src/core/config.py`) y sesión de base de datos (`src/infrastructure/database/session.py`).
- [ ] Hito 3: Inicialización y primera migración con Alembic.
- [ ] Hito 3: Suite de pruebas de integración para repositorios SQLAlchemy (`tests/infrastructure/`).
- [ ] Hito 4: Esquemas DTO de transporte, exception handlers y routers de FastAPI (`projects`, `expenses`).
- [ ] Hito 5: Docker Compose para PostgreSQL local y script de seed (`scripts/seed.py`).

## 🛑 Bloqueos o Pendientes Inmediatos
- **Pendiente de Autorización:** Instalación de librerías (`sqlalchemy`, `psycopg[binary]`, `alembic`, `pydantic-settings`) en `backend/pyproject.toml` según protocolo de autonomía en `AGENT.md`.
- **Pendiente:** Creación de `src/core/config.py` y `src/infrastructure/database/session.py`.
- **Pendiente:** Inicialización de migraciones Alembic y suite de tests de integración.

## 📋 Próximo Paso para el Agente
- Solicitar autorización para declarar e instalar las dependencias de persistencia (`sqlalchemy`, `psycopg[binary]`, `alembic`, `pydantic-settings`), para luego implementar la configuración de base de datos (`session.py` y `config.py`) y Alembic. Consultar `docs/04_fase2_infraestructura.md` para el desglose detallado.
