# Plan de Fase 2 — Persistencia y API

Responsabilidad: recorrido de implementación y mapa de infraestructura. El estado de los hitos pertenece a [PROJECT_STATE.md](PROJECT_STATE.md).

## Secuencia

1. Implementar modelos, mappers y repositorios concretos siguiendo las [reglas de arquitectura](02_reglas_arquitectura.md).
2. Configurar la conexión y el ciclo de sesión.
3. Versionar la evolución del esquema y comprobarla contra PostgreSQL.
4. Exponer los casos de uso mediante esquemas de transporte, dependencias y routers.
5. Preparar orquestación y datos semilla para el despliegue final cuando se retome ese trabajo.

## Fuentes de implementación

| Tema | Fuente |
| :--- | :--- |
| Dependencias Python | [pyproject.toml](../backend/pyproject.toml) |
| Configuración de conexión | [Settings](../backend/src/core/config.py) |
| Sesiones y transacciones | [session.py](../backend/src/infrastructure/database/session.py) |
| Esquema ORM | [models.py](../backend/src/infrastructure/database/models.py) |
| Conversión de entidades | [mappers.py](../backend/src/infrastructure/database/mappers.py) |
| Revisiones del esquema | [alembic/versions](../backend/alembic/versions/) |
| Contrato de proyectos | [Router](../backend/src/infrastructure/http/routers/projects.py) y [esquemas](../backend/src/infrastructure/http/schemas/project.py) |
| Contrato de gastos | [Router](../backend/src/infrastructure/http/routers/expenses.py) y [esquemas](../backend/src/infrastructure/http/schemas/expense.py) |
| Lecturas financieras | [Repositorio de agregación](../backend/src/infrastructure/database/repositories/sqlalchemy_financial_summary_repository.py), [router](../backend/src/infrastructure/http/routers/financial_summaries.py) y [esquemas](../backend/src/infrastructure/http/schemas/financial_summary.py) |
| Registro transaccional | [Repositorio de operaciones](../backend/src/infrastructure/database/repositories/sqlalchemy_operation_repository.py), [mappers](../backend/src/infrastructure/database/operation_mappers.py) y [snapshots persistidos](../backend/src/infrastructure/database/operation_payload.py) |
| Integración de comandos | [Coordinador](../backend/src/use_cases/services/idempotency.py), [canonicalización](../backend/src/use_cases/services/canonicalization.py) y [errores HTTP](../backend/src/infrastructure/http/schemas/operation.py) |
| Composición y OpenAPI | [main.py](../backend/src/main.py) |

No copiar aquí el catálogo de endpoints ni sus ejemplos: el contrato ejecutable y OpenAPI son la referencia. La instalación, el manejo de migraciones y las pruebas pertenecen al [README del backend](../backend/README.md).
