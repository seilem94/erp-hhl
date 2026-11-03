# Índice documental y fuentes canónicas

## Fuentes canónicas

Cada documento mantiene exclusivamente el tema asignado. Las referencias de navegación no sustituyen a sus fuentes.

| Tema | Única fuente documental |
| :--- | :--- |
| Presentación, stack de alto nivel y arranque rápido | [README raíz](../README.md) |
| Objetivos y usuarios del producto | [Contexto](01_contexto_erp.md) |
| Normas de trabajo y responsabilidad documental | [AGENT](AGENT.md) |
| Entregas, pendientes y evidencia de validación | [PROJECT_STATE](PROJECT_STATE.md) |
| Preparación Python, conexión, migraciones y pruebas | [README del backend](../backend/README.md) |
| Operación, estructura y recursos de la interfaz | [README del frontend](../frontend/README.md) |
| Restricciones de diseño de las capas | [Reglas de arquitectura](02_reglas_arquitectura.md) |
| Preguntas y acuerdos de uso con el socio | [Guía de reunión](05_revision_mvp_socio.md) |
| Justificación y compensaciones de decisiones | Cada ADR del registro siguiente |

El código y sus manifiestos son la autoridad de contratos, versiones, scripts y configuración. No mantener catálogos manuales que compitan con ellos.

## Planes de trabajo

- [Fase 1: dominio y casos de uso](03_fase1_mvp.md).
- [Fase 2: persistencia y API](04_fase2_infraestructura.md).
- [Fase 3: integración de la interfaz](06_fase3_frontend.md).

Los planes definen secuencias y criterios; no repiten estados de avance. Para comenzar una sesión, seguir el [itinerario LLM](LLM_CONTEXT.md).

## Registro de decisiones

| ID | Decisión |
| :--- | :--- |
| 0000 | [Separación del núcleo mediante Clean Architecture](adr/0000-stack-y-clean-architecture.md) |
| 0001 | [Migración de Next.js a React + Vite](adr/0001-migracion-react-vite.md) |

Usar la [plantilla ADR](adr/0000-plantilla-adr.md) para decisiones futuras; la plantilla no es un registro aceptado. La fecha, el estado y las consecuencias de cada decisión se mantienen solo en su archivo.

## Auditoría de consolidación

| Documento depurado | Cambio de responsabilidad |
| :--- | :--- |
| README raíz | Se retiraron recetas de migración, arquitectura detallada y afirmaciones de PWA o Compose disponibles |
| README del backend, nuevo | Se centralizaron entorno virtual, configuración, Alembic y Pytest |
| README y AGENTS del frontend | Se separaron instrucciones del componente de estado, planificación y normas generales |
| AGENT | Se centralizaron reglas del agente y se añadió la obligación SSOT/DRY |
| PROJECT_STATE | Se conservaron entregas y evidencia histórica; se retiraron copias de recetas y decisiones |
| LLM_CONTEXT | Se sustituyó la réplica del proyecto por un itinerario de enlaces |
| Contexto de producto | Se retiraron stack e informe de implementación |
| Reglas de arquitectura | Se centralizaron las restricciones antes dispersas en planes y estado |
| Planes de fases 1, 2 y 3 | Se retiraron estados duplicados, comandos y catálogos de contrato; se conservaron secuencias y criterios |
| Guía con el socio | Se retiraron afirmaciones de funcionalidades y se conservaron preguntas y acuerdos de UX |
| Arquitectura_Inicial | Se retiró el prompt de reinicialización; se mantuvo una referencia histórica |
| ADR fundacional | Se separó la decisión del núcleo y se renumeró a 0000, preservando su ruta anterior como referencia |
| ADR de migración, nuevo | Se registraron exclusivamente contexto, decisión y consecuencias del pivote |
| Este índice | Se eliminaron copias del estado y se registró la propiedad de cada tema |

La información retirada sigue disponible en el historial de Git. No se modifican código, configuración ejecutable ni dependencias por esta consolidación.

## Propuestas documentales — No creadas

1. `adr/0002-autenticacion-spa.md`: decidir sesión, expiración, almacenamiento y permisos antes de conectar la identidad del usuario.
2. `adr/0003-sincronizacion-offline.md`: decidir idempotencia, cola, conflictos y política de caché antes de permitir escrituras sin conexión.
3. `operacion/despliegue-y-recuperacion.md`: procedimiento probado de publicación, backups y restauración cuando se retome la operación de producción.

Estos documentos aportarían responsabilidades todavía no cubiertas. No deben duplicar el contrato OpenAPI, las recetas locales de los componentes ni el estado de entrega.
