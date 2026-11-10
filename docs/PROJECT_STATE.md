# Estado del proyecto

Actualizado: 2026-11-10. Fuente canónica de entregas, pendientes y evidencia; no contiene recetas de instalación ni reglas de diseño.

## Situación actual

- Rama de trabajo: `feature/fase4-evolucion`.
- Fase activa: Fase 4, en ejecución según la [planificación de evolución y resiliencia](07_fase4_evolucion_y_resiliencia.md).
- Backend base de las Fases 1 y 2: dominio, persistencia, migraciones y API implementados; autenticación no implementada. Infraestructura final y datos semilla aplazados.
- Fase 4, Módulo 1, Paso 1: núcleo puro y contratos implementados para resúmenes financieros e idempotencia. Incluye proyecciones, DTO, contratos de repositorio, puertos de identidad y autorización, excepciones, filtro fiscal opcional y moneda tipada, snapshots inmutables, confirmaciones con payload opcional y canonicalización extensible a metadatos sin binarios. El dominio y los contratos no dependen de Pydantic, SQLAlchemy ni FastAPI. Identidad Dummy estable e inyectable disponible exclusivamente en desarrollo local; no constituye autenticación real.
- Fase 4, Módulo 1, Paso 2: casos de uso, repositorio SQLAlchemy y endpoints HTTP de resumen general y por obra implementados y probados contra PostgreSQL real. Cada resumen agrega gastos y cantidades en una sola sentencia SQL, con autorización global o por obra, filtros inclusivos de fecha, separación fiscal explícita e importes decimales exactos. Migración aditiva de clasificación fiscal nullable disponible, sin asignar valores a obras históricas; la clasificación obligatoria de escritura sigue pendiente de su evolución funcional. El frontend conserva sus consultas anteriores.
- Fase 4, Módulo 1, Paso 3: registro transaccional, modelo ORM de operaciones, repositorio SQLAlchemy de idempotencia y migración implementados y probados en concurrencia con PostgreSQL real. La clave compuesta por actor y operación arbitra la reserva; los snapshots versionados usan JSONB nullable para futura purga. Reserva y confirmación comparten la transacción de negocio, sin commit ni rollback en el repositorio.
- Fase 4, Módulo 1, Paso 4: integración de comandos, canonicalización SHA-256 y compatibilidad de rutas de escritura implementadas y probadas. Las altas de obras y gastos y el PATCH de obras reservan, ejecutan negocio, capturan el snapshot y confirman cuando reciben clave e identidad válidas; permiten preasignar el UUID del recurso y recuperan el resultado original al repetir. Sin clave o identidad conservan el flujo antiguo sin deduplicación. El commit de la dependencia termina antes de enviar éxito HTTP, verificado también bajo fallo forzado.
- Fase 4, Módulo 1, Paso 5: consulta autorizada de recuperación implementada y probada en PostgreSQL real. El caso de uso y el endpoint de operaciones aíslan por actor, revalidan permisos antes de leer el payload y devuelven el snapshot original o los errores de operación desconocida, resolución incierta y reconciliación requerida. **EL CÓDIGO BACKEND DEL MÓDULO 1 ESTÁ COMPLETO** para el alcance aprobado de esta iteración: resúmenes financieros e idempotencia de obras y gastos con recuperación. La integración del frontend, la sesión real y la futura cola offline conservan sus alcances posteriores.
- Frontend: integración con la API implementada mediante cliente HTTP tipado basado en OpenAPI, consultas y mutaciones TanStack Query e invalidación de caché. Proyectos dispone de listado real, filtro local por estado, creación y edición parcial de nombre, cliente, presupuesto y estado desde el detalle. Gastos dispone de registro rápido con proyecto opcional y consulta de gastos operativos o por obra con filtros de fecha. Los formularios conservan datos ante errores, bloquean envíos simultáneos y confirman las operaciones exitosas.
- Inicio muestra métricas consultadas: obras registradas y completadas, gastos operativos, gastos de obras y total acumulado. Incluye carga, errores recuperables y protección frente a totales incompletos. El detalle de obra muestra sus datos y todos los gastos asociados.
- Arranque local en Windows disponible mediante `start_dev.ps1`; uso y requisitos en el [README raíz](../README.md#arranque-rápido).
- Configuración permite elegir tema claro u oscuro, persistirlo en el navegador y consultar la versión del ERP. El tema se aplica en todas las vistas. No existe todavía una sesión autenticada ni sincronización de preferencias con una cuenta.
- Frontend auditado y pulido en UX/UI, manejo de errores y caché, cerrando la estabilidad de la Fase 3 para los flujos implementados. Las mejoras que requieren ampliar el contrato del servicio se planifican en la [Fase 4](07_fase4_evolucion_y_resiliencia.md), con antecedentes en las [propuestas de UX/UI](UX_UI_SUGGESTIONS.md).
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
| Auditoría y pulido de estabilidad de la Fase 3 | Entrega de 2026-11-04 | Lint/build sin advertencias; carreras de caché, errores de escritura, controles táctiles, precisión de importes y casos extremos a 320 px verificados en Chromium con API simulada |

Los resultados anteriores no se vuelven vigentes por editar documentación. El detalle operativo del frontend pertenece a su [README](../frontend/README.md).

## Pendientes de entrega

- Autenticación y preferencias sincronizadas con una cuenta.
- Captura y carga de comprobantes.
- Capacidades PWA y resolución de operaciones sin conexión.
- Orquestación de producción y seed, en pausa hasta preparar el despliegue final.

## Validación del Paso 5 de recuperación

Entrega de 2026-11-10 sobre `feature/fase4-evolucion`.

- La suite completa aprobó 270 pruebas en Python 3.12, incluidas 26 nuevas de
  recuperación HTTP contra PostgreSQL 17, sin omisiones. Persisten los dos avisos
  de deprecación de AnyIO y Starlette.
- La consulta devolvió 200 con los metadatos públicos y el snapshot original de
  alta de obra, registro de gasto y edición de obra. Conservó decimales y
  timestamps tras cambios posteriores o eliminación del recurso, sin consultar
  su estado actual ni ejecutar comandos.
- Operaciones desconocidas, ajenas y con permisos revocados devolvieron el mismo
  404 `operation_unknown`. Un UUID compartido por dos actores recuperó únicamente
  el resultado de cada identidad del servidor; un actor enviado en encabezados o
  parámetros no permitió cambiar ese espacio de consulta.
- La autorización precedió a la lectura del JSONB, comprobando el SQL emitido.
  La revocación siguió devolviendo 404 incluso con payload purgado, corrupto o de
  versión no soportada. Para un actor autorizado, esos tres casos devolvieron
  409 `operation_reconciliation_required` sin alterar el registro.
- Una reserva visible sin confirmar y un bloqueo real de tabla produjeron
  503 `operation_unresolved`; tras liberar el bloqueo se recuperó el resultado.
  Una escritura pausada antes de su commit no resultó visible para la consulta:
  devolvió 404 y, después del commit, 200 con el mismo resultado original.
- Se verificaron identidad obligatoria fuera de desarrollo, rechazo de UUID no
  válidos sin consultar la base, OpenAPI y respuestas sin almacenamiento en
  caché. Las pruebas de comandos y recuperación comparten la dependencia de
  sesión real; las suites anteriores conservaron sus resultados.
- `make check-backend` aprobó Ruff, formato y mypy estricto en 68 archivos de
  `src/`; mypy también aprobó con objetivo Python 3.12. No se añadieron
  dependencias ni migraciones y no se modificó el frontend. La validación usó
  esquemas aislados de una base temporal, sin migrar bases de negocio.

## Validación del Paso 4 de integración de comandos

Entrega de 2026-11-10 sobre `feature/fase4-evolucion`.

- La suite completa aprobó 244 pruebas en Python 3.12, sin omisiones. Incluye
  65 casos nuevos de comandos HTTP contra PostgreSQL 17 y 12 de precisión
  monetaria, además de las suites previas. Persisten los dos avisos de
  deprecación de AnyIO y Starlette.
- Se verificaron las tres rutas con clave y sin ella, identidad ausente,
  UUIDv4 inválidos, identificadores preasignados, alias con y sin barra final y
  equivalencia de opcionales y escala decimal. OpenAPI conserva opcionales los
  nuevos campos y encabezados; el indicador de reintento es accesible por CORS.
- Los reintentos devolvieron los snapshots originales y sus timestamps tras
  ediciones, cancelación de la obra e incluso eliminación del recurso. Otro
  contenido, comando u objetivo produjo conflicto; ocupar un identificador con
  otra operación no sobrescribió el recurso. Payload purgado, corrupto o con
  versión desconocida nunca permitió ejecutar nuevamente una clave conocida.
- Dos solicitudes HTTP concurrentes compartieron la misma clave: una ejecutó
  el negocio y la otra recibió un 503 recuperable por contención. El reintento
  posterior recuperó el único resultado confirmado. Se verificó aislamiento
  por actor resuelto en servidor e ignorancia de un actor enviado por el cliente.
- Las denegaciones actuales de comando o resultado no entraron al flujo
  anterior. El puerto recibió también la obra de imputación de un gasto. Los
  fallos de permisos y de validación de negocio revirtieron la reserva junto con
  cualquier efecto pendiente; corregir una solicitud sin confirmar permitió
  ejecutarla con la misma clave.
- Se interceptó el commit de la dependencia real en las tres rutas y ambos
  modos: cada fallo produjo rollback y solo envió `http.response.start` con
  estado 500, sin emitir 200 ni 201. Fallar al construir la respuesta también
  revirtió negocio y confirmación. Simular pérdida del acuse después de un
  commit real produjo error HTTP y permitió recuperar por reintento sin duplicar.
- Se rechazaron importes que necesitaran redondeo o excedieran la precisión
  persistida en el contrato idempotente, sin alterar la precisión de agregados ni
  depender del contexto Decimal. Se conservó la interfaz de metadatos de
  adjuntos y el rechazo de binarios y streams sin leerlos.
- `make check-backend` aprobó Ruff, formato y mypy estricto en 66 archivos de
  `src/`; mypy también aprobó con objetivo Python 3.12. No se instalaron nuevas
  dependencias, no se añadieron migraciones ni se modificó el frontend. Las
  pruebas aplicaron las migraciones existentes solo en esquemas aislados de una
  base temporal; la consulta de recuperación y la autenticación real siguen
  pendientes.

## Validación del Paso 3 de registro transaccional

Entrega de 2026-11-09 sobre `feature/fase4-evolucion`.

- La suite completa aprobó 167 pruebas en Python 3.12, incluidas 26 nuevas del
  registro y las 29 de resúmenes contra PostgreSQL 17 real, sin omisiones.
  Persisten dos avisos de deprecación de dependencias externas (AnyIO y Starlette).
- Dos sesiones iniciadas simultáneamente compitieron por la misma clave: una
  preparó un único cambio de negocio y su confirmación; la otra recibió
  `OperationUnresolvedError` por timeout mientras el ganador conservaba la
  transacción abierta. El reintento posterior recuperó la confirmación original.
- Las pruebas verificaron commit y rollback conjuntos de negocio y registro,
  invisibilidad de datos no confirmados para otra sesión, liberación de la clave
  tras rollback y ausencia de llamadas a commit o rollback en el repositorio.
- La reserva quedó vinculada al identificador de transacción de PostgreSQL. Se
  rechazaron confirmaciones después de un commit prematuro y modificaciones de
  resultados ya confirmados. Los errores de contención exigieron rollback del
  llamador; el timeout local no quedó aplicado después de ese rollback.
- Se verificaron snapshots de obra y gasto con UUID, enums, fechas, timestamps y
  decimales exactos, también bajo un contexto Decimal de baja precisión. La purga
  a SQL NULL conservó identidad, huella, versiones y referencias, sin habilitar
  una nueva reserva. Resultados corruptos o con versiones no soportadas exigieron
  reconciliación; borrar el recurso no eliminó su confirmación.
- Se comprobaron aislamiento por actor, conflictos por contenido, comando,
  versión u objetivo y restricciones persistentes de coherencia. Recuperar o
  repetir una clave conocida no forzó el flush de objetos de negocio pendientes.
- La migración se ensayó en upgrade y downgrade dentro de esquemas aislados,
  verificando PK compuesta y JSONB nullable. Los resúmenes y operaciones comparten
  ahora la infraestructura de pruebas PostgreSQL; no se migraron bases de negocio.
- `make check-backend` aprobó Ruff, formato y mypy estricto en 63 archivos de
  `src/`; mypy también aprobó con objetivo Python 3.12. No se añadieron
  dependencias ni se modificaron frontend, comandos o routers HTTP de escritura.

## Validación del Paso 2 de resúmenes

Entrega de 2026-11-09 sobre `feature/fase4-evolucion`.

- La suite completa de Pytest aprobó 141 pruebas en Python 3.12, incluidas 29
  nuevas con TestClient y PostgreSQL 17 real, sin omisiones. Persisten dos avisos
  de deprecación de dependencias externas (AnyIO y Starlette).
- Cada prueba PostgreSQL aplicó Alembic en un esquema generado y aislado. Se
  verificaron upgrade y downgrade de la clasificación fiscal, preservación de
  datos históricos como NULL y ausencia de un valor por defecto. Solo se usó una
  base temporal de pruebas, sin migrar bases de negocio.
- Se comprobaron exactitud de fracciones decimales, totales superiores al límite
  de una fila NUMERIC(12,2), fechas inclusivas y rangos abiertos, datos vacíos,
  gastos históricos de obras canceladas y reconciliación con el detalle real.
- Las solicitudes verificadas ejecutaron una sentencia de agregación por
  resumen. Añadir 30 obras no incrementó ese número; el repositorio devolvió
  proyecciones puras sin poblar el mapa de entidades ORM de la sesión.
- Las pruebas separaron `has_iva=true`, `false` y ausencia de filtro en SQL;
  OPEX y obras sin clasificar no entraron en un subconjunto fiscal. Los
  contadores de obras siguieron ese subconjunto sin depender del período de
  gastos.
- Se verificaron denegación del resumen global sin permiso global, aislamiento
  por obra, respuestas indistinguibles para obras inexistentes, excluidas o
  ajenas, activación del Dummy solo en desarrollo y rechazo de filtros inválidos
  antes de consultar la base. Los errores de persistencia devolvieron 503 sin
  totales parciales; un gasto confirmado apareció en la siguiente lectura.
- `make check-backend` aprobó Ruff, formato y mypy estricto en 60 archivos de
  `src/`; mypy también aprobó con objetivo Python 3.12. No se añadieron
  dependencias ni se modificó el frontend. La persistencia idempotente y sus
  pruebas de concurrencia pertenecen al Paso 3.

## Validación del Paso 1 de contratos y núcleo

Entrega de 2026-11-09 sobre `feature/fase4-evolucion`, posterior a la aprobación
de la [propuesta de ingeniería versión 0.2](https://chatgpt.com/space/page_5c78f7dfe3f881919ec1929c3884e5c2).

- `make check-backend` aprobó Ruff, formato y mypy estricto en los 55 archivos de
  `src/`. La suite completa de Pytest aprobó 112 pruebas en Python 3.12, con dos
  avisos de deprecación de dependencias externas (AnyIO y Starlette).
- Los casos nuevos verificaron la conservación de los tres valores del filtro
  fiscal, los límites temporales del contrato, snapshots independientes de cambios
  posteriores, confirmaciones purgadas que exigen reconciliación y separación de
  identidad de operación y recurso.
- La canonicalización comprobó equivalencia de orden y escala decimal, precisión
  independiente del contexto Decimal, normalización temporal, huellas diferentes
  por comando, objetivo y metadatos, y rechazo de streams sin leerlos.
- La inyección HTTP local conservó el mismo actor entre peticiones e ignoró un
  encabezado que intentaba seleccionarlo. Se verificó ausencia de Dummy en
  producción, testing y configuración por defecto, además de denegación de actores
  ajenos y aislamiento de dependencias entre núcleo e infraestructura.
- El inicio de TestClient quedó bloqueado dentro del aislamiento de red del
  sandbox. Tras interrumpir esas ejecuciones, la suite completa terminó fuera de
  ese aislamiento. Las pruebas HTTP usaron fakes y las de repositorios existentes,
  SQLite; no se atribuye concurrencia ni persistencia idempotente en PostgreSQL a
  esta entrega.
- No se modificó el frontend ni se ejecutaron sus comprobaciones. No se aplicaron
  migraciones ni se habilitaron endpoints nuevos. La clasificación de IVA de
  obras históricas y el esquema SQLAlchemy anulable se resolverán al implementar
  sus adaptadores y migraciones; el núcleo no inventa clasificaciones históricas.

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

## Validación de auditoría y estabilidad del frontend

- `make check-frontend` ejecutó `npm run lint` y `npm run build` sin errores ni advertencias. Se revisaron imports, tipado estricto y ausencia de logs de depuración. No se añadieron dependencias.
- Las pruebas controladas comprobaron que una lectura tardía no sobrescribe un PATCH confirmado y que el detalle usa la colección actualizada al volver a entrar. Las altas no invalidan detalles ajenos; los gastos refrescan todos los rangos de su cuenta y el resumen correspondiente, preservando las otras cuentas.
- Se verificaron respuestas POST/PATCH ilegibles tras una escritura aceptada: aviso visible, conservación del formulario, actualización de las consultas y ausencia de reenvíos automáticos. La regresión de formularios, errores 422/500/de conexión, filtros, Dashboard y temas siguió aprobada.
- Chromium comprobó cargas y actualizaciones visibles, navegación por teclado y controles táctiles de al menos 44 px. Los campos numéricos conservan teclado decimal y texto de 16 px en móvil. Mensajes, nombres, clientes e importes extensos se revisaron a 320 px en ambos temas sin desbordes horizontales; se midió contraste mínimo de 4,5:1 en los textos de la tarjeta azul.
- Diez casos comprobaron el formato monetario exacto, incluidos importes por encima del entero seguro de JavaScript, redondeo y notación científica. Los recorridos de regresión también se comprobaron entre 320 y 1440 px, sin errores de JavaScript.
- Esta auditoría usó exclusivamente respuestas de API simuladas para probar el frontend: no ejecutó, consultó ni modificó el backend, ni creó datos de negocio. Las propuestas que requieren cambios del servicio se documentaron sin implementarlas.

## Historial documental

### Apertura de la Fase 4 — 2026-11-05

Se creó el [plan de Fase 4](07_fase4_evolucion_y_resiliencia.md), integrando las notas acordadas del cliente y las propuestas pendientes de UX/UI. Se registraron los ADR de [idempotencia offline](adr/0002-idempotencia-offline.md) y [motor financiero por IVA](adr/0003-motor-financiero-iva.md), y se actualizaron los accesos del [índice](README.md) y del [itinerario LLM](LLM_CONTEXT.md).

La entrega se limita al diseño documental. Los módulos de esta fase siguen pendientes de implementación; no se modificaron frontend, backend, contratos ejecutables ni dependencias. La aceptación de las decisiones arquitectónicas no implica haber entregado autenticación, sincronización, gestión de archivos, nuevas reglas financieras, RRHH o inventario.

Validación de esta entrega: revisión de coherencia y referencias al código; comprobación de 23 archivos Markdown y 139 enlaces locales, incluidas 24 anclas; identificadores ADR aceptados únicos del 0000 al 0003; alcance de seis documentos bajo `docs/` y `git diff --check` sin errores. No se ejecutaron suites de aplicación por tratarse de una entrega exclusivamente documental.

### Consolidación SSOT anterior

Consolidación SSOT registrada en `d096ef4`, sin cambios de aplicación en aquella revisión. El [índice documental](README.md#auditoría-de-consolidación) registra los documentos depurados y las propuestas aún no creadas.

Validación de aquella revisión documental: 18 archivos Markdown, 94 enlaces y anclas locales, referencias al código, identificadores ADR únicos y `git diff --check`. Esas comprobaciones no constituyeron nuevas ejecuciones de suites de aplicación.
