# 0000. Separación del núcleo mediante Clean Architecture

- **Fecha original:** 2026-11-01
- **Consolidación documental:** 2026-11-03
- **Estado:** Aceptado

## Contexto

Las reglas de obras y gastos deben poder evolucionar y probarse sin depender de la base de datos ni del transporte HTTP. Mezclar entidades ORM con resultados de negocio introduciría acoplamiento y acceso implícito a persistencia.

## Decisión

Separar dominio, casos de uso e infraestructura, con contratos de repositorio y conversión explícita entre representaciones persistidas y entidades puras. Las restricciones de implementación se mantienen únicamente en [reglas de arquitectura](../02_reglas_arquitectura.md).

La selección del cliente web se registra de forma independiente en el [ADR de migración](0001-migracion-react-vite.md).

## Consecuencias

- **Positivas:** pruebas del núcleo independientes y sustitución de infraestructura sin trasladar detalles de persistencia a los casos de uso.
- **Compensaciones:** contratos, mappers y conversiones adicionales que deben mantenerse coherentes.

## Trazabilidad

Este registro conserva la decisión fundacional del antiguo archivo `0001-stack-y-clean-architecture.md`. Se renumera a 0000 para reservar 0001 a la migración solicitada; el archivo anterior permanece como enlace de compatibilidad. La plantilla no constituye una decisión numerada.
