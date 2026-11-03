# Plan de Fase 1 — Dominio y casos de uso

Responsabilidad: secuencia de construcción del núcleo de negocio. El grado de entrega se registra únicamente en [PROJECT_STATE.md](PROJECT_STATE.md).

## Secuencia

1. Definir entidades y enumeraciones del negocio en el [dominio](../backend/src/domain/).
2. Establecer contratos de repositorio sin detalles de persistencia.
3. Implementar registro y consultas de gastos, y creación, consulta y actualización de proyectos en [casos de uso](../backend/src/use_cases/).
4. Verificar las reglas con repositorios falsos y fuentes temporales deterministas.

## Criterio de salida

Los casos de uso deben poder ejecutarse sin transporte HTTP ni base real, cumpliendo las [reglas de arquitectura](02_reglas_arquitectura.md). La preparación y ejecución de pruebas se documenta en el [README del backend](../backend/README.md#pruebas-con-pytest).
