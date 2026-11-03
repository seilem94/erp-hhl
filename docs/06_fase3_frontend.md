# Roadmap: Fase 3 — Frontend SPA / PWA (React 19 + Vite)

**Estado al 2026-11-03:** Base Vite y panel visual implementados. Las rutas de módulos existen como vistas en preparación; integración HTTP, formularios, autenticación y PWA siguen pendientes. Ver [PROJECT_STATE.md](PROJECT_STATE.md).

Esta fase comprende el diseño y construcción de la interfaz de usuario para el ERP Eléctrico, implementada como una Single Page Application (SPA) con capacidades PWA, optimizada para captura de gastos en terreno desde dispositivos móviles y administración operativa de obras desde escritorio.

---

## 📐 Principios y Decisiones Arquitectónicas

1. **Stack Base:** React 19 + Vite (SPA) con TypeScript en modo estricto, priorizando ligereza, despliegue estático desacoplado y rendimiento móvil instantáneo.
2. **Enrutamiento Tipado:** Uso exclusivo de **TanStack Router** para gestionar la navegación del cliente con validación estricta de rutas, parámetros de URL y carga paralela de datos sin acoplamiento a frameworks de backend.
3. **Gestión de Estado Asíncrono y API:** Uso de **TanStack Query** para la orquestación de llamadas a la API REST de FastAPI (`/api/v1/projects`, `/api/v1/expenses`), manejo de caché reactiva, revalidaciones automáticas y mutaciones con optimistic updates.
4. **Estrategia de Fuentes (Offline-First):**
   - Las tipografías del sistema (ej. `@fontsource/inter`) deben instalarse exclusivamente como dependencias npm y auto-alojarse dentro del bundle generado por Vite.
   - **Prohibición estricta:** Queda prohibido el uso de enlaces externos a Google Fonts (`fonts.googleapis.com` o `fonts.gstatic.com`) o CDNs de fuentes en línea. Esto permite compilar sin descargas externas tras instalar dependencias; la operativa offline completa requiere service worker, caché y sincronización de datos.
5. **Comandos de Validación y Compilación:**
   - Análisis estático / Linter: `eslint .`
   - Chequeo de tipos y empaquetado para producción: `tsc -b && vite build`
   - Comandos estándar oficiales requeridos para el pipeline y desarrollo: `eslint .` y `tsc -b && vite build`.

---

## 📋 Hitos y Tareas Secuenciales

### 🔹 Hito 1: Configuración Base del Entorno y Dependencias (Vite + TanStack)
- [x] Inicialización del proyecto con Vite y React 19 en TypeScript estricto.
- [x] Dependencias instaladas: `react`, `react-dom`, `@tanstack/react-router`, `@tanstack/react-query` y `@fontsource/inter`.
- [x] Tailwind CSS 4, `@tailwindcss/postcss`, PostCSS y Autoprefixer configurados.
- [x] Configuración de `vite.config.ts` y alias `@/` en Vite y TypeScript.
- [x] ESLint 10 (`eslint .`) y script de compilación (`tsc -b && vite build`).
- [x] Corrección de GHSA-g3hv-75wg-m249 mediante override limitado de minimatch; lockfile actualizado.

Los iconos actuales son SVG locales tipados. `lucide-react`, `clsx` y `tailwind-merge` no están instalados; evaluar su necesidad antes de añadir dependencias.

### 🔹 Hito 2: Enrutamiento y Capa de Consumo API (FastAPI Client)
- [x] Árbol de rutas tipadas con Inicio, Proyectos, Gastos, Configuración y página no encontrada.
- [ ] Reemplazar las vistas de preparación por pantallas funcionales y definir el flujo de autenticación.
- [x] Configuración del `QueryClient` de TanStack Query y proveedor global.
- [ ] Capa de servicios HTTP / funciones de fetch hacia la API FastAPI (`/api/v1/projects`, `/api/v1/expenses`) con tipado estricto alineado a los esquemas Pydantic v2 del backend.
- [ ] Manejo estandarizado de errores HTTP (400, 404, 422) y estados de carga (`isPending`, `isError`).

### 🔹 Diseño Visual del Panel (Completado)
- [x] Navbar con logo local, enlaces activos, menú móvil y menú de usuario con cierre por Escape.
- [x] Hero con título original, texto descriptivo, degradado sutil e ilustración local.
- [x] Tarjetas de Proyectos y Obras, Registro de Gastos y Finanzas Rápidas; tres columnas en escritorio y una en móvil.
- [x] Paleta de marca, Inter local, favicon y barras de distribución financiera accesibles.
- [x] Datos de ejemplo identificados; navegación a vistas de módulo en preparación sin simular persistencia.
- [x] Revisión visual y de interacción en Chromium de 320 a 1440 px.

### 🔹 Hito 3: Interfaz Móvil de Terreno (Registro Rápido de Gastos)
- [ ] Formulario móvil optimizado para terreno: captura en 20 segundos de compras con validación de montos positivos y fechas.
- [ ] Selector interactivo de imputación: Costo directo de Obra (CapEx) vs. Gasto Operativo de la Empresa (OPEX).
- [ ] Control de comprobantes: switch para marcar boleta física o captura fotográfica desde la cámara del dispositivo móvil.
- [ ] Feedback visual inmediato mediante notificaciones o toast de confirmación.

### 🔹 Hito 4: Panel de Obras y Administración
- [ ] Vista de listado de obras con filtro rápido por estado (*Planificación*, *En Ejecución*, *Pausada*, *Completada*, *Cancelada*).
- [ ] Modal / formulario para creación de nueva obra (`POST /api/v1/projects`) y actualización de estado/presupuesto (`PATCH /api/v1/projects/{project_id}`).
- [ ] Vista de detalle de proyecto con balance financiero: presupuesto estimado vs. costos directos acumulados.
- [ ] Reporte y consulta de gastos generales operativos (OPEX) y gastos por período.

### 🔹 Hito 5: Capacidades PWA y Optimización Offline
- [ ] Configuración de manifiesto de aplicación web (`manifest.json` o plugin `vite-plugin-pwa`).
- [ ] Service Worker para caching de assets estáticos y tipografías locales `@fontsource/inter`.
- [ ] Soporte para instalación directa en pantalla de inicio en Android e iOS sin pasar por tiendas de aplicaciones.
- [x] Validación de la base y el diseño actual con `eslint .` y `tsc -b && vite build` (exit code 0).
- [ ] Validación específica de instalación PWA, caché y sincronización offline cuando se implementen.
