# Estado del proyecto

Actualizado: 2026-11-04. Fuente canónica de entregas, pendientes y evidencia; no contiene recetas de instalación ni reglas de diseño.

## Situación actual

- Rama de trabajo: `refactor/frontend-vite`.
- Fase activa: Fase 3, integración funcional de la interfaz. Secuencia en el [plan de frontend](06_fase3_frontend.md).
- Backend: dominio, persistencia, migraciones y API implementados; autenticación no implementada. Infraestructura final y datos semilla aplazados.
- Frontend: integración con la API implementada mediante cliente HTTP tipado basado en OpenAPI, consultas y mutaciones TanStack Query e invalidación de caché. Proyectos dispone de listado real, filtro local por estado, creación y edición parcial de nombre, cliente, presupuesto y estado desde el detalle. Gastos dispone de registro rápido con proyecto opcional y consulta de gastos operativos o por obra con filtros de fecha. Los formularios conservan datos ante errores, bloquean envíos simultáneos y confirman las operaciones exitosas.
- Inicio muestra métricas consultadas: obras registradas y completadas, gastos operativos, gastos de obras y total acumulado. Incluye carga, errores recuperables y protección frente a totales incompletos. El detalle de obra muestra sus datos y todos los gastos asociados.
- Arranque local en Windows disponible mediante `start_dev.ps1`; uso y requisitos en el [README raíz](../README.md#arranque-rápido).
- Configuración permite elegir tema claro u oscuro, persistirlo en el navegador y consultar la versión del ERP. El tema se aplica en todas las vistas. No existe todavía una sesión autenticada ni sincronización de preferencias con una cuenta.
- PWA instalable, caché de aplicación y sincronización offline: pendientes.

## Entregas y evidencia histórica

| Entrega | Referencia | Evidencia registrada |
| :--- | :--- | :--- |
| Dominio, repositorios y API, incluida actualización parcial de proyectos | `414c9ce` | 80 pruebas aprobadas; Ruff y mypy sin errores en la validación histórica |
| Migración de la interfaz | `e3f071c` | Lint/build y navegación de la base aprobados; build sin red externa tras instalar dependencias |
| Corrección de dependencias de desarrollo | `b483990` | Auditoría con cero vulnerabilidades en esa fecha; lint/build aprobados |
| Panel visual y branding | `312284e` | Lint/build, bloque frontend de check.ps1 y revisión en Chromium de 320 a 1440 px aprobados |
| Recursos de empresa y ajuste de Navbar | `6ae6c07`, `85ae4aa` | Integrados; no atribuirles automáticamente la validación del diseño anterior |
| Cliente HTTP y formularios funcionales de obras y gastos | Entrega de 2026-11-03 | DTO contrastados con OpenAPI; lint/build aprobados; Chromium con casos controlados y API local real |
| Dashboard con métricas reales, detalle de obra y arranque local | Entrega de 2026-11-03 | Lint/build aprobados; consultas verificadas en Chromium con respuestas controladas y API local; script exacto con sintaxis y argumentos comprobados |
| Edición parcial y estados de obras, filtros de fecha y Configuración básica | Entrega de 2026-11-04 | PATCH y filtros contrastados con OpenAPI y API local; caché y errores comprobados en Chromium; temas persistentes y vistas revisadas de 320 a 1440 px; lint/build aprobados |

Los resultados anteriores no se vuelven vigentes por editar documentación. El detalle operativo del frontend pertenece a su [README](../frontend/README.md).

## Pendientes de entrega

- Autenticación y preferencias sincronizadas con una cuenta.
- Captura y carga de comprobantes.
- Capacidades PWA y resolución de operaciones sin conexión.
- Orquestación de producción y seed, en pausa hasta preparar el despliegue final.

## Validación de la integración API

Se consultó el OpenAPI servido por la API local sin inspeccionar ni modificar código del backend. Los DTO reproducen campos requeridos, opcionalidad, enumeraciones e importes decimales del contrato.

- `make check-frontend` ejecutó `npm run lint` y `npm run build` sin errores. No se añadieron dependencias.
- Chromium verificó validaciones de campos, errores 422/500 y de conexión, respuestas malformadas, reintento de consultas, prevención de doble envío, refresco de listados y limpieza de formularios.
- Las pruebas controladas comprobaron presentación sin desbordes de 320 a 1280 px, sin errores de JavaScript.
- Con el navegador realmente desconectado se verificaron errores visibles, conservación de formularios y ausencia de envíos diferidos al reconectar; no hubo altas exitosas durante esa comprobación.
- La prueba contra la API local del entorno confirmó la creación y recarga de un proyecto y el registro/consulta de un gasto de obra y otro operativo, conservando importes decimales. Estos tres registros quedaron identificados con el prefijo `[Verificación frontend]`; no son datos de negocio.
- No se modificó el backend ni se ejecutaron sus tests. Autenticación, operaciones offline y edición de proyectos no se atribuyen a esta entrega.

## Validación del Dashboard, detalle y arranque local

- `make check-frontend` ejecutó `npm run lint` y `npm run build` sin errores. No se añadieron dependencias ni se modificó el backend.
- Se comprobaron siete casos de suma decimal, incluidos fracciones, notación científica e importes superiores al entero seguro de JavaScript.
- Chromium verificó carga, datos vacíos, fallos parciales y reintentos sin presentar sumas incompletas; inclusión de gastos de obras canceladas; acceso directo y recarga del detalle, obra inexistente y presentación de doce gastos sin recorte. Las mutaciones controladas actualizaron las métricas mediante la caché compartida.
- La presentación se revisó entre 320 y 1440 px, sin errores de JavaScript ni desbordes horizontales.
- La API local confirmó los totales frente a una suma decimal independiente y la correspondencia de la información y los gastos del detalle. Esta comprobación fue de solo lectura y no creó registros.
- `start_dev.ps1` coincide con las cuatro líneas solicitadas. PowerShell comprobó su sintaxis y los argumentos de los dos arranques mediante interceptación; la apertura real de ventanas en Windows no se ejecutó en este entorno Linux.

## Validación de edición, filtros y Configuración

- `make check-frontend` ejecutó `npm run lint` y `npm run build` sin errores. No se añadieron dependencias, no se modificó código del backend y no se ejecutaron sus tests.
- El PATCH parcial y los filtros inclusivos se contrastaron con el OpenAPI servido por la API local. Chromium comprobó envío exclusivo de cambios, presupuesto cero, validación, cancelación, bloqueo de doble envío y conservación de la edición ante errores 422, 500 y de conexión. La actualización se reflejó en detalle, listado y conteo del Dashboard.
- Las consultas controladas verificaron ambos límites de fecha, rangos abiertos y vacíos, bloqueo de rangos invertidos, limpieza, reintento e independencia de caché por cuenta y fechas. Un nuevo gasto controlado invalidó también los resultados filtrados.
- La API local confirmó PATCH de nombre, cliente, presupuesto y estado, persistencia tras recarga y filtros inclusivos reales. Se usó una obra identificada con `[Verificación frontend]` y se restauraron sus campos de negocio al terminar; no se crearon registros.
- Se comprobó persistencia de tema claro y oscuro tras recarga, aplicación entre rutas y respuesta visible al bloqueo de `localStorage`. Las vistas se revisaron en Chromium entre 320 y 1440 px, sin desbordes horizontales ni errores de JavaScript.
- La regresión del Dashboard y el detalle confirmó totales completos, recuperación de fallos parciales, estados vacíos, acceso directo y actualización de caché tras las mutaciones existentes.

## Historial documental

Consolidación SSOT registrada en `d096ef4`, sin cambios de aplicación en aquella revisión. El [índice documental](README.md#auditoría-de-consolidación) registra los documentos depurados y las propuestas aún no creadas.

Validación de aquella revisión documental: 18 archivos Markdown, 94 enlaces y anclas locales, referencias al código, identificadores ADR únicos y `git diff --check`. Esas comprobaciones no constituyeron nuevas ejecuciones de suites de aplicación.
