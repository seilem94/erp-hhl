# PROJECT_STATE.md (Última actualización: [Fecha])

## 📌 Estado Actual
- Fase Activa: Fase 1 (Dominio de Gastos y Proyectos)
- Último hito completado: Entidades de dominio `Expense` y `Project` definidas.
- En progreso: Creación de interfaces de repositorio (`expense_repository.py`).

## 🧱 Decisiones Técnicas Tomadas (Inmutables)
- Clean Architecture pragmática sin sobreingeniería (entidades puras sin decorators de ORM).
- IDs en UUIDv4 en lugar de enteros autoincrementales.
- SQLAlchemy 2.0 / Pydantic v2.

## 🛑 Bloqueos o Pendientes Inmediatos
- Definir si los gastos aceptan múltiples fotos de boleta o solo una URL de comprobante.
- Pendiente crear script de seed de datos para desarrollo local.

## 📋 Próximo Paso para el Agente
- Implementar el caso de uso `RegisterDailyExpenseUseCase` validando que la fecha no sea futura.