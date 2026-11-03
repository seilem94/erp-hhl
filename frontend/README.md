# HHL ERP — Frontend

Fuente canónica para instalar, desarrollar y publicar la interfaz. La entrega vigente se consulta en [PROJECT_STATE](../docs/PROJECT_STATE.md); el trabajo futuro, en el [plan de frontend](../docs/06_fase3_frontend.md).

## Instalación y desarrollo

Requiere npm y una versión de Node compatible con `engines` en [package.json](package.json). Los manifiestos y el lockfile determinan las versiones instaladas.

Desde `frontend/`:

```bash
npm ci
npm run dev
```

La instalación inicial necesita registro npm. Vite utiliza el puerto 5173 por defecto y anuncia en la terminal cualquier puerto alternativo. Para exigir uno concreto:

```bash
npm run dev -- --port 5173 --strictPort
```

## Configuración de la API

El cliente usa `VITE_API_BASE_URL` como origen de la API, sin añadir `/api/v1` al valor de configuración. La referencia de configuración local está en [.env.example](.env.example); copiarla a `.env.local` si necesitas un origen distinto al predeterminado y reiniciar Vite.

La variable se incorpora al build: definirla antes de compilar para publicar en otro entorno. Las variables `VITE_*` son públicas y no deben contener credenciales. El servicio debe permitir mediante CORS el origen desde el que se sirve la interfaz.

Los DTO se mantienen en `src/api/types.ts` y se contrastan con `/openapi.json` del servicio. El cliente usa `fetch`, comprueba las respuestas y normaliza errores HTTP, validaciones y fallos de conexión. No reintenta automáticamente las altas ni las deja en cola al detectar desconexión: si no puede confirmar un envío, conserva los datos del formulario y se debe revisar el listado antes de repetirlo.

## Scripts disponibles

| Comando | Acción |
| :--- | :--- |
| `npm run dev` | Desarrollo con recarga de módulos |
| `npm run lint` | Análisis estático con ESLint |
| `npm run build` | Comprobación TypeScript y empaquetado de producción |
| `npm run preview` | Vista local de la compilación, por defecto en el puerto 4173 |

Ejecutar lint y build al modificar código. Los comandos efectivos se definen en [package.json](package.json); no editar esta guía en lugar de actualizar el script correspondiente.

## Estructura

| Ruta | Responsabilidad |
| :--- | :--- |
| `src/main.tsx` | Entrada React e importación de CSS y fuentes |
| `src/App.tsx` | Proveedores globales de navegación y consultas |
| `src/router.ts` | Árbol de rutas tipadas y restauración de scroll |
| `src/query-client.ts` | Instancia de QueryClient |
| `src/api/` | Cliente HTTP, DTO, validación de respuestas y servicios tipados |
| `src/hooks/queries.ts` | Consultas, mutaciones e invalidación de caché |
| `src/components/projects/` | Formulario de alta de proyectos |
| `src/components/expenses/` | Registro rápido y consulta de gastos |
| `src/utils/` | Formato de importes/fechas y utilidades de formularios |
| `src/components/navbar.tsx` | Navegación y menús |
| `src/components/root-layout.tsx` | Composición de cabecera, contenido y pie |
| `src/components/dashboard/` | Hero y tarjetas |
| `src/components/ui/icon.tsx` | Iconos SVG tipados |
| `src/pages/` | Vistas asociadas a las rutas |
| `src/index.css` | Tokens y estilos compartidos de Tailwind |
| `public/` | Recursos gráficos servidos sin transformar |

El alias `@/` apunta a `src/` y se configura en [Vite](vite.config.ts) y [TypeScript](tsconfig.app.json). El procesamiento CSS se define en [PostCSS](postcss.config.js).

## Rutas

| Ruta | Vista |
| :--- | :--- |
| `/` | Inicio |
| `/proyectos` | Proyectos y Obras |
| `/gastos` | Registro de Gastos |
| `/configuracion` | Configuración |
| Otras | Página no encontrada |

Las capacidades reales de cada vista pertenecen al informe de estado enlazado al inicio, no a este catálogo de navegación.

## Branding y recursos

Los valores canónicos de color están en el bloque `@theme` de `src/index.css`. Reutilizar los tokens `brand-navy`, `brand-blue`, `brand-deep-blue`, `brand-canvas`, `brand-tint` y `brand-border` en lugar de introducir colores paralelos.

| Recurso en `public/` | Uso |
| :--- | :--- |
| `logo.png` | Logo activo en la Navbar |
| `logo-white.png` | Variante disponible para fondos oscuros |
| `favicon.svg` | Favicon activo en `index.html` |
| `favicon.ico` | Alternativa disponible, sin activar |
| `hero-blueprint.svg` | Ilustración decorativa del Hero |
| `logo.svg` | Emblema provisional conservado, no usado como logo de empresa |

Referenciar estos recursos desde la raíz pública, por ejemplo `/logo.png`, sin incluir `public/` en la URL.

Inter se importa desde `@fontsource/inter` en `src/main.tsx`, con pesos 400, 500 y 600 del subconjunto latino. El build incorpora sus archivos a `dist/assets/`. La estrategia de fuentes se justifica en el [ADR de migración](../docs/adr/0001-migracion-react-vite.md).

Las tarjetas usan tres columnas desde `lg` y una en pantallas menores. Conservar navegación por teclado, nombres accesibles, foco visible y cierre de menús con Escape.

## Publicación estática

El build genera `dist/` sin descargar recursos externos una vez instaladas las dependencias. Comprobar ese resultado con el script de preview; no usar preview como servidor de producción.

Publicar `dist/` en un alojamiento estático con redirección de rutas SPA a `index.html`, para permitir aperturas y recargas directas de las rutas internas.

## Mantenimiento de dependencias

Consultar avisos con `npm audit`. El override de minimatch en `package.json` mitiga GHSA-g3hv-75wg-m249 para sus consumidores modernos. Revisarlo cuando estos declaren versiones corregidas compatibles; conservar el lockfile y validar lint/build después de actualizar dependencias.
