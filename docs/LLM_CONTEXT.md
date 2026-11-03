# Contexto de Continuación para LLM

Última actualización: 2026-11-03. Rama de trabajo: `refactor/frontend-vite`.

## Orden de Lectura

1. [AGENT.md](AGENT.md): protocolo de trabajo, tipado, validación y commits.
2. [PROJECT_STATE.md](PROJECT_STATE.md): entregas realizadas y pendientes.
3. [06_fase3_frontend.md](06_fase3_frontend.md): checklist de la fase activa.
4. [README del frontend](../frontend/README.md) y [reglas del frontend](../frontend/AGENTS.md): instalación y detalles de la SPA.

Este archivo resume el punto de continuación; no sustituye la inspección de la rama, el árbol de trabajo ni el código. Los objetivos de arquitectura no prueban que una funcionalidad esté implementada.

## Entrega Actual

- Backend estable según las validaciones históricas registradas en `PROJECT_STATE.md`. No modificarlo durante tareas exclusivas de frontend o documentación.
- Migración de la base a React 19 + Vite: `e3f071c`.
- Corrección de dependencias de desarrollo: `b483990`. La auditoría de esa entrega informó cero vulnerabilidades; volver a consultar npm si se necesita un resultado vigente.
- Branding y panel principal: `312284e`. Navbar adaptable, Hero, tres tarjetas, menús, navegación y gráfico de barras implementados.
- Recursos gráficos y ajustes posteriores: `6ae6c07` y `85ae4aa`. La Navbar usa `/logo.png`; también existen `logo-white.png` y `favicon.ico`. El favicon activo de `index.html` sigue siendo `/favicon.svg`. Conservar los recursos y el ajuste del usuario; no sustituirlos por el emblema provisional `logo.svg`.
- Las métricas del panel son ejemplos explícitos: 1 / 70 obras, OPEX $84.000, CapEx $161.800 y total $245.800 CLP. No proceden de FastAPI.
- Las rutas `/proyectos`, `/gastos` y `/configuracion` muestran módulos en preparación. Los botones navegan, no crean ni modifican registros. El icono de usuario no acredita una sesión autenticada.
- Pendientes: cliente HTTP, consultas/mutaciones, listados y formularios, autenticación, carga de comprobantes, instalación PWA y sincronización offline.

## Mapa del Frontend

| Archivo o directorio | Responsabilidad |
| :--- | :--- |
| `frontend/src/main.tsx` | React, StrictMode, CSS y fuentes Inter locales |
| `frontend/src/App.tsx` | Proveedores de TanStack Query y Router |
| `frontend/src/router.ts` | Rutas tipadas, navegación y restauración de scroll |
| `frontend/src/query-client.ts` | Instancia global de QueryClient, sin cliente HTTP aún |
| `frontend/src/components/navbar.tsx` | Navegación, menú móvil y menú de usuario |
| `frontend/src/components/dashboard/` | Hero y tarjetas con datos de ejemplo |
| `frontend/src/components/ui/icon.tsx` | Iconos SVG tipados; sin dependencia de Lucide instalada |
| `frontend/src/pages/` | Inicio, vistas de módulo en preparación y página no encontrada |
| `frontend/src/index.css` | Tokens de marca, estilos compartidos y Tailwind CSS 4 |
| `frontend/public/` | Logo de empresa PNG, variante blanca, favicon ICO disponible y recursos SVG anteriores; verificar cuál referencia cada componente |

## Restricciones que Deben Conservarse

- TypeScript estricto, sin `any`; enrutamiento con TanStack Router y estado remoto con TanStack Query.
- Inter auto-alojada (400, 500, 600). No introducir fuentes, scripts ni estilos de CDNs externos.
- Paleta: `#0F172A`, `#2563EB`, `#1E40AF`, `#F8FAFC` y blanco. Reutilizar los tokens existentes.
- No sustituir la interfaz de demostración por cifras que aparenten ser datos reales. Al conectar FastAPI, implementar estados de carga, error y vacío y retirar las cifras de ejemplo donde corresponda.
- Conservar el lockfile y el override limitado de minimatch hasta revisar que los consumidores declaren versiones corregidas compatibles. No usar `npm audit fix --force` como corrección automática.
- Los recursos locales y el build sin descargas externas no equivalen a una aplicación completamente offline; aún no existe service worker.

## Comandos de Desarrollo y Validación

Node requerido por `package.json`: `^20.19.0 || ^22.13.0 || >=24`.

Desde `frontend/`:

```bash
npm ci
npm run dev
npm run lint
npm run build
```

El servidor de desarrollo usa el puerto 5173 por defecto. La instalación necesita registro npm; el build funciona sin red externa una vez instaladas las dependencias. Para comprobar `dist/`, usar `npm run preview`; el despliegue estático debe redirigir las rutas SPA a `index.html`.

Desde la raíz, `make check-frontend` ejecuta lint y build. En Windows, `.\check.ps1` también ejecuta backend y tests. En la entrega visual `312284e` solo se ejecutó su bloque frontend en PowerShell temporal, además de lint/build y comprobaciones de navegador; no atribuirle una ejecución completa del script ni nuevas pruebas del backend. Los ajustes posteriores de Navbar/logo no se revalidaron durante esta actualización exclusivamente documental.

Para cambios únicamente documentales, comprobar enlaces, consistencia con el código y `git diff --check`. Las validaciones históricas no deben presentarse como ejecuciones nuevas.

## Siguiente Trabajo Sugerido

Integrar FastAPI con funciones HTTP tipadas y TanStack Query, comenzando por listado y filtros de proyectos. Después implementar creación/actualización de obras y registro/consulta de gastos. Mantener las validaciones de negocio en el backend y conservar el diseño adaptable. Consultar el roadmap antes de ampliar el alcance.
