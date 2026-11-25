# Plan de Arquitectura Técnica — Usuarios, Sesiones, RBAC y Panel de Administración

**Estado:** Propuesta para diseño y validación (Fase siguiente)  
**Stack:** FastAPI + SQLAlchemy + Alembic + PostgreSQL 17 + React/Vite + Cloudflare Tunnel

---

## 1. Arquitectura de Autenticación y Relación con Cloudflare Access

Actualmente, Cloudflare Zero Trust actúa como capa de perímetro con One-time PIN. Al escalar a trabajadores en terreno y roles internos, existen dos opciones:

### Estrategia Recomendada: Autenticación Interna de Aplicación (Sesiones + RBAC)
* **Cómo funciona:**
  * El backend gestiona su propia tabla `users`, verificación de contraseñas (`Argon2id` o `bcrypt` vía `pwdlib`/`passlib`) y sesiones basadas en **JWT en cookies `HttpOnly`, `Secure`, `SameSite=Lax`** (access token corto + refresh token revocable en BD).
  * **Rol de Cloudflare Tunnel:** Sigue exponiendo `erp.mrchispeza.cl` de forma segura sin abrir puertos en Debian 13.
  * **Rol de Cloudflare Access:**
    * *Fase inicial (solo socios):* Puede mantenerse activo como doble barrera mientras prueban.
    * *Fase con trabajadores en terreno:* Se desactiva Cloudflare Access para la app principal (o se deja solo para rutas administrativas sensibles) para no tener que gestionar listas de correos en dos plataformas distintas cada vez que entra o sale un trabajador. El control de acceso pasa a ser 100% administrado desde el **Panel de Administración del ERP**.
* **Impacto en Auditoría (`audit_logs`):**
  * `actor_user_id` (FK a `users.id`) y `actor_email` pasan a tomarse directamente del usuario autenticado en la sesión del ERP, manteniendo trazabilidad exacta e inmutable.

---

## 2. Modelo de Datos Propuesto

### Tabla `users`
| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | `UUID` / `INT PK` | Identificador único del usuario |
| `email` | `VARCHAR(255)` (Unique, Index) | Correo de inicio de sesión |
| `nombre_completo` | `VARCHAR(150)` | Nombre visible en tarjetas y auditoría |
| `password_hash` | `VARCHAR(255)` (Nullable) | Hash Argon2id/bcrypt (`NULL` mientras la invitación esté pendiente) |
| `rol` | `ENUM('ADMIN', 'ENCARGADO', 'TRABAJADOR')` | Rol global base del usuario |
| `activo` | `BOOLEAN` (Default `true`) | Permite desactivar acceso sin borrar historial ni auditoría |
| `debe_cambiar_password` | `BOOLEAN` (Default `false`) | Fuerza cambio de clave en el siguiente inicio de sesión si aplica |
| `created_at` / `updated_at` | `TIMESTAMPTZ` | Trazabilidad |

### Tabla `proyecto_miembros` (Asignación a Obras)
Relación N:M entre `users` y `proyectos`:
| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | `INT PK` | Identificador |
| `proyecto_id` | `FK -> proyectos.id` (`ON DELETE CASCADE`) | Obra asignada |
| `user_id` | `FK -> users.id` (`ON DELETE CASCADE`) | Usuario asignado |
| `rol_en_proyecto` | `ENUM('ENCARGADO', 'TRABAJADOR')` | Permite distinguir quién lidera la obra frente a trabajadores base |
| `asignado_por_id` | `FK -> users.id` (`ON DELETE SET NULL`) | Quién lo agregó (para auditoría) |
| `created_at` | `TIMESTAMPTZ` | Fecha de asignación |
* *Restricción:* `UNIQUE (proyecto_id, user_id)`.
* *Nota adicional en `proyectos`:* Agregar `creado_por_id` (`FK -> users.id`, nullable para proyectos previos) para saber qué proyectos creó un `ENCARGADO`.

### Tabla `user_tokens` (Alta de Contraseña y Recuperación)
| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | `INT PK` | Identificador |
| `user_id` | `FK -> users.id` (`ON DELETE CASCADE`) | Usuario dueño del token |
| `token_hash` | `VARCHAR(255)` (Unique, Index) | Hash SHA-256 del token (nunca guardar el token plano en BD) |
| `tipo` | `ENUM('INVITACION', 'RESET_PASSWORD')` | Propósito del enlace |
| `expires_at` | `TIMESTAMPTZ` | Expiración (ej. 48h para invitación, 1h para reset) |
| `used_at` | `TIMESTAMPTZ` (Nullable) | Marca de uso único |

---

## 3. Mecanismo de Creación y Cambio de Contraseña

Para evitar compartir contraseñas en texto plano por WhatsApp:

