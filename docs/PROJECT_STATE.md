# PROJECT_STATE.md (Última actualización: 2026-11-01)

## 📌 Estado Actual
- **Fase Activa:** Fase 1 - Dominio de Gastos y Proyectos (Backend).
- **Rama:** `feat/backend-expense-domain`
- **Último hito completado:** Definición e implementación completa de la capa de Dominio (`backend/src/domain/`):
  - Enums (`ProjectStatus`, `ExpenseCategory` con categoría `MAINTENANCE`).
  - Entidades con `@dataclass` puro (`Project`, `Expense` con soporte de costos de obra y OPEX).
  - Interfaces de repositorios abstractos (`ProjectRepository`, `ExpenseRepository` con `get_operational_expenses`).
  - Validación estricta con Ruff y Mypy pasando limpio (0 errores).
- **En progreso:** Implementación de Casos de Uso (`backend/src/use_cases/`).


## 🧱 Decisiones Técnicas Tomadas (Inmutables)
- Clean Architecture pragmática sin sobreingeniería (entidades puras sin decorators de ORM).
- Clean Architecture estricta: `domain/` no depende de frameworks ni ORM (uso de `@dataclass` nativo).
- Tipado estricto verificado con Mypy y Ruff vía `.\check.ps1` (prohibido `Any`/`any`).
- Identificadores con UUIDv4.
- Soporte de Gastos Operacionales (OPEX): `Expense.project_id: UUID | None = None` y propiedad `is_project_expense -> bool`.
- Manejo de comprobantes en MVP: `has_receipt: bool` y `receipt_url: str | None` (1 comprobante por gasto).
- SQLAlchemy 2.0 / Pydantic v2 (en capas externas cuando aplique).

## 📋 Tarea Inmediata para el Agente
- Crear la estructura de carpetas `backend/src/use_cases/`.
- Implementar el caso de uso `RegisterDailyExpenseUseCase` (validando monto > 0, fecha no futura `date <= today()`, y existencia de proyecto si `is_project_expense`).
- Implementar excepciones de dominio/aplicación (`ProjectNotFoundError`, `InvalidExpenseDataError`, etc.).

## 🛑 Bloqueos o Pendientes Inmediatos
- **Resuelto:** Decisión sobre comprobantes (resuelto: 1 URL de comprobante opcional en MVP).
- **Pendiente:** Implementar repositorio en memoria (`in_memory_expense_repo.py` e `in_memory_project_repo.py`) para pruebas unitarias de casos de uso sin base de datos real.
- **Pendiente:** Script de seed de datos para desarrollo local (Fase 2).

## 📋 Próximo Paso para el Agente
- Implementar `RegisterDailyExpenseUseCase` y sus tests unitarios / repositorio en memoria.
