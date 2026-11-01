# PROJECT_STATE.md (Última actualización: 2026-11-01)

## 📌 Estado Actual
- **Fase Activa:** Fase 1 - Dominio de Gastos y Proyectos (Backend).
- **Rama:** `feat/backend-projects-domain`
- **Último hito completado:** Implementación completa de los casos de uso del dominio de proyectos y su suite de pruebas unitarias:
  - Interfaz abstracta `ProjectRepository` actualizada con el método `list_by_status(status: ProjectStatus) -> list[Project]`.
  - DTO inmutable `CreateProjectDTO` y caso de uso `CreateProjectUseCase` en `use_cases/create_project.py` (id generado con uuid4, status inicial `PLANNING`, fechas en UTC, persistencia vía repositorio).
  - Caso de uso `ListProjectsUseCase` en `use_cases/list_projects.py` (listado total o filtrado por `ProjectStatus`).
  - Actualización de repositorio en memoria `InMemoryProjectRepository` (`tests/fakes.py`) con soporte para `list_by_status`.
  - Suite de 18 pruebas unitarias con `pytest` en `tests/use_cases/test_projects.py` (100% passing).
  - Suite global de backend con 32 pruebas unitarias pasando.
  - Validación estricta con Ruff, Mypy y Pytest pasando limpio (0 errores en `check.ps1`).
- **En progreso:** Transición a la capa de infraestructura (persistencia PostgreSQL con SQLAlchemy 2.0 y migraciones con Alembic).

## 🧱 Decisiones Técnicas Tomadas (Inmutables)
- Clean Architecture pragmática sin sobreingeniería (entidades puras sin decorators de ORM).
- Clean Architecture estricta: `domain/` y `use_cases/` no dependen de frameworks ni ORM (uso de `@dataclass` nativo).
- Tipado estricto verificado con Mypy y Ruff vía `.\check.ps1` (prohibido `Any`/`any`).
- Identificadores con UUIDv4 generados a nivel de caso de uso.
- Proyectos inician siempre en estado `PLANNING` con timestamps `created_at` y `updated_at` en UTC (`datetime.now(UTC)`).
- Soporte de Gastos Operacionales (OPEX): `Expense.project_id: UUID | None = None` y propiedad `is_project_expense -> bool`.
- Manejo de comprobantes: `has_receipt: bool` y `receipt_url: str | None`. Si se suministra `receipt_url`, se normaliza automáticamente `has_receipt = True`.
- Regla de negocio para proyectos en gastos: Se permiten gastos rezagados en proyectos `COMPLETED`. Solo se rechaza el registro si el proyecto está en estado `CANCELLED`.
- Desacoplamiento temporal: Inyección de `date_provider: Callable[[], date] = date.today` en casos de uso que requieran determinismo de fecha.
- Tests unitarios aislados con `pytest` usando fakes en memoria (`tests/fakes.py`) sin bases de datos ni I/O.
- SQLAlchemy 2.0 / Pydantic v2 (reservados para capas de infraestructura/API).

## 📋 Tareas de la Fase 1
- [x] Crear entidades de dominio (`Expense`, `Project`) y enums.
- [x] Crear interfaces abstractas de repositorios (`ExpenseRepository`, `ProjectRepository`).
- [x] Crear excepciones de dominio (`DomainException` y subtipos).
- [x] Implementar el caso de uso `RegisterDailyExpenseUseCase` y su DTO.
- [x] Implementar repositorios en memoria (`tests/fakes.py`) y suite de tests con `pytest`.
- [x] Implementar casos de uso de consulta de gastos (`GetProjectExpensesUseCase`, `GetOperationalExpensesUseCase`).
- [x] Implementar casos de uso de proyectos (`CreateProjectUseCase`, `ListProjectsUseCase`) y tests unitarios.

## 🛑 Bloqueos o Pendientes Inmediatos
- **Resuelto:** Decisión sobre comprobantes (normalización automática si hay URL).
- **Resuelto:** Regla sobre obras completadas (gastos rezagados permitidos).
- **Resuelto:** Repositorios en memoria y casos de uso del dominio completos para gastos y proyectos.
- **Pendiente:** Configuración de base de datos PostgreSQL, modelos SQLAlchemy y migraciones Alembic (Fase 2).
- **Pendiente:** Script de seed de datos para desarrollo local (Fase 2).

## 📋 Próximo Paso para el Agente
- Proceder a la capa de infraestructura (modelos SQLAlchemy 2.0, mapeadores entidad-modelo y repositorios PostgreSQL para proyectos y gastos).
