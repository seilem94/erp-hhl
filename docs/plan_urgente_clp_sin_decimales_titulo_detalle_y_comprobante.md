# Plan de Modificaciones Urgentes — Gastos y Formato CLP (`erp-hhl`)

**Rama sugerida:** main 
**Prioridad:** Alta (ajuste inmediato sobre producción actual)

---

## 1. Alcance y Decisiones Técnicas

### A. Pesos Chilenos (CLP) sin decimales y soporte para millones
* **Problema actual:** Se muestran 2 decimales (ej. `$631.810,00`), lo cual no aplica a CLP y ensucia la lectura de montos en miles y millones.
* **Base de datos (PostgreSQL 17):**
  * Usar `BIGINT` (o `NUMERIC(14, 0)`) para montos de gastos y presupuestos estimados de proyectos. `BIGINT` evita desbordamientos si los presupuestos o acumulados superan el límite de `INTEGER` (~$2.147 millones) y garantiza aritmética entera exacta sin residuos decimales.
  * La migración de Alembic debe redondear/castear los valores existentes sin pérdida de datos (`USING ROUND(monto)::bigint`).
* **Backend (Pydantic):** Validar `monto` y `presupuesto_estimado` como enteros (`int`, `gt=0` o `ge=0` según corresponda), rechazando decimales.
* **Frontend (React/TypeScript):**
  * Centralizar el formateo en un helper único (DRY), por ejemplo `formatCLP(value: number)`:
    ```ts
    new Intl.NumberFormat("es-CL", {
      style: "currency",
      currency: "CLP",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(Math.round(value));
    ```
  * En los formularios de creación/edición de gastos y proyectos, usar inputs enteros (`step="1"`, `inputMode="numeric"`) y, opcionalmente, mostrar una vista previa formateada con separador de miles mientras se escribe (ej. `$1.450.000`) para evitar errores de ceros en terreno.

### B. Separación de `titulo` (obligatorio) y `detalle` (opcional) en Gastos
* **Nota de diseño de datos:** En lugar de crear una tabla separada 1:1 para el detalle, lo más limpio, rápido y coherente con SQLAlchemy/PostgreSQL es mantener ambos campos como columnas en la tabla `gastos`:
  * Renombrar la columna existente `descripcion` -> `titulo` (`VARCHAR`, `NOT NULL`). Así se conservan intactos los gastos ya registrados en producción.
  * Agregar la columna `detalle` (`TEXT`, `NULLABLE`).
* **Visualización en tarjetas de gasto (Frontend):**
  * Mostrar **`titulo`** como encabezado principal de la tarjeta/fila.
  * Si existe `detalle`, renderizarlo justo debajo del título con tipografía más pequeña y color secundario (ej. `text-xs text-slate-500`), ocultando el bloque por completo cuando esté vacío.

### C. Casilla "Tiene comprobante" en el formulario de creación (`POST`)
* Incorporar el checkbox **`Tiene comprobante`** directamente en la vista principal de registro de gasto (con valor inicial `false`), enviándolo en el payload de `POST /api/gastos` de la misma forma que ya funciona en el modal de edición (`PATCH`).

---

## 2. Prompt Listo para Codex