1. **Alta de nuevo usuario (Admin):**
   * En el Panel de Administración, el Admin ingresa `Nombre`, `Email` y `Rol`.
   * El sistema crea el usuario con `password_hash = NULL` y genera un **enlace de activación de un solo uso** (ej. `https://erp.mrchispeza.cl/activar-cuenta?token=...`, válido por 48 horas).
   * *Entrega práctica (sin depender de SMTP desde el día 1):* La interfaz muestra un botón **"Copiar enlace de activación"** para enviárselo al trabajador por WhatsApp o correo (y en una fase posterior se puede automatizar el envío vía SMTP/Resend).
2. **Definición de contraseña inicial (Usuario nuevo):**
   * El usuario abre el enlace, ingresa su nueva contraseña (mínimo 8 caracteres) y la confirma.
   * El backend valida expiración y uso único, guarda `password_hash`, marca `used_at` e inicia sesión automáticamente.
3. **Cambio de contraseña voluntario (Usuario autenticado):**
   * Desde el menú de perfil (ícono de usuario arriba a la derecha), cualquier usuario puede entrar a **Mi cuenta > Cambiar contraseña**, ingresando contraseña actual + nueva contraseña.
   * Al cambiarla, se revocan los refresh tokens activos de otras sesiones.
4. **Recuperación / Reset por Admin:**
   * Si un trabajador olvida su clave, el Admin puede generar un nuevo enlace de **Restablecer contraseña** (`RESET_PASSWORD`, válido 1 hora) desde el Panel de Administración.

---

## 4. Control de Acceso (RBAC) en Backend y Frontend

La seguridad real se aplica en el **Backend** mediante dependencias de FastAPI; el Frontend oculta botones/vistas solo por experiencia de usuario.

* **Dependencias reutilizables en FastAPI (`backend/src/auth/dependencies.py`):**
  * `get_current_user`: Valida sesión y verifica `user.activo == True`.
  * `require_roles(*roles)`: Bloquea con `403 Forbidden` si el rol no coincide.
  * `require_project_access(proyecto_id, write=False)`:
    * `ADMIN`: acceso total lectura/escritura.
    * `ENCARGADO`: lectura/escritura solo si es creador del proyecto o figura como `ENCARGADO` en `proyecto_miembros`.
    * `TRABAJADOR`: solo lectura básica y permiso para registrar gastos si figura en `proyecto_miembros`.
* **Reglas de filtrado en listados (`GET`):**
  * `GET /api/proyectos`: `ADMIN` ve todos; `ENCARGADO` y `TRABAJADOR` ven únicamente los proyectos donde están asignados (o creados por ellos en el caso de `ENCARGADO`).
  * `GET /api/gastos`: `ADMIN` ve todos; `ENCARGADO` ve los de sus proyectos asignados y los suyos; `TRABAJADOR` ve únicamente los gastos registrados por él mismo (configurable según acuerdo con socios).

---

## 5. Panel de Administración (Solo `ADMIN`)

Accesible desde el menú `Configuración` o una pestaña dedicada `Administración`:

1. **Gestión de Usuarios:**
   * Listado con nombre, correo, rol, estado (`Activo` / `Invitación pendiente` / `Inactivo`).
   * Crear usuario y copiar enlace de activación.
   * Editar rol, desactivar/reactivar cuenta y generar enlace de reseteo de clave.
2. **Gestión de Asignaciones por Proyecto:**
   * Desde el detalle de cada obra (o desde el panel), asignar uno o más **Encargados** y **Trabajadores** a la obra.
   * *(Nota: Los Encargados también verán el bloque reducido para agregar/quitar Trabajadores únicamente en las obras donde ellos son Encargados).*
3. **Auditoría Global:**
   * Acceso exclusivo para `ADMIN` a la bitácora completa del sistema filtrable por usuario, acción y proyecto.

---

## 6. Hoja de Ruta Sugerida (Implementación Incremental)

* **Fase 1 — Base de Usuarios y Sesiones (Para Socios):**
  * Migración `users` + `user_tokens` + script CLI para crear el primer `ADMIN` (seed).
  * Login/Logout con cookies `HttpOnly`, pantalla de login, activación de cuenta y cambio de contraseña.
  * Integración de `actor_user_id` en `audit_logs`.
* **Fase 2 — Asignaciones y Reglas RBAC:**
  * Tabla `proyecto_miembros` y `creado_por_id` en `proyectos`.
  * Guards de permisos en endpoints de Proyectos, Gastos y Auditoría.
  * Ajuste de vistas del Frontend según rol (ocultar dashboards financieros/totales globales a no-admins).
* **Fase 3 — Panel de Administración:**
  * UI completa de gestión de usuarios, links de invitación/reset y asignación de personal a obras.