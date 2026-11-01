# Roadmap: Fase 1 - Dominio de Gastos y Proyectos

Esta fase se centra exclusivamente en el backend (Domain y Use Cases) para los módulos críticos.
No implementar controladores HTTP ni base de datos real hasta que el dominio esté completo.

## Tareas Secuenciales para el Agente:
1. [x] Crear `domain/entities/expense.py` y `domain/entities/project.py` usando Pydantic/Dataclasses.
2. [x] Crear las interfaces abstractas `domain/repositories/expense_repository.py` y `project_repository.py`.
3. [x] Implementar la lógica de negocio en `use_cases/register_daily_expense.py` (debe validar que el proyecto exista y registrar el gasto).
4. [x] Implementar un repositorio en memoria (`tests/fakes.py`) para probar los casos de uso sin PostgreSQL.
5. [ ] Implementar casos de uso de consulta (gastos por proyecto y gastos operacionales) antes de infraestructura.
