# HHL ERP — Frontend

Interfaz de cliente construida con **React 19, Vite y TypeScript estricto**. Incluye el diseño del panel principal, navegación adaptable y recursos gráficos y tipografías auto-alojados.

## Estado actual

- Panel de inicio con Hero y tarjetas de Proyectos y Obras, Registro de Gastos y Finanzas Rápidas.
- Navbar con logo de la empresa, enlaces activos, menú móvil y menú de usuario.
- Accesos rápidos y navegación mediante TanStack Router.
- Métricas identificadas como **datos de ejemplo**, con importes formateados en pesos chilenos.
- Las vistas de Proyectos, Gastos y Configuración están en preparación: los enlaces navegan, pero todavía no registran ni modifican información.
- El menú de usuario es visual; no representa una sesión autenticada.

## Tecnologías

| Herramienta | Uso |
| :--- | :--- |
| React 19 | Componentes de interfaz y estado local |
| Vite 8 | Desarrollo con HMR y empaquetado estático |
| TypeScript | Tipado estricto y alias de importación |
| TanStack Router | Rutas de cliente tipadas y restauración del scroll |
| TanStack Query | QueryClient y proveedor global preparados para futuras consultas remotas |
| Tailwind CSS 4 | Utilidades, tokens de marca y estilos compartidos |
| PostCSS y Autoprefixer | Procesamiento del CSS junto con `@tailwindcss/postcss` |
| @fontsource/inter | Tipografía local, sin dependencias de fuentes externas |
| ESLint 10 | Análisis estático de JavaScript, TypeScript y componentes React |

Los iconos se implementan como SVG locales tipados en `src/components/ui/icon.tsx`. No se requiere una biblioteca adicional de iconos para la interfaz actual.

## Requisitos

- npm.
- Una versión de Node.js compatible con `package.json`: **`^20.19.0 || ^22.13.0 || >=24`**.

Comprobar las versiones instaladas:

```bash
node --version
npm --version
```

## Instalación y desarrollo

Ejecutar los comandos desde esta carpeta, `frontend/`:

```bash
npm ci
npm run dev
```

`npm ci` utiliza `package-lock.json` para instalar las versiones fijadas. La instalación inicial requiere acceso al registro npm.

Vite utiliza el puerto **5173** por defecto; si está ocupado puede seleccionar otro, indicado en la terminal. Para fijar el puerto y detectar conflictos:

```bash
npm run dev -- --port 5173 --strictPort
```

El script `dev` debe ejecutar `vite`. Si muestra otro framework, comprobar la rama y la versión local de `package.json`.

## Scripts disponibles

| Comando | Acción |
| :--- | :--- |
| `npm run dev` | Inicia Vite con recarga de módulos |
| `npm run lint` | Ejecuta `eslint .` |
| `npm run build` | Ejecuta `tsc -b && vite build` |
| `npm run preview` | Sirve localmente la compilación de `dist/` |

Validar cambios de interfaz con:

```bash
npm run lint
npm run build
```

El build comprueba los proyectos TypeScript y genera HTML, JavaScript, CSS y fuentes en `dist/`. Una vez instaladas las dependencias, no necesita descargar recursos externos.

## Estructura

```text
frontend/
├── public/                         # Imágenes, favicon e ilustraciones locales
├── src/
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── hero.tsx             # Introducción del panel
│   │   │   └── feature-cards.tsx    # Tarjetas y métricas de ejemplo
│   │   ├── ui/icon.tsx              # Iconos SVG tipados
│   │   ├── navbar.tsx               # Navegación y menús
│   │   └── root-layout.tsx          # Cabecera, contenido y pie de página
│   ├── pages/                      # Inicio, módulos en preparación y página no encontrada
│   ├── App.tsx                     # Proveedores de Query y Router
│   ├── index.css                   # Tailwind, colores y estilos compartidos
│   ├── main.tsx                    # Entrada React e importación de Inter
│   ├── query-client.ts             # Instancia global de QueryClient
│   └── router.ts                   # Árbol de rutas tipadas
├── index.html                      # Metadatos, idioma y favicon activo
├── eslint.config.js
├── postcss.config.js
├── tsconfig.json                   # Referencias a las configuraciones de aplicación y herramientas
├── vite.config.ts
├── package.json
└── package-lock.json
```

