# Protocolo del Frontend — React 19 + Vite (SPA)

## 1. Stack Tecnológico
- **Base:** React 19 + Vite con TypeScript en modo estricto.
- **Enrutamiento:** TanStack Router (enrutamiento de cliente 100% tipado en React 19 + Vite (SPA)).
- **Estado Asíncrono / API:** TanStack Query para peticiones a la API de FastAPI.
- **Estilos:** Tailwind CSS y Lucide Icons.
- **Fuentes:** Tipografías auto-alojadas con dependencias npm (ej. `@fontsource/inter`).

## 2. Reglas Estrictas
- **Prohibición de Google Fonts externos:** Prohibido importar o enlazar a `fonts.googleapis.com` o CDNs externos. Todas las tipografías deben auto-alojarse en el bundle local para funcionamiento offline y pipelines CI/CD sin red.
- **Arquitectura SPA de cliente:** No utilizar componentes de servidor o dependencias acopladas a servidor; la aplicación es puramente React 19 + Vite (SPA).
- **Tipado estricto:** Prohibido el uso de `any`.

## 3. Comandos de Validación
- Linter: `eslint .`
- Tipos y Build: `tsc -b && vite build`
