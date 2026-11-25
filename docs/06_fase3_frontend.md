# Plan de Fase 3 — Integración de la interfaz

Responsabilidad: secuencia de trabajo, criterios de aceptación y referencias a los flujos funcionales. Los avances y las validaciones realizadas se registran exclusivamente en [PROJECT_STATE.md](PROJECT_STATE.md).

Las razones de arquitectura están en el [ADR de migración](adr/0001-migracion-react-vite.md). La estructura, el branding y los comandos pertenecen al [README del frontend](../frontend/README.md).

## 1. Cliente HTTP y estado remoto

Definir funciones tipadas que consuman el contrato de la API sin introducir persistencia en componentes de presentación. Normalizar errores y diferenciar carga, vacío y fallo. Integrar las consultas y mutaciones con el proveedor existente e invalidar las consultas afectadas al confirmar cambios.

**Aceptación:** datos consultados verificables, fallos visibles y ausencia de métricas ficticias presentadas como resultados reales.

## 2. Obras y gastos

Sustituir progresivamente las vistas en preparación por listados, filtros y formularios. Permitir consultar detalles de una obra y distinguir costos asociados de gastos generales. Utilizar los criterios de interacción acordados en la [revisión con el socio](05_revision_mvp_socio.md).

**Aceptación:** formularios tipados, validación de entrada, estados de envío y recuperación de errores; el cliente no reemplaza las reglas de negocio del servicio.

## 3. Identidad y preferencias

Definir el flujo de autenticación, expiración y permisos antes de conectar el menú de usuario a una identidad real. Precisar qué preferencias se conservan y con qué alcance.

**Aceptación:** rutas protegidas y permisos basados en un contrato de seguridad aprobado; un icono de usuario no prueba autenticación.

## 4. Comprobantes

Acordar formatos, límites, almacenamiento y tratamiento de archivos antes de habilitar cámara o carga. Asociar el resultado al gasto mediante el contrato correspondiente.

**Aceptación:** límites visibles, errores recuperables y verificación de acceso al comprobante.

## 5. PWA y operación offline

Diseñar manifiesto, service worker, caché de recursos y datos, política de actualización y cola de operaciones. Definir identificación de solicitudes, reintentos y resolución de conflictos antes de habilitar escrituras offline.

**Aceptación:** comprobar instalación, recarga sin señal, actualización de recursos y recuperación de operaciones sin duplicación. Auto-alojar fuentes no satisface por sí solo estos criterios.

## Referencias de los flujos

- **Obras.** En **Nueva obra**, nombre y cliente son obligatorios y el presupuesto es opcional. El desplegable **+ Más detalles (opcional)** permite añadir descripción, estado inicial y fechas de inicio y entrega. Al guardar, el formulario se limpia y el desplegable vuelve a cerrarse. El listado muestra la descripción y la entrega cuando existen. El editor del detalle permite cambiar nombre, cliente, presupuesto y estado. [Formulario de alta](../frontend/src/components/projects/project-form.tsx) y [editor de obras](../frontend/src/components/projects/project-edit-form.tsx).
- **Gastos.** El registro pide **Título**, permite añadir **Detalle** y ofrece la casilla **Tiene comprobante**, desmarcada al abrir el formulario. El listado muestra el detalle debajo del título cuando tiene contenido. La acción **Editar** abre un modal precargado desde el historial y el detalle de la obra. **Guardar cambios** actualiza las consultas afectadas. **Cancelar** descarta la edición y los errores de guardado conservan los valores ingresados. [Registro de gastos](../frontend/src/components/expenses/expense-form.tsx), [listado](../frontend/src/components/expenses/expense-list.tsx) y [editor](../frontend/src/components/expenses/expense-edit-dialog.tsx).
- **Bitácora.** La ruta `/auditoria` se abre desde la navegación principal. **Actividad de la obra** usa el mismo componente con el proyecto ya seleccionado. Cada fila muestra autor, fecha y hora locales, acción, resumen y obra asociada cuando corresponde. [Página de Auditoría](../frontend/src/pages/auditoria.tsx), [detalle de obra](../frontend/src/pages/proyecto-detalle.tsx) y [lista de actividad](../frontend/src/components/audit/audit-log-list.tsx).

Los nombres de campos y las rutas HTTP pertenecen a los [contratos de proyectos, gastos y auditoría](04_fase2_infraestructura.md#contratos-de-proyectos-gastos-y-auditoría).