```markdown
**Contexto y objetivo:**
Sobre una rama nueva creada desde `main` (`feat/gastos-clp-titulo-detalle`), necesitamos aplicar tres mejoras urgentes en `erp-hhl`:
1. Adaptar toda la aplicación (BD, API y Frontend) al formato de Pesos Chilenos (**CLP**) sin decimales, preparado para montos en miles y millones.
2. Refactorizar el campo `descripcion` del modelo de gastos para pasarlo a `titulo` (obligatorio) y agregar un campo `detalle` (opcional), preservando los datos ya existentes mediante Alembic.
3. Agregar la casilla `tiene_comprobante` en el formulario principal de creación de gastos (`POST`), igualando la paridad con el formulario de edición.

**Tareas a ejecutar (siguiendo SOLID, DRY y las convenciones del proyecto):**

### 1. Base de datos y Backend (`backend/`)
- **Migración Alembic segura (sin pérdida de datos):**
  - En la tabla de gastos:
    - Renombra la columna `descripcion` a `titulo` (`NOT NULL`).
    - Agrega la columna `detalle` (`Text`, `nullable=True`).
    - Asegura que `monto` (en gastos) y `presupuesto_estimado` (en proyectos) sean enteros grandes (`BigInteger` o `Numeric(14, 0)`), convirtiendo los registros existentes con `ROUND(...)::bigint`.
- **Modelos, Esquemas y Servicios:**
  - Actualiza el modelo SQLAlchemy, los esquemas Pydantic (`Create`, `Update`, `Read`) y los endpoints de gastos (`POST /api/gastos`, `PATCH /api/gastos/{id}`, `GET /api/gastos`) para usar `titulo` (obligatorio), `detalle` (opcional), `monto` (`int`) y `tiene_comprobante` (`bool`, default `False`).
  - Actualiza también `presupuesto_estimado` y totales en proyectos/finanzas para devolver enteros sin decimales.
  - Actualiza `audit_service.py` para que los resúmenes de auditoría utilicen `titulo` y formateen los montos en CLP sin decimales (ej. `$120.000`).
- **Tests:** Actualiza y ejecuta `pytest` cubriendo creación con `tiene_comprobante`, creación/edición de `titulo` y `detalle`, validación de montos enteros grandes (millones) y generación de logs de auditoría.

### 2. Frontend (`frontend/`)
- **Formateo CLP centralizado:**
  - Crea o actualiza un helper único de formateo de moneda (`es-CL`, `CLP`, `minimumFractionDigits: 0`, `maximumFractionDigits: 0`) y úsalo en **todas** las vistas (Home, Finanzas Rápidas, Proyectos, Gastos, Modal de Edición y Auditoría) eliminando cualquier visualización de 2 decimales.
  - En los inputs de montos (gastos y presupuesto de proyectos), usa `step="1"` e `inputMode="numeric"`, y muestra una ayuda visual en tiempo real con el monto formateado en pesos (ej. `$2.500.000`) para evitar errores de tipeo en montos altos.
- **Formulario de Registro de Gasto (`POST`):**
  - Reemplaza el campo `Descripción` por **`Título *`** (obligatorio, ej. "Compra cable EVA 2.5mm").
  - Agrega el campo **`Detalle`** (opcional, `<textarea>` compacto de 2–3 líneas, con etiqueta `Opcional`).
  - Agrega el checkbox **`Tiene comprobante`** (boleta/factura) directamente en el formulario principal de creación.
- **Formulario de Edición y Tarjetas de Gasto:**
  - Actualiza el modal de edición para soportar `titulo` y `detalle` (junto con `tiene_comprobante` que ya existe).
  - En cada tarjeta/fila del listado de gastos, muestra `titulo` destacado y, si `detalle` tiene contenido, muéstralo justo debajo en tipografía más pequeña y tono secundario.

### 3. Verificación
- Ejecuta `pytest` en `backend/`.
- Ejecuta `npm run build` / verificación de tipos TypeScript en `frontend/`.
- Verifica `git diff --check`.
```

---

## 3. Checklist de Despliegue y Validación en Producción

1. **Backup preventivo antes de migrar columnas en PostgreSQL:**
   ```bash
   docker compose exec db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup_pre_clp_$(date +%Y%m%d_%H%M).sql
   ```
2. **Desplegar cambios:**
   ```bash
   git pull origin main
   docker compose up -d --build backend frontend
   ```
3. **Pruebas manuales en `https://erp.mrchispeza.cl`:**
   * Verificar que los 9 gastos existentes conservaron su nombre ahora como `titulo` y que `$631.810` aparece sin `,00`.
   * Crear un gasto nuevo de `$1.250.000` marcando **Tiene comprobante**, con `titulo` y `detalle`, y comprobar cómo se renderiza la tarjeta y el log de auditoría.