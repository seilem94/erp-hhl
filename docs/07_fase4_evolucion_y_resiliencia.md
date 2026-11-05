# Plan de Fase 4 — Evolución del Dominio, Resiliencia y Reglas de Negocio

Responsabilidad: secuencia de trabajo, criterios de aceptación y reglas acordadas para esta evolución que no sean propiedad de un ADR. Las entregas y la evidencia se registran exclusivamente en [PROJECT_STATE.md](PROJECT_STATE.md). Este plan define trabajo futuro; no constituye un contrato HTTP implementado.

Las propuestas de [agregados financieros](UX_UI_SUGGESTIONS.md#agregados-financieros-en-el-servicio) y [confirmación idempotente](UX_UI_SUGGESTIONS.md#confirmación-idempotente-de-escrituras) son los antecedentes del Módulo 1. Las notas del cliente recibidas el 2026-11-05 se incorporan como reglas acordadas en los módulos correspondientes y en el ADR financiero. Las preguntas históricas de la [guía con el socio](05_revision_mvp_socio.md) siguen siendo material de descubrimiento, no requisitos adicionales aceptados.

Aplicar las [reglas de arquitectura](02_reglas_arquitectura.md) al evolucionar el dominio, los casos de uso y los adaptadores. Las decisiones de idempotencia y separación financiera, con sus compensaciones, tienen como fuente única el [ADR 0002](adr/0002-idempotencia-offline.md) y el [ADR 0003](adr/0003-motor-financiero-iva.md), respectivamente. Los routers, esquemas y OpenAPI serán la autoridad de los futuros contratos; este documento no mantiene un catálogo paralelo de rutas ni DTO.

## Módulo 1: Arquitectura y Resiliencia

### Idempotencia y recuperación de resultados

1. Evolucionar las altas y los comandos de modificación conforme al [ADR de idempotencia](adr/0002-idempotencia-offline.md#decisión), revisando el impacto en casos de uso, repositorios, restricciones persistentes y cliente HTTP.
2. Diseñar la consulta autorizada del resultado de una operación conforme al protocolo de recuperación y conservación del ADR, para resolver confirmaciones perdidas.
3. Integrar recuperación, reintentos y conflictos en la interfaz antes de habilitar envíos diferidos. Una operación local pendiente no debe aparecer como confirmada por el servidor.
4. Delimitar la futura cola por usuario, conservar dependencias entre obra, archivo y comando, y detener el envío ante sesión expirada o conflicto. El diseño completo de PWA, caché y actualización de recursos requiere una decisión posterior; se coordina con el [plan de Fase 3](06_fase3_frontend.md#5-pwa-y-operación-offline).

**Aceptación:** verificar pérdida de respuesta después de confirmar, solicitudes concurrentes, recarga del navegador, caída antes del commit y repetición con contenido alterado según el ADR. Incluir el reintento de un cambio de estado y de una liquidación, además de las altas. Comprobar persistencia y concurrencia contra PostgreSQL, sin atribuir esa garantía a pruebas con fakes o SQLite.

### Endpoints de resumen financiero

1. Diseñar un endpoint de resumen general y otro por obra, mediante casos de consulta y contratos de repositorio de lectura. La agregación se ejecuta en persistencia; el router no contiene consultas ORM y el cliente no descarga cada historial para reconstruir un total.
2. Cubrir inicialmente gastos operativos, gastos imputados a obras, total de gastos y cantidades de obras por estado. Incluir los gastos históricos de obras canceladas. El resumen por obra debe permitir reconciliar el costo acumulado con sus registros de detalle.
3. Precisar filtros opcionales e inclusivos de fecha, moneda, alcance autorizado y momento de corte. Las fechas filtran la fecha del gasto; los contadores de obras describen el conjunto de obras visibles, sin filtrarse implícitamente por su fecha de creación. Un rango invertido se rechaza y una consulta sin límites abarca todo el historial autorizado.
4. Devolver importes decimales exactos y una respuesta consistente para el mismo corte. Un conjunto vacío produce ceros; un fallo produce un error recuperable, nunca un total parcial presentado como definitivo. Definir la zona horaria cuando el corte o los datos incluyan instantes.
5. Sustituir las consultas del Dashboard tras contrastar el resumen con una suma independiente del detalle y adaptar la invalidación de caché. El Módulo 4 extenderá estas lecturas a cuentas y cobros, sin confundirlos con gastos.

**Aceptación:** reconciliación exacta con gastos operativos y de obras, límites de fecha, importes extremos, datos vacíos, obras canceladas y permisos. Comprobar que las solicitudes del Dashboard y las consultas de agregación no crecen una por cada obra, y que una escritura confirmada actualiza el resumen afectado.

## Módulo 2: Identidad y Seguridad

### Roles y privilegios

Establecer una matriz de permisos por acción, recurso y ámbito de obra o cuenta antes de conectar una sesión real:

- **Administrador:** administrar identidades, asignar roles y privilegios y gestionar la operación global. Los cambios de acceso deben quedar auditados.
- **Socio:** operar sobre las obras y cuentas que se le autoricen. Su condición no concede por sí sola acceso a todas las cuentas de otros socios ni administración de identidades.
- **Trabajador:** acceder a las obras y tareas asignadas y a sus registros de asistencia, gastos y custodia de herramientas según la matriz. La asignación a una cuadrilla no concede privilegios financieros globales.

La excepción para registrar **gastos sin boleta** corresponde exclusivamente a Socios y Administrador y exige motivo y autor trazables. Los Trabajadores **siempre requieren respaldo verificable**; una declaración de que existe o una URL arbitraria no satisface esa condición. Distinguir ausencia de boleta y ausencia de respaldo para precisar los documentos admitidos antes de implementar. La condición fiscal de una obra no altera estos permisos.

La identidad y los permisos efectivos provienen del servidor. No aceptar un rol, autor o privilegio declarado en el cuerpo de la solicitud para habilitar la excepción. Resolver expresamente la acumulación de roles antes de permitir combinaciones que cambien esta política.

### Autenticación y autorización

1. Seleccionar y documentar en un ADR independiente el mecanismo de sesión para SPA y API: inicio y cierre, expiración, renovación o revocación, almacenamiento y protección del transporte. Definir las protecciones necesarias para la alternativa elegida, sin presentar una elección pendiente como implementada.
2. Denegar por defecto y comprobar permisos en cada caso de uso, incluida consulta de resúmenes, recuperación de operaciones, descarga de archivos y acceso directo por identificador. Ocultar un botón solo adapta la experiencia.
3. Definir quién puede asignar personas a obras y cuadrillas, registrar asistencia ajena, aprobar jornadas, cambiar estados, custodiar herramientas y confirmar pagos. Registrar actor, fecha, recurso y motivo en las acciones sensibles.
4. Aislar caché y operaciones locales por identidad; resolver cierre de sesión, cambio de cuenta y revocación sin exponer datos de otra persona ni reenviar su cola bajo una nueva sesión.

**Aceptación:** identidad ausente, sesión expirada, acceso entre obras o cuentas ajenas, intento de cambiar el rol en una solicitud y revocación durante una sincronización. La matriz debe demostrar los permisos de captura y respaldo anteriores y el acceso autorizado a cada recurso, tanto por interfaz como por llamada directa a la API.

## Módulo 3: Evolución de Obras y Archivos

### Datos de obra y tareas pendientes

- Exigir **Ubicación** y **Referencia** al crear una obra; rechazar valores vacíos o compuestos solo por espacios. Acordar formato y longitud sin imponer geolocalización como requisito adicional.
- Incorporar **Tareas pendientes** como registros vinculados a la obra, con descripción, responsable cuando corresponda y estado de resolución. Mantener autoría y cambios trazables; precisar si existen tareas que bloquean el cierre antes de aplicar ese bloqueo.
- Preparar una migración gradual para obras existentes: identificar información faltante, permitir su regularización y activar las restricciones finales tras completarla. No inventar ubicaciones, referencias ni evidencia retroactiva.

### Evidencia multimedia y transiciones de estado

1. Modelar cada cambio de estado como un comando con estado o versión esperada, actor y evidencia de control vinculada. El ingreso a ejecución exige fotos del **antes**, tomadas antes de ejecutar; el término exige fotos del **después**, correspondientes al trabajo terminado. Una foto genérica del proyecto no acredita automáticamente una transición.
2. Definir la matriz de transiciones sobre los estados del dominio, incluidos pausa, reanudación, cancelación y reapertura. Precisar la evidencia exigida en cada caso antes de habilitarlo; no dejar un cambio genérico que eluda el control fotográfico. La edición parcial debe delegar la misma validación cuando incluya estado.
3. Diseñar un recurso de archivo compartido para evidencias y comprobantes: identificador, autor, pertenencia a obra o gasto, tipo, tamaño, integridad y estado de carga. El dominio conserva referencias y metadatos de negocio; el almacenamiento binario se resuelve mediante un puerto y su adaptador.
4. Acordar formatos admitidos, cantidad de fotos, límites, compresión, conservación y política de eliminación. Validar contenido y acceso en servidor; una carga iniciada, una ruta libre o un archivo de otra obra no son evidencia válida.
5. Completar y verificar la carga antes de confirmar la transición. Persistir estado, historial y vínculo de evidencia en una misma transacción de base de datos. El almacenamiento de archivos no comparte esa transacción: prever cargas huérfanas, limpieza y recuperación sin borrar archivos ya referenciados.
6. Aplicar el mecanismo del Módulo 1 a carga, finalización y transición, preservando sus dependencias. Si falta evidencia o cambió la versión de la obra, conservar el estado anterior y devolver un conflicto o validación recuperable.

**Aceptación:** datos obligatorios, tareas persistentes y acceso por obra; inicio y término con sus fotos correspondientes; rechazo de evidencia incompleta, ajena o de etapa incorrecta. Simular interrupción de carga, cambios concurrentes y repetición de comandos, comprobando un único cambio de estado y su historial. Revisar por separado el tratamiento del historial anterior a la migración.

## Módulo 4: Motor Financiero Avanzado

Las reglas canónicas de condición fiscal, destino de fondos, cuotas/link y selección de política salarial están en el [ADR financiero](adr/0003-motor-financiero-iva.md#decisión). Los permisos y excepciones de respaldo pertenecen al [Módulo 2](#módulo-2-identidad-y-seguridad); no se derivan del IVA.

### Secuencia de diseño

1. Evolucionar el modelo de obra y su clasificación financiera conforme al ADR. Diseñar cuentas identificables y movimientos con cuenta, obra cuando corresponda, concepto, importe, moneda, fecha y autor; registrar explícitamente el socio responsable cuando proceda.
2. Separar presupuesto, costo, cobro programado, cobro recibido y pago efectuado. Diseñar la conciliación de transferencias, reintegros y gastos OPEX conforme al ADR, evitando duplicaciones al consolidar cuentas.
3. Modelar acuerdos de cobro, vencimientos, cuotas, estados y referencias de link de pago conforme a su elegibilidad. Emitir un link o programar una cuota no equivale a recibir dinero. Si se integra un proveedor, confirmar eventos y conciliación en servidor y deduplicar sus notificaciones antes de afectar saldos.
4. Validar conjuntamente actor, respaldo confirmado, obra, clasificación y cuenta antes de persistir un gasto o movimiento. Reutilizar el recurso de archivo del Módulo 3 y evaluar estas reglas en los casos de uso; no confiar en indicadores de la interfaz.
5. Diseñar la política de remuneración seleccionada por el ADR y recibir del Módulo 5 la asistencia aprobada. Diferenciar cálculo provisional, liquidación aprobada y desembolso para impedir pagos duplicados y permitir correcciones auditadas.
6. Extender los resúmenes del Módulo 1 con saldos y agrupaciones por cuenta y clasificación, respetando permisos. Mantener visibles las diferencias entre costos, obligaciones y caja efectivamente movida.

**Aceptación:** casos combinados para ambas clasificaciones financieras, destino permitido o incompatible, modalidades elegibles o rechazadas y permisos de respaldo. Reconciliar detalle, resumen y movimientos; comprobar anticipos, pagos parciales, notificaciones repetidas y correcciones de clasificación sin alterar silenciosamente movimientos o liquidaciones anteriores.

**Definiciones que condicionan la implementación:** aprobar tasas y base de cálculo aplicables, redondeo, tarifas y fórmulas salariales para cada política, reparto entre socios, cuenta pagadora y reglas de ajustes o anulación. No inferir una tasa, descuento o fórmula a partir de la sola existencia del indicador de impuestos.

## Módulo 5: RRHH e Inventario

### Cuadrillas, asistencia y pagos

1. Modelar personas, cuadrillas y asignaciones a proyecto con vigencia y responsable. Vincular la identidad de acceso a la persona sin confundir pertenencia a una cuadrilla con un rol de seguridad.
2. Registrar asistencia por **trabajador, cuadrilla, proyecto, jornada y turno**, con duración o fracción de jornada, estado de revisión y aprobador. Definir jornadas parciales, ausencias, reemplazos y traspasos entre obras; evitar solapamientos y duplicación de horas al consolidar una persona en varias cuadrillas.
3. Separar captura de asistencia de su aprobación. Precisar quién puede registrar al equipo y quién valida, siguiendo el Módulo 2. Conservar las correcciones y la fuente temporal utilizada.
4. Generar propuestas de liquidación desde asistencia aprobada y la política financiera del Módulo 4. Una aprobación de asistencia no confirma por sí sola una transferencia; la confirmación del pago y su recuperación deben seguir el Módulo 1.

**Aceptación:** un trabajador en varias obras dentro del período, fracciones y ausencias, rechazo de superposiciones, aprobación autorizada y corrección posterior al cierre. Cada importe calculado debe poder rastrearse hasta jornadas y versión de política; el reintento no duplica asistencia, liquidación ni desembolso.

### Bodega, herramientas y turnos

1. Distinguir existencias consumibles y herramientas individualizadas. Modelar bodega, entradas, salidas, devoluciones, traslados, ajustes y disponibilidad, con referencia a proyecto cuando corresponda.
2. Registrar asignación y devolución de herramientas por proyecto, **responsable y turno**, con fechas, condición de entrega y recepción y trazabilidad de cambios de custodio.
3. Validar disponibilidad y concurrencia: una herramienta no puede quedar asignada a dos custodios en el mismo intervalo y una salida no puede generar stock negativo. El responsable vigente debe poder consultarse desde bodega y desde la obra.
4. Autorizar movimientos según la matriz de seguridad y usar la confirmación del Módulo 1. Relacionar una compra o gasto con el ingreso físico cuando exista ese vínculo; una asignación o devolución no genera automáticamente un nuevo gasto.

**Aceptación:** recepción en bodega, asignación a obra, cambio de turno con entrega, devolución, daño o pérdida y ajuste autorizado. Probar competencia por la última unidad y por la misma herramienta, movimientos repetidos y consulta del responsable histórico.

## Secuencia de ejecución y dependencias

1. Cerrar el diseño de contratos del Módulo 1 y la matriz de permisos y sesión del Módulo 2. Proteger las escrituras y la consulta de resultados antes de habilitar reintentos o sincronización para usuarios.
2. Entregar la base de resiliencia y los resúmenes iniciales, verificando compatibilidad con los consumidores existentes. Mantener deshabilitada la cola hasta validar identidad, concurrencia y recuperación.
3. Evolucionar obras y archivos con el Módulo 3; habilitar transiciones controladas solo cuando los datos y la evidencia puedan validarse de extremo a extremo.
4. Desarrollar el Módulo 4 tras aprobar las definiciones financieras y completar la clasificación de datos históricos. El contrato de asistencia se acuerda con RRHH antes de automatizar liquidaciones.
5. Completar el Módulo 5: asistencia aprobada como entrada del motor salarial e inventario apoyado en identidad, proyectos y confirmación de operaciones.

Cada incremento debe cubrir dominio, persistencia, contrato e interfaz, con migraciones revisables y recuperación de errores. Las recetas de ejecución se mantienen en los README de [backend](../backend/README.md) y [frontend](../frontend/README.md).

## Criterio de cierre de la fase

Demostrar los criterios de cada módulo mediante pruebas del dominio, integración con persistencia real y recorridos de interfaz, incluyendo permisos, fallos de conexión y concurrencia. Antes de activar restricciones sobre registros existentes, verificar su regularización y un procedimiento de recuperación. Registrar únicamente las comprobaciones efectivamente realizadas en la fuente de estado; aprobar esta planificación no equivale a entregar estas capacidades.
