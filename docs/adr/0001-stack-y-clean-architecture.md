# 0001. Clean Architecture y Stack Base

* **Fecha:** 2026-11-01
* **Estado:** Aceptado

## Contexto
El sistema debe gestionar proyectos, gastos y sueldos para un emprendimiento eléctrico, operando en servidor local sin costo y con clientes móviles y de escritorio.

## Decisión
1. Se adopta Clean Architecture pragmática (Domain, Use Cases, Infrastructure).
2. Backend: FastAPI + Pydantic v2 + SQLAlchemy (con mapeo estricto a entidades puras).
3. Frontend: Next.js (App Router, React 19, TypeScript estricto, Tailwind CSS).
4. Persistencia: PostgreSQL con claves primarias tipo UUIDv4.

## Consecuencias
* **Positivas:** Desacoplamiento total de la lógica de negocio frente a la base de datos y frameworks.
* **Negativas:** Mayor cantidad de código inicial (boilerplate) debido a los mappers y clases abstractas.