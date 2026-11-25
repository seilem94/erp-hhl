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
| Recuperación autorizada | [Caso de uso](../backend/src/use_cases/get_operation_result.py), [router](../backend/src/infrastructure/http/routers/operations.py) y [esquemas](../backend/src/infrastructure/http/schemas/operation.py) |
| Composición y OpenAPI | [main.py](../backend/src/main.py) |

El contrato ejecutable y OpenAPI definen los cuerpos, parámetros y respuestas completos. La instalación, el manejo de migraciones y las pruebas pertenecen al [README del backend](../backend/README.md).

## Persistencia de la bitácora

El modelo `AuditLogORM` de la [capa de persistencia](../backend/src/infrastructure/database/models.py) representa la tabla `audit_logs`. La [revisión Alembic `3845a60b9d12`](../backend/alembic/versions/3845a60b9d12_crear_bitacora_de_auditoria.py), sucesora de `b528c7394d01`, crea la tabla y sus índices. Su reversión elimina la tabla y los eventos almacenados en ella.

Cada evento tiene un `id` UUID, un `created_at` con zona horaria y un `actor_email` obtenido según la [atribución de Cloudflare Access](08_infraestructura_y_despliegue.md#cloudflare-tunnel-y-zero-trust). `entidad` y `entidad_id` identifican el proyecto o gasto afectado. `proyecto_id` es una clave foránea nullable a `projects.id` con `ON DELETE SET NULL`, lo que conserva el evento al borrar la obra.

El servicio de auditoría registra cada evento en la misma transacción que la escritura del repositorio de proyectos o gastos. `accion` identifica el tipo como `CREATE`, `UPDATE` o `DELETE`. Cada evento tiene un `resumen` en español y un JSONB `detalles` con `antes` y `despues`. En altas y borrados se guarda el snapshot disponible. En ediciones se guardan solo los campos que cambiaron. La bitácora comienza con las escrituras posteriores a la migración. [Servicio de auditoría](../backend/src/use_cases/services/audit_service.py).

## Contratos de proyectos, gastos y auditoría

- **Proyectos.** El alta en `POST /api/v1/projects/` admite `description`, `status`, `start_date` y `end_date` como opcionales junto a `estimated_budget`. Cuando se omiten el estado y la fecha de inicio, el servidor usa `planning` y el día actual en UTC. `PATCH /api/v1/projects/{project_id}` admite `description`. Las fechas se establecen en el alta. [Router de proyectos](../backend/src/infrastructure/http/routers/projects.py) y [esquemas de proyectos](../backend/src/infrastructure/http/schemas/project.py).
- **Gastos.** `PATCH /api/gastos/{expense_id}` comparte contrato con `PATCH /api/v1/expenses/{expense_id}`. `expense_id` es el UUID del gasto. Omitir un campo conserva su valor y enviar `project_id: null` mueve el gasto a OPEX. El cuerpo también acepta `proyecto_id` como alias de `project_id`. Enviar `receipt_url: null` retira el enlace del comprobante y un enlace presente implica `has_receipt: true`. La API devuelve 404 si el gasto o la obra destino indicada no existen. [Router de gastos](../backend/src/infrastructure/http/routers/expenses.py) y [esquemas de gastos](../backend/src/infrastructure/http/schemas/expense.py).
- **Auditoría.** `GET /api/auditoria` comparte contrato con `GET /api/v1/audit-logs`. Devuelve `items` y `has_more`, con los eventos más recientes primero. La paginación usa `limit` y `offset`. Los filtros son `proyecto_id`, `entidad` y `accion`. Si un gasto cambia de obra, el filtro por proyecto encuentra el evento tanto en el origen como en el destino. [Router de auditoría](../backend/src/infrastructure/http/routers/audit.py) y [esquemas de auditoría](../backend/src/infrastructure/http/schemas/audit.py).

OpenAPI publica las variantes versionadas. Los flujos de la interfaz se describen en las [referencias del frontend](06_fase3_frontend.md#referencias-de-los-flujos).
