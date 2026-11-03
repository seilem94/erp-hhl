# Plan de Fase 3 — Integración de la interfaz

Responsabilidad: secuencia de trabajo y criterios de aceptación. Los avances y las validaciones realizadas se registran exclusivamente en [PROJECT_STATE.md](PROJECT_STATE.md).

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
