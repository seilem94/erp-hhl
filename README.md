# ⚡ HHL ERP — Sistema de Gestión para HHL

Un ERP modular, ligero y diseñado bajo **Clean Architecture**, optimizado para el control operativo en terreno y la administración financiera de proyectos eléctricos. Implementado como solución *self-hosted* con costo de infraestructura $0.

---

## 📋 Resumen del Proyecto

VoltaicERP nace de la necesidad real de resolver dos puntos críticos en operaciones eléctricas de terreno:
1. **Portabilidad y agilidad en terreno:** Registro inmediato de compras de insumos, transporte y alimentación desde el móvil por parte del técnico/socio.
2. **Control financiero por obra:** Trazabilidad de costos directos, asignación de cuadrillas y cálculo de liquidaciones de sueldos al cierre de cada proyecto.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Propósito |
| :--- | :--- | :--- |
| **Backend** | Python + FastAPI + Pydantic v2 | API REST asíncrona, validación estricta y bajo consumo de recursos |
| **Persistencia** | PostgreSQL + SQLAlchemy / SQLModel | Almacenamiento relacional robusto con transaccionalidad ACID |
| **Frontend** | Next.js (App Router, React 19, TypeScript) | Interfaz web responsiva configurada como PWA para terreno |
| **Estilos** | Tailwind CSS + Lucide Icons | UI funcional, accesible y adaptada a dispositivos móviles |
| **Contenedores** | Docker + Docker Compose | Entorno reproducible y despliegue unificado |
| **Red y Acceso** | Cloudflare Tunnels / Tailscale | Exposición remota segura sin apertura de puertos en router ($0 costo) |

---

## 🏛️ Enfoque Arquitectónico (Clean Architecture Pragmática)

El backend sigue una separación estricta de responsabilidades para evitar que las reglas de negocio dependan de frameworks o de la base de datos:

```text
backend/
├── src/
│   ├── core/               # Configuración centralizada y variables de entorno
│   ├── domain/             # Entidades puras y contratos de repositorios (Zero dependencies)
│   │   ├── entities/       # Modelos del negocio (Expense, Project, Worker)
│   │   └── repositories/   # Interfaces abstractas (ABC)
│   ├── use_cases/          # Lógica de aplicación y orquestación de flujos
│   └── infrastructure/     # Implementación concreta del mundo exterior
│       ├── database/       # Modelos ORM, migraciones e implementaciones de repositorios
│       └── http/           # Routers de FastAPI, autenticación JWT y dependencias
```

> **Regla de oro de persistencia:** Los repositorios de infraestructura mapean las entidades ORM a entidades puras de dominio antes de retornar datos a los casos de uso, evitando el acoplamiento directo y errores de *lazy-loading*.

---

## 🗺️ Fases del Proyecto

- [x] **Fase 1: Núcleo y Dominio (MVP)** — Entidades de dominio, contratos de repositorios y casos de uso de proyectos y gastos diarios.
- [ ] **Fase 2: API e Infraestructura (En progreso)** — Modelos SQLAlchemy 2.0, mappers y repositorios PostgreSQL completados; pendientes configuración de sesión/engine, migraciones con Alembic, routers FastAPI y autenticación JWT.
- [ ] **Fase 3: Frontend PWA** — UI móvil para registro rápido en terreno y panel de administración en escritorio.
- [ ] **Fase 4: Despliegue y DevOps** — Orquestación completa con Docker Compose y túnel seguro en servidor local.

---

## 🚀 Puesta en Marcha (Entorno Local)

### Requisitos Previos
* Docker y Docker Compose
* Python 3.12+ (para desarrollo local backend)
* Node.js 20+ y pnpm / npm (para desarrollo local frontend)

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/erp-electrico.git
cd erp-electrico
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
```

### 3. Levantar con Docker Compose
```bash
docker compose up -d --build
```

El sistema estará disponible en:
* **Frontend / PWA:** `http://localhost:3000`
* **Backend API Docs:** `http://localhost:8000/docs`
* **PostgreSQL:** `localhost:5432`

---

## 📱 Capacidades PWA para Terreno

* **Optimización Offline-First:** Formularios ligeros para captura rápida de boletas y gastos.
* **Instalable:** Acceso directo desde la pantalla de inicio en Android e iOS sin pasar por tiendas de aplicaciones.
* **Consumo Mínimo de Datos:** Cargas optimizadas para conexiones 4G/3G inestables en obra.

---

## 🔒 Seguridad y Self-Hosting

El sistema está diseñado para correr en hardware casero (Mini PC, Raspberry Pi o servidor local) sin comprometer la red local:
* **Sin IP pública estática ni port forwarding:** Acceso asegurado mediante túnel inverso cifrado (Cloudflare Zero Trust / Tailscale).
* **Aislamiento por Contenedores:** Redes internas de Docker no expuestas directamente a la interfaz pública.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.