# ⚡ Frontend — HHL ERP (React 19 + Vite SPA)

Interfaz de usuario para el ERP Eléctrico HHL, desarrollada como una Single Page Application (SPA) ligera con capacidades PWA, optimizada para la captura rápida de gastos en terreno desde dispositivos móviles y la administración de proyectos eléctricos desde escritorio.

---

## 🛠️ Stack Tecnológico

| Herramienta | Propósito |
| :--- | :--- |
| **React 19** | Biblioteca declarativa de interfaces de usuario |
| **Vite** | Bundler ultrarrápido y servidor de desarrollo HMR |
| **TypeScript** | Tipado estático estricto (cero `any`) |
| **TanStack Router** | Enrutamiento SPA fuertemente tipado con gestión de parámetros |
| **TanStack Query** | Manejo de estado del servidor, caché reactiva y peticiones a FastAPI |
| **Tailwind CSS** | Sistema de diseño de utilidades adaptado a dispositivos móviles |
| **@fontsource/inter** | Tipografía auto-alojada localmente en el bundle |

---

## 🚀 Puesta en Marcha

### Instalación de dependencias
```bash
npm install
```

### Servidor de desarrollo
```bash
npm run dev
```
Disponible por defecto en: [http://localhost:5173](http://localhost:5173)

---

## 🔍 Comandos de Validación y Compilación

Para cumplir con los estándares de calidad del proyecto, utiliza los comandos de Vite y TypeScript:

```bash
# Análisis estático y linter:
eslint .

# Comprobación de tipos y empaquetado para producción:
tsc -b && vite build
```

*(Nota: Comandos estándar requeridos para validación en desarrollo y pipelines CI/CD).*

---

## 🔤 Estrategia de Fuentes (Offline-First)

* **Auto-alojamiento local:** Las fuentes tipográficas (ej. `@fontsource/inter`) deben ser instaladas exclusivamente como paquetes npm y empaquetadas dentro del bundle estático generado por Vite.
* **Prohibición de Google Fonts externos:** Queda prohibido el enlace o consumo de fuentes externas provenientes de `fonts.googleapis.com` o `fonts.gstatic.com`. Esta regla asegura:
  1. Operativa 100% offline para el técnico en terreno en zonas con señal inestable o nula.
  2. Builds deterministas y sin bloqueos de red en pipelines de CI/CD.

---

## 🌐 Enrutamiento y Estado de Servidor

* **TanStack Router:** Proporciona enrutamiento seguro de tipos en tiempo de compilación para la navegación entre el dashboard, obras y formularios de rendición.
* **TanStack Query:** Gestiona la comunicación con los endpoints REST del backend FastAPI (`/api/v1/projects`, `/api/v1/expenses`), ofreciendo revalidación automática, caché en memoria y optimizaciones de red.
