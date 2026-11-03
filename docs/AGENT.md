# AGENT.md — Protocolo del agente

## Lectura inicial

Consultar [LLM_CONTEXT.md](LLM_CONTEXT.md) para localizar las fuentes del trabajo. Las instrucciones explícitas del usuario delimitan el alcance y prevalecen sobre este protocolo.

## Autonomía y código

- Trabajar únicamente en la rama asignada; preservar los cambios ajenos. No hacer reset destructivo ni sobrescribir el remoto para resolver divergencias.
- No instalar nuevas dependencias sin autorización explícita ni modificar firmas del dominio sin confirmar su impacto.
- Mantener tipado estricto, sin `Any` ni `any` sin justificación documentada.
- Respetar las [reglas de arquitectura](02_reglas_arquitectura.md) y las decisiones aceptadas del [registro ADR](README.md#registro-de-decisiones).
- No presentar datos de ejemplo, navegación o maquetas como operaciones reales ni como autenticación implementada.

## Validación

Para cambios de código, ejecutar desde la raíz la comprobación correspondiente:

- Backend: `make check-backend`; añadir las pruebas relevantes descritas en el [README del backend](../backend/README.md#pruebas-con-pytest).
- Frontend: `make check-frontend`; las comprobaciones individuales se mantienen en el [README del frontend](../frontend/README.md#scripts-disponibles).

Corregir los fallos antes de declarar la entrega validada. Informar qué se ejecutó, qué falló y qué se omitió. `check.ps1` abarca ambas capas y tests; si el alcance excluye una capa, ejecutar solo las comprobaciones autorizadas y no afirmar que se ejecutó el script completo.

Para cambios exclusivamente documentales, revisar enlaces, referencias, coherencia y `git diff --check`. No presentar resultados históricos como ejecuciones nuevas.

## Responsabilidad Única en Documentación — SSOT / DRY

**Regla estricta:** ningún documento debe duplicar instrucciones, reglas, catálogos, estado o decisiones cuyo propietario sea otro documento. Cada tema tiene una única fuente canónica, registrada en la [matriz de responsabilidades](README.md#fuentes-canónicas).

- Enlazar al documento propietario; no copiar su contenido, ni siquiera como resumen operativo que deba mantenerse por separado.
- El README raíz contiene únicamente presentación, stack de alto nivel, accesos y comandos rápidos de entrada. No explica Alembic: enlaza al README del backend. Las recetas completas pertenecen al componente.
- Registrar avances y evidencia solamente en PROJECT_STATE; mantener la secuencia y criterios de trabajo en los planes de fase, sin repetir checklists de estado.
- Documentar el motivo de una decisión en su ADR, sin convertirlo en guía de instalación ni informe de avance.
- Ante un cambio, actualizar la fuente propietaria y los enlaces afectados. Eliminar la versión redundante o conservar únicamente una referencia de compatibilidad.
- Las versiones, scripts, contratos y configuración ejecutables siguen teniendo como autoridad el código y sus manifiestos; la documentación los explica, no los reemplaza.
- Antes de crear un documento, comprobar que su responsabilidad no esté cubierta. Las propuestas documentales no se materializan hasta ser solicitadas.

## Cierre y control de versiones

Actualizar la fuente de estado cuando cambie una entrega. Mantener el alcance: completar una tarea documental no autoriza cambios de aplicación.

Usar Conventional Commits con prefijo en minúsculas y descripción imperativa en español, por ejemplo `docs: consolidar documentación bajo SSOT`. Si el usuario pide solo una propuesta de commit, no crear el commit ni ejecutar push.
