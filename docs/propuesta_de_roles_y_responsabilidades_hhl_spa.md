# Propuesta de Modelo de Usuarios y Permisos — ERP HHL SpA

**Objetivo:** Definir cómo operará el ERP a medida que incorporemos a encargados de obra y trabajadores en terreno, manteniendo el control financiero y administrativo en manos de los socios, sin frenar la operación diaria.

---

## 1. Perfiles de Usuario Propuestos

### 1. Administrador / Socios (`Admin`)
* **Quiénes son:** Socios de HHL SpA y administrador técnico.
* **Propósito:** Control total de la empresa, finanzas, proyectos, usuarios y auditoría.
* **Qué puede hacer:**
  * Crear, editar y eliminar/archivar cualquier proyecto u obra.
  * Ver, registrar, editar y eliminar cualquier gasto (de obra u operativo).
  * Asignar o remover encargados y trabajadores en cualquier proyecto.
  * Acceder a resúmenes financieros, presupuestos y futuros dashboards de rentabilidad.
  * Crear cuentas de usuario, cambiar roles, desactivar accesos y reiniciar contraseñas.
  * Consultar el historial completo de auditoría (quién hizo qué y cuándo).

### 2. Encargado de Proyecto / Visita (`Encargado`)
* **Quiénes son:** Supervisores de terreno, jefes de obra o técnicos responsables de visitas/proyectos puntuales.
* **Propósito:** Gestionar la ejecución diaria de sus obras asignadas sin acceder a la información global de la empresa ni interferir en proyectos de otros.
* **Qué puede hacer:**
  * Crear nuevos proyectos/obras (queda automáticamente como encargado de los que crea).
  * Editar únicamente los proyectos que creó o a los que fue asignado como encargado.
  * Agregar o quitar trabajadores base dentro de sus proyectos asignados.
  * Registrar gastos en sus proyectos asignados y gastos operativos (sin proyecto).
* **Qué NO puede hacer:**
  * Ver ni editar proyectos de otros encargados.
  * Eliminar proyectos.
  * Ver dashboards financieros globales ni totales generales de la empresa.
  * Crear cuentas de usuario ni modificar permisos.

### 3. Trabajador Base (`Trabajador`)
* **Quiénes son:** Técnicos y ayudantes en terreno.
* **Propósito:** Facilitar la rendición rápida de gastos desde el celular (materiales menores, combustible, peajes, colaciones, etc.) sin exponer información sensible del negocio.
* **Qué puede hacer:**
  * Registrar gastos asociados únicamente a los proyectos donde esté asignado.
  * Registrar gastos operativos sin proyecto asociado (OPEX).
  * Indicar si cuenta con boleta/comprobante al cargar el gasto.
* **Qué NO puede hacer:**
  * Crear, editar o eliminar proyectos.
  * Ver presupuestos de obras ni dashboards financieros.
  * Editar gastos de otras personas ni gestionar usuarios.

---

## 2. Matriz Resumida de Permisos

| Acción en el ERP | Admin / Socios | Encargado de Proyecto | Trabajador Base |
| :--- | :---: | :---: | :---: |
| **Ver proyectos** | Todos | Solo asignados / creados | Solo asignados (lista básica) |
| **Crear proyecto nuevo** | Sí | Sí | No |
| **Editar proyecto** | Todos | Solo propios / asignados | No |
| **Eliminar / archivar proyecto** | Sí | No | No |
| **Ver presupuesto estimado de obra** | Sí | *Por definir* | No |
| **Asignar trabajadores a una obra** | En cualquier obra | Solo en sus obras | No |
| **Asignar encargados a una obra** | Sí | No | No |
| **Registrar gasto en obra** | En cualquier obra | En sus obras | En obras asignadas |
| **Registrar gasto operativo (OPEX)** | Sí | Sí | Sí |
| **Editar gastos** | Todos | *Por definir* | *Por definir* |
| **Eliminar gastos** | Sí | No | No |
| **Ver dashboards / finanzas globales** | Sí | No | No |
| **Ver historial de auditoría** | Completo (sistema y obras) | Solo sus obras *(opcional)* | No |
| **Crear usuarios y gestionar accesos** | Sí | No | No |

---

## 3. Cómo Funcionará el Acceso y las Contraseñas

1. **Alta segura:** Cuando un socio crea un usuario nuevo en el Panel de Administración, el sistema genera un **enlace personal de activación** (válido por 48 horas y de un solo uso) que se envía al trabajador.
2. **Clave privada:** El trabajador abre el enlace y crea su propia contraseña; nadie más conoce su clave.
3. **Autogestión:** Desde su perfil en el ERP, cada usuario puede cambiar su contraseña cuando quiera.
4. **Baja inmediata:** Si un trabajador deja de prestar servicios, un socio puede **desactivar su cuenta con un clic**. Se bloquea el acceso de inmediato, pero se conserva intacto todo su historial de gastos y auditoría.

---

## 4. Puntos a Acordar en Reunión de Socios (Decisiones Abiertas)

Antes de construir el sistema, conviene definir estas 5 reglas de negocio:

1. **Edición de gastos propios:** Si un **Trabajador Base** o un **Encargado** se equivoca al digitar un monto o un título, ¿debería poder editar *su propio gasto* (por ejemplo, dentro de las primeras 24 horas) o debe avisar a un Admin para que lo corrija?
2. **Visibilidad de gastos en una obra:** Un **Trabajador Base**, ¿solo debe ver el historial de *los gastos que él mismo cargó*, o puede ver también los gastos que subieron otros compañeros en la misma obra? *(Recomendación: que vea solo los propios).*
3. **Presupuesto de obra para Encargados:** ¿El **Encargado de Proyecto** debería poder ver el `Presupuesto Estimado` de la obra para controlar que no se pase del margen, o prefieren mantener los montos cotizados visibles solo para Socios?
4. **Edición de gastos de su equipo por el Encargado:** ¿Puede un **Encargado** editar o corregir gastos cargados por los trabajadores dentro de *su* proyecto, o esa facultad queda exclusiva de los **Socios**?
5. **Control de Gastos Operativos (OPEX):** Como el trabajador base puede cargar gastos operativos sin proyecto, ¿requieren algún paso posterior de "validación/rendición" por parte de los socios o basta con que quede registrado en la auditoría con su nombre?