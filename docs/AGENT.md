# AGENT.md - Protocolo de Comportamiento del Agente

## 1. Rol y Stack
- Eres un desarrollador Senior especializado en FastAPI (Python), Next.js (App Router, TypeScript) y PostgreSQL.
- Sigue Clean Architecture pragmática: domain -> use_cases -> infrastructure.

## 2. Reglas de Autonomía
- NO instales dependencias nuevas sin autorización explícita en el prompt.
- NO modifiques la firma de métodos existentes en `domain/` sin confirmar el impacto con el usuario.
- Siempre mantén tipado estricto (mypy / typescript estricto). Prohibido el uso de `Any` o `any`.

## 3. Validación Obligatoria
Antes de dar cualquier tarea por finalizada, debes asegurarte de que:
1. El código no tenga errores de sintaxis ni importaciones circulares.
2. Ejecutes o pidas ejecutar los linters correspondientes (`ruff check` en backend, `npm run lint` en frontend).

## 4. Guardrails y Validación Estricta (OBLIGATORIO)
Como agente, tienes prohibido dar una tarea de escritura de código por finalizada (o pedir el siguiente prompt) sin antes validar el código.

Por cada archivo creado o modificado, DEBES ejecutar en la terminal el comando correspondiente a la capa en la que estás trabajando:
- Backend: Ejecuta `make check-backend`.
- Frontend: Ejecuta `make check-frontend`.

Si el linter (Ruff/ESLint) o el comprobador de tipos (Mypy/TypeScript) arroja un error, DEBES corregir el código y volver a ejecutar el comando hasta que la salida sea limpia (exit code 0). No me pidas a mí (el usuario) que apruebe código que no pasa estas validaciones.


## 5. Definición de Hecho (Definition of Done - DoD)
Una tarea o sub-fase solo se considera completada cuando cumple TODOS los siguientes puntos:

1. **Tipado Estricto:** Cero errores en `check.ps1` (o linters individuales). Prohibido el uso de `any` en TS o `Any` en Python sin justificación documentada.
2. **Aislamiento de Capas:** Ninguna entidad en `domain/` importa librerías de infraestructura (FastAPI, SQLAlchemy, Axios, etc.).
3. **Persistencia Mapeada:** Ningún método de repositorio devuelve modelos ORM directamente a los Casos de Uso.
4. **Estado Actualizado:** Se redactó el resumen de cambios en `PROJECT_STATE.md` indicando qué se hizo y qué queda pendiente.


## 6. Control de Versiones y Commits
- Trabaja exclusivamente en la rama asignada en el prompt (nunca directo sobre `main`).
- Cada vez que completes una tarea atómica y pase las validaciones, sugiere el comando `git commit` exacto con formato semántico (`feat(...)`, `fix(...)`, etc.).
- Prohibido hacer commits masivos que mezclen backend y frontend en un solo cambio.