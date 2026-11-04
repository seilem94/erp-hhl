# HHL ERP

ERP para administrar obras eléctricas y gastos en terreno, orientado al uso móvil y al alojamiento en un servidor propio. El alcance del producto se define en [Contexto y usuarios](docs/01_contexto_erp.md).

## Stack

| Capa | Tecnología |
| :--- | :--- |
| Interfaz | React 19 + Vite SPA, TypeScript, Tailwind CSS |
| Navegación y estado remoto | TanStack Router y TanStack Query |
| API | FastAPI y Pydantic v2 |
| Persistencia | PostgreSQL, SQLAlchemy y Alembic |

## Arranque rápido

Preparar primero el [entorno de datos](backend/README.md) y las [dependencias del frontend](frontend/README.md#instalación-y-desarrollo).

### Windows

Desde la raíz del repositorio:

```powershell
.\start_dev.ps1
```

El [script de desarrollo](start_dev.ps1) abre cada servicio en una ventana de PowerShell separada. Requiere las dependencias y la configuración local preparadas; debe ejecutarse desde esta carpeta.

### Arranque manual

Con el entorno virtual activado y la configuración local lista, ejecutar en terminales separadas desde la raíz:

```bash
cd backend
python -m uvicorn src.main:app --reload --port 8000
```

```bash
npm --prefix frontend run dev
```

## Documentación

- [Índice y fuentes canónicas](docs/README.md).
- [Estado de entrega y validaciones](docs/PROJECT_STATE.md).
- [Protocolo para agentes](docs/AGENT.md).
- [Decisiones de arquitectura](docs/README.md#registro-de-decisiones).

La instalación, las migraciones y las pruebas se documentan exclusivamente en los README de cada componente enlazados arriba.
