# PROJECT_STATE.md (Última actualización: [Fecha])

## 📌 Estado Actual
- **Fase Activa:** Fase 1 - Dominio de Gastos y Proyectos (Backend).
- **Rama:** `feat/backend-expense-domain`
- **Último hito completado:** Repositorio base, linters y guardrails configurados.
- **En progreso:** Definición de entidades puras (`domain/entities`) e interfaces (`domain/repositories`).


## 🧱 Decisiones Técnicas Tomadas (Inmutables)
- Clean Architecture pragmática sin sobreingeniería (entidades puras sin decorators de ORM).
- Clean Architecture estricta: `domain/` no depende de frameworks ni ORM.
- Tipado estricto verificado con Mypy y Ruff vía `.\check.ps1`.
- Identificadores con UUIDv4.
- SQLAlchemy 2.0 / Pydantic v2.

## 📋 Tarea Inmediata para el Agente
- Crear la estructura de carpetas `backend/src/domain/`.
- Definir las entidades `Expense` y `Project`.
- Definir las interfaces abstractas `ExpenseRepository` y `ProjectRepository`.

## 🛑 Bloqueos o Pendientes Inmediatos
- Definir si los gastos aceptan múltiples fotos de boleta o solo una URL de comprobante.
- Pendiente crear script de seed de datos para desarrollo local.

## 📋 Próximo Paso para el Agente
- Implementar el caso de uso `RegisterDailyExpenseUseCase` validando que la fecha no sea futura.