El alias `@/` apunta a `src/` y está configurado tanto en Vite como en TypeScript. Conservar los proveedores globales al incorporar nuevas páginas.

## Rutas

| Ruta | Vista |
| :--- | :--- |
| `/` | Panel principal con cifras de ejemplo |
| `/proyectos` | Proyectos y Obras, en preparación |
| `/gastos` | Registro de Gastos, en preparación |
| `/configuracion` | Configuración, en preparación |
| Cualquier otra ruta | Página no encontrada con enlace de regreso al inicio |

## Identidad visual y recursos locales

Los tokens se definen en el bloque `@theme` de `src/index.css`:

| Token | Color | Aplicación |
| :--- | :--- | :--- |
| `brand-navy` | `#0F172A` | Textos oscuros y tarjeta de proyectos |
| `brand-blue` | `#2563EB` | Acentos, enlaces activos y acciones |
| `brand-deep-blue` | `#1E40AF` | Degradados y contraste del azul |
| `brand-canvas` | `#F8FAFC` | Fondo general |
| `brand-tint` | `#EFF6FF` | Fondos suaves y estados activos |
| `brand-border` | `#E2E8F0` | Bordes y separadores |

Recursos de `public/`:

- **`logo.png`**: logo de empresa utilizado por la Navbar.
- **`logo-white.png`**: variante blanca disponible para fondos oscuros.
- **`favicon.svg`**: favicon activo, referenciado desde `index.html`.
- **`favicon.ico`**: alternativa disponible; todavía no está referenciada en `index.html`.
- **`hero-blueprint.svg`**: ilustración decorativa del Hero.
- **`logo.svg`**: emblema provisional anterior, conservado como recurso; no sustituye al logo de empresa actual.

Los archivos de `public/` se referencian desde la raíz pública, por ejemplo `/logo.png`, sin incluir `public/` en la URL.

Inter es la fuente predeterminada de todo el sitio. Se importa desde `@fontsource/inter` en `src/main.tsx`, con pesos **400, 500 y 600** del subconjunto latino. Vite incorpora sus archivos `.woff` y `.woff2` en `dist/assets/`. No añadir enlaces a Google Fonts ni a CDNs de tipografías, estilos o scripts.

El diseño utiliza tres columnas de tarjetas desde el breakpoint `lg` y una columna en pantallas menores. Mantener los nombres accesibles, los estados de foco, la navegación por teclado y el cierre de menús mediante Escape.

## Compilación y publicación estática

```bash
npm run build
npm run preview
```

`preview` utiliza el puerto **4173** por defecto y permite comprobar el resultado localmente. No es un servidor de producción.

Para publicar la interfaz, servir el contenido de `dist/` con un alojamiento estático que redirija las rutas de la SPA a `index.html`. Esto permite abrir o recargar directamente rutas como `/proyectos`.

## Dependencias de desarrollo

Para consultar avisos de seguridad:

```bash
npm audit
```

El override `minimatch@>=10 <11` selecciona `^11.0.1` para los consumidores modernos de esa dependencia y mitiga GHSA-g3hv-75wg-m249. Revisarlo cuando las herramientas consumidoras declaren versiones corregidas compatibles; conservar el lockfile y validar lint/build después de actualizar dependencias.

## Funcionalidades pendientes

- Consultas remotas y sustitución de las métricas de ejemplo por información real.
- Listados, filtros, formularios y estados de carga, error y vacío.
- Autenticación y preferencias persistentes de usuario.
- Captura y carga de comprobantes desde la interfaz.
- Manifiesto PWA, service worker, instalación y sincronización offline.

Los recursos auto-alojados permiten compilar sin descargas externas tras instalar dependencias. No implican por sí solos que la aplicación pueda instalarse o funcionar completamente sin conexión.
