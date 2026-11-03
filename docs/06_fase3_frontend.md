# Roadmap: Fase 3 — Frontend SPA / PWA (React 19 + Vite)

Esta fase comprende el diseño y construcción de la interfaz de usuario para el ERP Eléctrico, implementada como una Single Page Application (SPA) con capacidades PWA, optimizada para captura de gastos en terreno desde dispositivos móviles y administración operativa de obras desde escritorio.

---

## 📐 Principios y Decisiones Arquitectónicas

1. **Stack Base:** React 19 + Vite (SPA) con TypeScript en modo estricto, priorizando ligereza, despliegue estático desacoplado y rendimiento móvil instantáneo.
2. **Enrutamiento Tipado:** Uso exclusivo de **TanStack Router** para gestionar la navegación del cliente con validación estricta de rutas, parámetros de URL y carga paralela de datos sin acoplamiento a frameworks de backend.
3. **Gestión de Estado Asíncrono y API:** Uso de **TanStack Query** para la orquestación de llamadas a la API REST de FastAPI (`/api/v1/projects`, `/api/v1/expenses`), manejo de caché reactiva, revalidaciones automáticas y mutaciones con optimistic updates.
4. **Estrategia de Fuentes (Offline-First):**
   - Las tipografías del sistema (ej. `@fontsource/inter`) deben instalarse exclusivamente como dependencias npm y auto-alojarse dentro del bundle generado por Vite.
   - **Prohibición estricta:** Queda prohibido el uso de enlaces externos a Google Fonts (`fonts.googleapis.com` o `fonts.gstatic.com`) o CDNs de fuentes en línea, garantizando operatividad total sin conexión a internet en zonas rurales/obras y evitando bloqueos de red en pipelines de CI/CD.
5. **Comandos de Validación y Compilación:**
   - Análisis estático / Linter: `eslint .`
   - Chequeo de tipos y empaquetado para producción: `tsc -b && vite build`
   - Comandos estándar oficiales requeridos para el pipeline y desarrollo: `eslint .` y `tsc -b && vite build`.

---

## 📋 Hitos y Tareas Secuenciales

### 🔹 Hito 1: Configuración Base del Entorno y Dependencias (Vite + TanStack)
- [ ] Inicialización / reconfiguración del proyecto frontend con `vite` y React 19 en TypeScript estricto.
- [ ] Instalación de dependencias núcleo:
  - `react@19`, `react-dom@19`
  - `@tanstack/react-router`, `@tanstack/react-query`
  - `@fontsource/inter` (auto-alojada en bundle local)
  - `tailwindcss`, `lucide-react`, `clsx`, `tailwind-merge`
- [ ] Configuración de `vite.config.ts` y alias de paths (`@/...`).
- [ ] Configuración de ESLint (`eslint .`) y script de compilación (`tsc -b && vite build`).

### 🔹 Hito 2: Enrutamiento y Capa de Consumo API (FastAPI Client)
- [ ] Definición del árbol de rutas con TanStack Router (rutas de autenticación, dashboard, obras, gastos).
- [ ] Configuración del `QueryClient` de TanStack Query y proveedor global.
- [ ] Capa de servicios HTTP / funciones de fetch hacia la API FastAPI (`/api/v1/projects`, `/api/v1/expenses`) con tipado estricto alineado a los esquemas Pydantic v2 del backend.
- [ ] Manejo estandarizado de errores HTTP (400, 404, 422) y estados de carga (`isPending`, `isError`).

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
- [ ] Validación completa con `eslint .` y `tsc -b && vite build` asegurando exit code 0.
