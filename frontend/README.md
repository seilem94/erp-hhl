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

Los DTO se mantienen en `src/api/types.ts` y se contrastan con `/openapi.json` del servicio. El cliente usa `fetch`, comprueba las respuestas y normaliza errores HTTP, validaciones y fallos de conexión. No reintenta automáticamente las escrituras ni las deja en cola al detectar desconexión. Si una respuesta POST/PATCH no permite confirmar el resultado, conserva el formulario, avisa al usuario y refresca las consultas afectadas para revisar el listado o el detalle antes de repetir el envío.

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
| `src/hooks/queries.ts` | Consultas compartidas, selección de una obra, mutaciones e invalidación de caché |
| `src/hooks/dashboard.ts` | Composición de consultas y métricas del Dashboard |
| `src/utils/decimal.ts` | Suma decimal exacta antes del formato visual |
| `src/components/projects/` | Formularios de alta y edición parcial de proyectos |
| `src/components/expenses/` | Registro rápido y consulta de gastos |
| `src/utils/` | Formato de importes/fechas y utilidades de formularios |
| `src/utils/theme.ts` | Aplicación y persistencia local del tema |
| `src/components/navbar.tsx` | Navegación y menús |
| `src/components/root-layout.tsx` | Composición de cabecera, contenido y pie |
| `src/components/dashboard/` | Hero y tarjetas |
| `src/components/ui/icon.tsx` | Iconos SVG tipados |
| `src/components/ui/feedback.tsx`, `spinner.tsx` | Alertas accesibles e indicadores de carga y actualización |
| `src/pages/` | Vistas asociadas a las rutas |
| `src/index.css` | Tokens y estilos compartidos de Tailwind |
| `public/` | Recursos gráficos servidos sin transformar |

El alias `@/` apunta a `src/` y se configura en [Vite](vite.config.ts) y [TypeScript](tsconfig.app.json). El procesamiento CSS se define en [PostCSS](postcss.config.js).

## Rutas

| Ruta | Vista |
| :--- | :--- |
| `/` | Inicio |
| `/proyectos` | Proyectos y Obras |
| `/proyectos/$projectId` | Información y todos los gastos asociados a una obra |
| `/gastos` | Registro de Gastos |
| `/configuracion` | Configuración |
| Otras | Página no encontrada |

Las capacidades reales de cada vista pertenecen al informe de estado enlazado al inicio, no a este catálogo de navegación.

## Branding y recursos

Los valores canónicos de color están en el bloque `@theme` de `src/index.css`. Reutilizar los tokens `brand-navy`, `brand-blue`, `brand-deep-blue`, `brand-canvas`, `brand-tint` y `brand-border` en lugar de introducir colores paralelos.

| Recurso en `public/` | Uso |
| :--- | :--- |
| `logo.png` | Logo activo en la Navbar |
| `logo-white.png` | Logo activo en la Navbar con tema oscuro |
| `favicon.svg` | Favicon activo en `index.html` |
| `favicon.ico` | Alternativa disponible, sin activar |
| `hero-blueprint.svg` | Ilustración decorativa del Hero |
| `logo.svg` | Emblema provisional conservado, no usado como logo de empresa |

Referenciar estos recursos desde la raíz pública, por ejemplo `/logo.png`, sin incluir `public/` en la URL.

Inter se importa desde `@fontsource/inter` en `src/main.tsx`, con pesos 400, 500 y 600 del subconjunto latino. El build incorpora sus archivos a `dist/assets/`. La estrategia de fuentes se justifica en el [ADR de migración](../docs/adr/0001-migracion-react-vite.md).

Las tarjetas usan tres columnas desde `lg` y una en pantallas menores. Conservar navegación por teclado, nombres accesibles, foco visible y cierre de menús con Escape. El modificador `dark:` responde a la clase `dark` del elemento `html`; los tokens de superficies y bordes se adaptan a ese tema sin cambiar los colores de las tarjetas de marca.

## Publicación estática

El build genera `dist/` sin descargar recursos externos una vez instaladas las dependencias. Comprobar ese resultado con el script de preview; no usar preview como servidor de producción.

Publicar `dist/` en un alojamiento estático con redirección de rutas SPA a `index.html`, para permitir aperturas y recargas directas de las rutas internas.

## Consultas del Dashboard y del detalle

El resumen obtiene el listado de obras, los gastos operativos y los gastos de cada obra, incluidas las canceladas con gastos históricos. Cuenta las obras registradas y calcula el avance como obras completadas respecto al total. Los importes reflejan todos los registros devueltos, sin limitarse al historial rápido de diez gastos ni aplicar un período de fechas.

Los importes decimales se suman de forma exacta y se formatean en CLP sin pasar por `Number`, conservando precisión incluso por encima del entero seguro de JavaScript. Si una consulta necesaria falla, el total dependiente queda sin valor y se ofrece reintento; no se presenta una suma parcial como total definitivo.

La API actual no proporciona un GET individual de proyecto: la consulta del detalle resuelve la obra mediante el listado compartido en caché y consulta sus gastos por identificador. El detalle muestra todos esos gastos; comparte caché de gastos con el Dashboard y el historial para reflejar las mutaciones existentes. El número de consultas de gastos del resumen crece con el número de obras hasta disponer de un endpoint agregado.

## Edición, filtros y preferencias

El formulario de edición se abre en el detalle, precarga los datos y envía por PATCH únicamente los campos modificados. Un presupuesto vacío conserva el valor existente. Tras confirmar la respuesta, la mutación cancela lecturas anteriores, actualiza los datos e invalida exactamente la colección y la clave específica de la obra. La consulta derivada del detalle vuelve a resolver desde la colección al entrar, sin prolongar por su cuenta la vigencia de una copia anterior. Los errores conservan la edición.

El historial de gastos conserva las fechas en estado local y las envía al servicio como `start_date` y `end_date`, límites inclusivos y opcionales. Un rango invertido bloquea la consulta y muestra el error. Cada combinación de cuenta y fechas tiene su propia clave de caché; el botón de limpieza vuelve a la consulta sin fechas. Un registro invalida todos los rangos de su cuenta, incluida la consulta sin filtros, preservando la caché de otras obras y de OPEX cuando no están afectados. El historial mantiene su límite visual de diez registros, sin afectar los totales completos del Dashboard ni los gastos del detalle.

Los formularios muestran guardado y carga con indicadores visibles, conservan el teclado decimal en los campos numéricos y usan texto de 16 px en móviles. Los controles principales tienen al menos 44 px de alto; los importes y mensajes extensos se ajustan al ancho disponible sin ocultar contenido con `overflow-x: hidden`.

Configuración permite elegir tema claro u oscuro. La selección se guarda en `localStorage` y se aplica antes del montaje de React al recargar. Si el navegador impide guardarla, el tema se aplica a la sesión y se informa de la limitación. Esta preferencia pertenece al navegador, sin sincronización con una cuenta de usuario.

## Mantenimiento de dependencias

Consultar avisos con `npm audit`. El override de minimatch en `package.json` mitiga GHSA-g3hv-75wg-m249 para sus consumidores modernos. Revisarlo cuando estos declaren versiones corregidas compatibles; conservar el lockfile y validar lint/build después de actualizar dependencias.
