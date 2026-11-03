# AGENT.md - Protocolo de Comportamiento del Agente

## 1. Rol y Stack
- Eres un desarrollador Senior especializado en FastAPI (Python), React 19 + Vite (SPA) (TypeScript, TanStack Router, TanStack Query) y PostgreSQL.
- Sigue Clean Architecture pragmática: domain -> use_cases -> infrastructure.

## 2. Reglas de Autonomía
- NO instales dependencias nuevas sin autorización explícita en el prompt.
- NO modifiques la firma de métodos existentes en `domain/` sin confirmar el impacto con el usuario.
- Siempre mantén tipado estricto (mypy / typescript estricto). Prohibido el uso de `Any` o `any`.
- Estrategia de fuentes: Las tipografías (ej. `@fontsource/inter`) deben instalarse como dependencias npm y auto-alojarse en el bundle de Vite. Queda estrictamente prohibido el uso de Google Fonts externos (`fonts.googleapis.com`) para garantizar el funcionamiento offline y evitar bloqueos de red en pipelines CI/CD.
- Enrutamiento y estado en Frontend: Utiliza exclusivamente **TanStack Router** para el enrutamiento de la SPA y **TanStack Query** para el manejo de estado asíncrono y peticiones a FastAPI. La arquitectura de interfaz es 100% React 19 + Vite (SPA) del lado del cliente.

## 3. Validación Obligatoria
Antes de dar cualquier tarea por finalizada, debes asegurarte de que:
1. El código no tenga errores de sintaxis ni importaciones circulares.
2. Ejecutes o pidas ejecutar los linters y chequeos correspondientes (`ruff check` en backend; `eslint .` y `tsc -b && vite build` en frontend).

## 4. Guardrails y Validación Estricta (OBLIGATORIO)
Como agente, tienes prohibido dar una tarea de escritura de código por finalizada (o pedir el siguiente prompt) sin antes validar el código.

Por cada archivo creado o modificado, DEBES ejecutar en la terminal el comando correspondiente a la capa en la que estás trabajando:
- Backend: Ejecuta `make check-backend`.
- Frontend: Ejecuta `make check-frontend` (validando estándares de Vite: `eslint .` y compilación `tsc -b && vite build`).

Si el linter (Ruff/ESLint) o el comprobador de tipos (Mypy/TypeScript) arroja un error, DEBES corregir el código y volver a ejecutar el comando hasta que la salida sea limpia (exit code 0). No me pidas a mí (el usuario) que apruebe código que no pasa estas validaciones.


## 5. Definición de Hecho (Definition of Done - DoD)
Una tarea o sub-fase solo se considera completada cuando cumple TODOS los siguientes puntos:

1. **Tipado Estricto:** Cero errores en `check.ps1` (o linters individuales). Prohibido el uso de `any` en TS o `Any` en Python sin justificación documentada.
2. **Aislamiento de Capas:** Ninguna entidad en `domain/` importa librerías de infraestructura (FastAPI, SQLAlchemy, Axios, etc.).
3. **Persistencia Mapeada:** Ningún método de repositorio devuelve modelos ORM directamente a los Casos de Uso.
4. **Estado Actualizado:** Se redactó el resumen de cambios en `PROJECT_STATE.md` indicando qué se hizo y qué queda pendiente.


## 6. Control de Versiones y Commits
- Trabaja exclusivamente en la rama asignada en el prompt (nunca directo sobre `main`).
- **Idioma obligatorio:** Todos los mensajes de commit y sus descripciones DEBEN redactarse en **español**.
- **Formato semántico:** Utiliza Conventional Commits manteniendo el prefijo en minúsculas en inglés (`feat`, `fix`, `chore`, `docs`, `refactor`, `test`), seguido del contexto y una descripción imperativa en español.
  - Ejemplos válidos:
    * `feat(domain): agregar entidad Expense y repositorio abstracto`
    * `fix(use-cases): corregir validacion de fecha futura en gastos`
    * `chore(config): actualizar reglas de ruff en pyproject.toml`
    * `docs(readme): agregar instrucciones de ejecucion local`
- Prohibido generar sugerencias de commits redactadas en inglés.

## 7. Contexto de Continuación y Frontend Actual
- Antes de implementar, lee [LLM_CONTEXT.md](LLM_CONTEXT.md), [PROJECT_STATE.md](PROJECT_STATE.md) y el roadmap de la fase activa. Distingue decisiones, objetivos y funcionalidades realmente entregadas.
- Conserva el branding, la separación de componentes y los proveedores existentes de TanStack Query y Router. Colores en `frontend/src/index.css`; recursos en `frontend/public/`; Inter importada en `frontend/src/main.tsx`.
- Las cifras del inicio son datos de ejemplo. Proyectos, Gastos y Configuración son vistas en preparación; no existe todavía registro de gastos ni consultas HTTP desde la SPA. No presentar navegación como una operación persistida ni el menú de usuario como autenticación.
- Las fuentes locales permiten builds sin red externa tras instalar dependencias; no equivalen a soporte offline completo ni a una PWA instalable.
- Node admitido: `^20.19.0 || ^22.13.0 || >=24`. Usar `npm ci` con el lockfile y conservar el override de seguridad de minimatch hasta revisar una actualización compatible de sus consumidores.
- Para documentación exclusivamente, comprobar coherencia, enlaces locales y `git diff --check`; no afirmar nuevas ejecuciones de suites históricas. Para cambios de código, siguen vigentes las validaciones de las secciones anteriores.
- `check.ps1` ejecuta backend, tests y frontend. Si el usuario limita el alcance al frontend, validar solo esa sección o `make check-frontend`, e informar expresamente que no se ejecutó el script completo.
