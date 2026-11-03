# Estado del proyecto

Actualizado: 2026-11-03. Fuente canónica de entregas, pendientes y evidencia; no contiene recetas de instalación ni reglas de diseño.

## Situación actual

- Rama de trabajo: `refactor/frontend-vite`.
- Fase activa: Fase 3, integración funcional de la interfaz. Secuencia en el [plan de frontend](06_fase3_frontend.md).
- Backend: dominio, persistencia, migraciones y API implementados; autenticación no implementada. Infraestructura final y datos semilla aplazados.
- Frontend: migración y panel visual entregados. Las vistas de módulos están en preparación; las cifras son ejemplos, no consultas reales. No hay operaciones persistidas desde la SPA ni sesión autenticada.
- PWA instalable, caché de aplicación y sincronización offline: pendientes.

## Entregas y evidencia histórica

| Entrega | Referencia | Evidencia registrada |
| :--- | :--- | :--- |
| Dominio, repositorios y API, incluida actualización parcial de proyectos | `414c9ce` | 80 pruebas aprobadas; Ruff y mypy sin errores en la validación histórica |
| Migración de la interfaz | `e3f071c` | Lint/build y navegación de la base aprobados; build sin red externa tras instalar dependencias |
| Corrección de dependencias de desarrollo | `b483990` | Auditoría con cero vulnerabilidades en esa fecha; lint/build aprobados |
| Panel visual y branding | `312284e` | Lint/build, bloque frontend de check.ps1 y revisión en Chromium de 320 a 1440 px aprobados |
| Recursos de empresa y ajuste de Navbar | `6ae6c07`, `85ae4aa` | Integrados; no atribuirles automáticamente la validación del diseño anterior |

Los resultados anteriores no se vuelven vigentes por editar documentación. El detalle operativo del frontend pertenece a su [README](../frontend/README.md).

## Pendientes de entrega

- Cliente HTTP tipado y consultas/mutaciones con estados de carga, error y vacío.
- Listados y formularios reales de obras y gastos; sustitución de ejemplos por datos consultados.
- Autenticación y preferencias persistentes.
- Captura y carga de comprobantes.
- Capacidades PWA y resolución de operaciones sin conexión.
- Orquestación de producción y seed, en pausa hasta preparar el despliegue final.

## Actualización documental actual

Consolidación SSOT preparada sin cambios de aplicación. El [índice documental](README.md#auditoría-de-consolidación) registra los documentos depurados y las propuestas aún no creadas.

Validación de esta actualización: 18 archivos Markdown, 94 enlaces y anclas locales, referencias al código, identificadores ADR únicos y `git diff --check`. No se ejecutan nuevas suites de aplicación por esta tarea documental.
