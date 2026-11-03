# Documentación de HHL ERP

## Continuar el Desarrollo

- [Contexto para LLM](LLM_CONTEXT.md): resumen de continuidad, archivos clave, comandos y límites de lo entregado.
- [Protocolo del agente](AGENT.md): reglas de implementación, validación y control de versiones.
- [Estado del proyecto](PROJECT_STATE.md): hitos completados, rama activa, validaciones y pendientes.
- [Roadmap de frontend](06_fase3_frontend.md): checklist actualizado de la Fase 3.

## Contexto y Arquitectura

- [Objetivo y usuarios](01_contexto_erp.md).
- [Reglas de arquitectura del backend](02_reglas_arquitectura.md).
- [Arquitectura inicial](Arquitectura_Inicial.md): decisiones y planificación histórica; el estado vigente está en `PROJECT_STATE.md`.
- [ADR del stack y Clean Architecture](adr/0001-stack-y-clean-architecture.md).
- [Plantilla de ADR](adr/0000-plantilla-adr.md).

## Planificación y Revisión Funcional

- [Fase 1: núcleo y dominio](03_fase1_mvp.md).
- [Fase 2: infraestructura y API](04_fase2_infraestructura.md).
- [Guía de revisión con el socio](05_revision_mvp_socio.md): capacidades de backend y objetivos de UX, sin asumir que ya existen los formularios móviles.
- [Guía de ejecución del frontend](../frontend/README.md).

## Estado al 2026-11-03

La base React 19 + Vite y el diseño visual del inicio están implementados. El panel usa datos de ejemplo; los módulos de Proyectos, Gastos y Configuración son vistas en preparación. La integración HTTP, los formularios, la autenticación y el funcionamiento PWA/offline completo siguen pendientes.
