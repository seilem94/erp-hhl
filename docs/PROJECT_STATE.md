# PROJECT_STATE.md (Última actualización: 2026-11-01)

## 📌 Estado Actual
- **Fase Activa:** Fase 1 - Dominio de Gastos y Proyectos (Backend).
- **Rama:** `feat/backend-expense-domain`
- **Último hito completado:** Implementación completa del caso de uso de registro de gastos y su suite de pruebas unitarias:
  - Excepciones de dominio en `domain/exceptions.py` (`DomainException`, `ProjectNotFoundError`, `ProjectCancelledError`, `InvalidExpenseDateError`, `InvalidExpenseAmountError`).
  - DTO inmutable `RegisterDailyExpenseDTO` y caso de uso `RegisterDailyExpenseUseCase` en `use_cases/register_daily_expense.py`.
  - Repositorios en memoria (`tests/fakes.py`: `InMemoryExpenseRepository`, `InMemoryProjectRepository`).
  - Suite de 9 pruebas unitarias con `pytest` en `tests/use_cases/test_register_daily_expense.py` (100% passing).
  - Validación estricta con Ruff, Mypy y Pytest pasando limpio (0 errores).
- **En progreso:** Definición de siguientes casos de uso del módulo de gastos (consultas/listados) o transición a capa de infraestructura.

## 🧱 Decisiones Técnicas Tomadas (Inmutables)
- Clean Architecture pragmática sin sobreingeniería (entidades puras sin decorators de ORM).
- Clean Architecture estricta: `domain/` y `use_cases/` no dependen de frameworks ni ORM (uso de `@dataclass` nativo).
- Tipado estricto verificado con Mypy y Ruff vía `.\check.ps1` (prohibido `Any`/`any`).
- Identificadores con UUIDv4.
- Soporte de Gastos Operacionales (OPEX): `Expense.project_id: UUID | None = None` y propiedad `is_project_expense -> bool`.
- Manejo de comprobantes: `has_receipt: bool` y `receipt_url: str | None`. Si se suministra `receipt_url`, se normaliza automáticamente `has_receipt = True`.
- Regla de negocio para proyectos en gastos: Se permiten gastos rezagados en proyectos `COMPLETED`. Solo se rechaza el registro si el proyecto está en estado `CANCELLED`.
- Desacoplamiento temporal: Inyección de `date_provider: Callable[[], date] = date.today` en casos de uso para testing unitario determinista sin monkeypatching.
- Tests unitarios aislados con `pytest` usando fakes en memoria (`tests/fakes.py`) sin bases de datos ni I/O.
- SQLAlchemy 2.0 / Pydantic v2 (reservados para capas de infraestructura/API).

## 📋 Tareas de la Fase 1
- [x] Crear entidades de dominio (`Expense`, `Project`) y enums.
- [x] Crear interfaces abstractas de repositorios (`ExpenseRepository`, `ProjectRepository`).
- [x] Crear excepciones de dominio (`DomainException` y subtipos).
- [x] Implementar el caso de uso `RegisterDailyExpenseUseCase` y su DTO.
- [x] Implementar repositorios en memoria (`tests/fakes.py`) y suite de tests con `pytest`.
- [ ] Definir casos de uso de consulta (ej. listar gastos por proyecto y OPEX).

## 🛑 Bloqueos o Pendientes Inmediatos
- **Resuelto:** Decisión sobre comprobantes (normalización automática si hay URL).
- **Resuelto:** Regla sobre obras completadas (gastos rezagados permitidos).
- **Resuelto:** Implementación de repositorios en memoria para testing (`tests/fakes.py`).
- **Pendiente:** Definir si se implementan casos de uso de lectura antes de pasar a la base de datos real.
- **Pendiente:** Script de seed de datos para desarrollo local (Fase 2).

## 📋 Próximo Paso para el Agente
- Implementar casos de uso de consulta de gastos o proceder a la capa de infraestructura (repositorios PostgreSQL/SQLAlchemy).
