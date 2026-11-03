# 0001. Clean Architecture y Stack Base

* **Fecha:** 2026-11-01
* **Estado:** Aceptado

## Contexto
El sistema debe gestionar proyectos, gastos y sueldos para un emprendimiento eléctrico, operando en servidor local sin costo y con clientes móviles y de escritorio.

## Decisión
1. Se adopta Clean Architecture pragmática (Domain, Use Cases, Infrastructure).
2. Backend: FastAPI + Pydantic v2 + SQLAlchemy (con mapeo estricto a entidades puras).
3. Frontend: React 19 + Vite (SPA) (TypeScript estricto, Tailwind CSS, TanStack Router para enrutamiento SPA y TanStack Query para gestión de estado y peticiones a FastAPI). Tipografías auto-alojadas con @fontsource/inter dentro del bundle de Vite, prohibiendo fuentes externas (fonts.googleapis.com) para evitar descargas externas durante el build tras instalar dependencias. El soporte offline completo requiere trabajo adicional de PWA y sincronización. Validación con eslint . y tsc -b && vite build.
4. Persistencia: PostgreSQL con claves primarias tipo UUIDv4.

## Consecuencias
* **Positivas:** Desacoplamiento total de la lógica de negocio frente a la base de datos y frameworks. En frontend, adopción de React 19 + Vite (SPA) con arquitectura ligera, compilación instantánea, enrutamiento fuertemente tipado con TanStack Router, gestión óptima de caché con TanStack Query y recursos estáticos auto-alojados sin dependencia de CDNs externos como Google Fonts. Esto no proporciona por sí solo persistencia ni sincronización offline.
* **Negativas:** Mayor cantidad de código inicial (boilerplate) debido a los mappers y clases abstractas.

## Estado de Adopción (2026-11-03)

La SPA y el branding están implementados; las rutas de módulos aún son vistas en preparación. TanStack Query dispone de un proveedor global, sin integración HTTP. PWA, autenticación y operaciones offline siguen pendientes. El detalle de entrega se mantiene en [PROJECT_STATE.md](../PROJECT_STATE.md).
