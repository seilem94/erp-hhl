# ⚡ ERP Eléctrico - Documentación de Arquitectura y Diseño

Este documento resume la estrategia arquitectónica, decisiones tecnológicas y la planificación para el desarrollo de un ERP modular diseñado para un emprendimiento eléctrico, optimizado para portabilidad móvil y self-hosting seguro con costo \$0.

---

## 🏗️ Stack Tecnológico Seleccionado

*   **Backend:** FastAPI (Python) + Pydantic v2
*   **Base de Datos:** PostgreSQL
*   **Frontend / UI:** React 19 + Vite (SPA) (Configurado como PWA - Progressive Web App)
    *   **Enrutamiento y Estado:** TanStack Router para navegación SPA tipada y TanStack Query para gestión de estado asíncrono y peticiones a FastAPI.
    *   **Estrategia de Fuentes:** Tipografías auto-alojadas (ej. `@fontsource/inter`) instaladas como dependencias npm y empaquetadas en el bundle de Vite. Prohibido el uso de Google Fonts externos (`fonts.googleapis.com`) para garantizar funcionamiento offline y evitar bloqueos en CI/CD.
    *   **Validación y Compilación:** Estándares de Vite (`eslint .` para linter y `tsc -b && vite build` para tipos y empaquetado).
*   **Infraestructura:** Docker & Docker Compose
*   **Red / Seguridad:** Cloudflare Tunnels o Tailscale (Exposición segura sin apertura de puertos en router)

---

## 📐 Filosofía Arquitectónica: Clean Architecture Pragmática

El sistema separa estrictamente las reglas de negocio de los detalles de infraestructura para garantizar mantenibilidad a largo plazo y facilitar la evolución del sistema.

### Estructura del Core (Backend)
1.  **`domain/` (Núcleo):** Entidades puras de Python. Define la estructura de datos y reglas lógicas de `Proyectos`, `Gastos` y `Trabajadores`. Cero dependencias externas.
2.  **`use_cases/` (Lógica de Aplicación):** Orquesta el flujo del negocio (ej. `RegistrarGastoDiario`, `CalcularLiquidacionSueldo`). Utiliza interfaces (abstracciones) para interactuar con el exterior.
3.  **`infrastructure/` (Mundo Exterior):** Implementación de base de datos (SQLAlchemy / SQLModel), controladores HTTP (FastAPI Routers), integraciones de red y configuración de Docker.

---

## 🗺️ Mapa de Ruta del Proyecto (Fases Sugeridas)

*   **Fase 1: El Núcleo y Datos (MVP):** Definición del modelo relacional en PostgreSQL y creación del dominio/casos de uso en FastAPI para el módulo crítico de Gastos y Proyectos.
*   **Fase 2: API e Inyección de Dependencias:** Implementación de repositorios de base de datos en FastAPI y exposición de endpoints seguros (Auth JWT).
*   **Fase 3: Frontend SPA / PWA (Interfaz Móvil):** Construcción de la interfaz en React 19 + Vite (SPA) con TanStack Router y TanStack Query, diseño responsivo y capacidades PWA para su uso rápido en terreno.
*   **Fase 4: Despliegue y DevOps:** Contenerización total con Docker Compose y configuración del túnel seguro en el servidor casero.

---

## 🤖 Prompt de Continuación para Modelos de IA (Gemini Pro/Flash)

Copia el siguiente prompt en tu chat de IA para iniciar el proceso de desarrollo guiado:

```text
Actúa como un Arquitecto de Software Senior, CTO y Especialista en DevOps con amplia experiencia en Python (FastAPI), React 19 + Vite (SPA), PostgreSQL y Self-Hosting. 

Voy a construir un pequeño ERP para mi emprendimiento eléctrico. El objetivo del sistema es centralizar operaciones, dar portabilidad móvil a mi socio en terreno y mantener los costos en \$0 usando self-hosting casero. El proyecto debe ser impecable a nivel de diseño de software para incluirlo en mi portafolio profesional.

Los requerimientos clave del negocio son:
1. Gestión de proyectos eléctricos y asignación de trabajadores a obras.
2. Registro de finanzas en terreno: gastos diarios (transporte, comida, compras a proveedores).
3. Liquidación y pago de sueldos al finalizar cada proyecto.
4. Acceso móvil (vía React 19 + Vite (SPA)) para el socio en terreno y de escritorio para tareas complejas.

Para lograr esto, hemos decidido usar Clean Architecture (adaptada de forma pragmática para evitar sobreingeniería), FastAPI en el Backend, PostgreSQL como Base de Datos y React 19 + Vite (SPA) en el Frontend (con TanStack Router y TanStack Query). Todo correrá en Docker dentro de un servidor casero seguro (usando Cloudflare Tunnels o Tailscale).

Quiero que me ayudes a depurar el diseño técnico y planificar el proyecto en fases lógicas de desarrollo. Para esta primera interacción, por favor provéeme lo siguiente:

1. MAPA DE RUTA EN FASES: Divide el proyecto en 4 fases secuenciales (desde el MVP funcional hasta el despliegue e infraestructura en el servidor casero). Cada fase debe tener objetivos claros y qué entregable técnico se obtiene al final.
2. ARQUITECTURA DE CARPETAS (BACKEND): Muestra la estructura exacta de carpetas para el backend en FastAPI siguiendo Clean Architecture (capas de Domain, Use Cases e Infrastructure), específicamente aplicada al módulo de "Gestión de Gastos Diarios".
3. CONSEJO DE ENFOQUE: ¿Cuál es el error más común al implementar el patrón Repository con FastAPI + SQLAlchemy/SQLModel y cómo debo evitarlo para que mi capa de Dominio no se contamine con la base de datos?

Mantén un tono profesional, técnico, directo y enfocado en buenas prácticas de producción. No uses introducciones genéricas ni resúmenes innecesarios. Vamos directo al diseño.
```
