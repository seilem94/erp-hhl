# ⚡ Frontend — HHL ERP (React 19 + Vite SPA)

Base de la interfaz de HHL ERP, generada con la plantilla oficial `react-ts` de Vite. Aplicación de cliente con TypeScript estricto, TanStack Router y TanStack Query.

---

## 🛠️ Stack Tecnológico

| Herramienta | Propósito |
| :--- | :--- |
| **React 19 + Vite** | SPA con desarrollo HMR y compilación estática |
| **TypeScript** | Tipado estricto, sin `any` |
| **TanStack Router** | Ruta de inicio y página no encontrada con navegación tipada |
| **TanStack Query** | `QueryClient` y proveedor global para la futura integración con FastAPI |
| **Tailwind CSS 4** | Utilidades CSS procesadas con `@tailwindcss/postcss` y Autoprefixer |
| **@fontsource/inter** | Inter auto-alojada, con pesos 400, 500 y 600 del subconjunto latino |

---

## 🚀 Puesta en Marcha

Requiere Node.js 20.19+ o 22.12+ y npm. Ejecutar desde `frontend/`:

```bash
npm ci
npm run dev
```

Vite utiliza el puerto `5173` por defecto. El alias `@/` apunta a `src/` tanto en Vite como en TypeScript.

---

## 🔍 Comandos de Validación y Compilación

```bash
# ESLint:
npm run lint

# TypeScript y compilación de producción (tsc -b && vite build):
npm run build

# Servir localmente el resultado de dist/:
npm run preview
```

Desde la raíz del repositorio, `make check-frontend` ejecuta lint y build. `check.ps1` utiliza las mismas validaciones de frontend y propaga sus errores.

La instalación inicial necesita acceso al registro npm. Una vez instaladas las dependencias, la compilación funciona sin acceso a red externa y genera HTML, JavaScript, CSS y fuentes locales en `dist/`.

Para desplegar, servir `dist/` con un servidor estático que redirija las rutas de la SPA a `index.html`. `vite preview` sirve para comprobar la compilación localmente, no como servidor de producción.

---

## 🔤 Estrategia de Fuentes (Offline-First)

Inter se importa desde `@fontsource/inter` en `src/main.tsx`. Vite copia los archivos `.woff` y `.woff2` a `dist/assets/`; el navegador los obtiene del mismo servidor que la aplicación. No se utilizan hojas de estilo, fuentes ni scripts desde CDNs externos.

Esta base no incluye todavía un service worker ni una cola de operaciones offline. Las capacidades PWA completas y la integración funcional con FastAPI siguen pendientes según `docs/06_fase3_frontend.md`.
