# Reglas Estrictas de Backend (Clean Architecture)

1. DEPENDENCIA UNIDIRECCIONAL: `infrastructure` depende de `use_cases`, y `use_cases` depende de `domain`. El `domain` NO tiene dependencias de frameworks (ni FastAPI, ni SQLAlchemy).
2. AISLAMIENTO DE BASE DE DATOS: Los repositorios en `infrastructure` DEBEN mapear los objetos ORM a entidades puras de Python (`domain/entities`) antes de retornarlos. Nunca filtrar un objeto ORM a un caso de uso.
3. INYECCIÓN DE DEPENDENCIAS: Los casos de uso reciben interfaces (ABCs) de los repositorios en su constructor. FastAPI inyecta las implementaciones reales en las rutas.
4. ESTADO HTTP: Usar códigos HTTP estándar (201 para creación, 404 no encontrado, 422 error de validación Pydantic).