# Reglas de arquitectura del backend

Esta es la fuente canónica de restricciones de diseño de las capas. El motivo de la separación se registra en el [ADR fundacional](adr/0000-stack-y-clean-architecture.md).

1. **Dependencia unidireccional:** infraestructura depende de casos de uso y estos del dominio. El dominio no importa frameworks, ORM ni transporte HTTP.
2. **Entidades puras:** el dominio usa dataclasses y tipos de negocio; los DTO de transporte y los modelos de persistencia pertenecen a infraestructura.
3. **Mapeo obligatorio:** los repositorios concretos convierten modelos ORM en entidades de dominio antes de devolver resultados. No filtrar modelos ORM a los casos de uso.
4. **Inyección por contratos:** los casos de uso reciben interfaces de repositorio. La capa HTTP resuelve sus implementaciones y dependencias.
5. **Transacciones:** los repositorios utilizan flush, sin commit. La dependencia de sesión confirma al completar una petición y revierte ante excepciones.
6. **Aislamiento HTTP:** los routers ejecutan casos de uso; no contienen consultas ORM ni reglas de negocio.
7. **Determinismo:** inyectar la fuente de fecha cuando un caso de uso necesite pruebas temporales reproducibles.

Los códigos, cuerpos y parámetros de la API se definen en sus routers y esquemas, referenciados desde el [mapa de infraestructura](04_fase2_infraestructura.md); no se mantienen catálogos paralelos aquí.
