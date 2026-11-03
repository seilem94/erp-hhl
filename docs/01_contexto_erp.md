# Contexto del Proyecto: ERP Eléctrico

## Objetivo
Desarrollar un ERP modular self-hosted para un emprendimiento eléctrico. El sistema centraliza finanzas y operaciones con costo $0 en infraestructura (servidor casero + Cloudflare Tunnels/Tailscale).

## Usuarios
1. Administrador (Escritorio): Liquidación de sueldos, creación de proyectos, análisis financiero.
2. Socio en Terreno (Móvil - PWA): Registro ágil de gastos diarios (comida, transporte, materiales) y revisión de asignación a obras.

## Stack
- Backend: FastAPI, Pydantic v2, PostgreSQL, SQLAlchemy/SQLModel.
- Frontend: React 19 + Vite (SPA), TypeScript, Tailwind CSS, TanStack Router (enrutamiento tipado) y TanStack Query (estado asíncrono y FastAPI). Fuentes auto-alojadas con @fontsource/inter en bundle de Vite, sin Google Fonts externos (fonts.googleapis.com).
- Infraestructura: Docker, Docker Compose.