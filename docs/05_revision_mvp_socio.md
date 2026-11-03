# ⚡ Validación Funcional Rápida (MVP)
## Reunión Operativa de Terreno

> **Alcance actualizado (2026-11-03):** Esta guía combina capacidades del backend y objetivos de uso a validar con el socio. El panel web actual es una vista visual con datos de ejemplo; aún no permite registrar obras/gastos ni capturar fotografías. La captura en 20 segundos es un objetivo de UX, no una medición validada. El backend admite un enlace de comprobante (`receipt_url`), sin implementar captura ni carga de archivos.

---

### 🎯 1. Resumen Ejecutivo y Capacidades Centrales del Sistema

Este documento presenta lo que ya tenemos construido y funcionando en la lógica del sistema para apoyar el trabajo diario en terreno. El propósito de esta reunión no es vender una idea, sino revisar en conjunto las herramientas que ya están listas, verificar si calzan con tu rutina en la calle y definir qué datos necesitas ver en pantalla antes de programar la aplicación para el celular.

La revisión cubre cuatro pilares del negocio, separando las capacidades actuales de la API de los objetivos pendientes de interfaz:

1. **Gestión y Control de Obras Eléctricas:**
   Centraliza todas las faenas de la empresa desde que se cotizan hasta su entrega final. Permite fijar un presupuesto estimado por proyecto y controlar en tiempo real la situación real del trabajo (si está en planificación, en plena ejecución, pausado por materiales o permisos, completado o cancelado). Esto asegura que cada trabajo tenga un marco claro de costos y evita confusiones sobre qué faenas están activas.

2. **Rendición Ágil de Gastos en Terreno:**
   Elimina el hábito de juntar boletas arrugadas en la camioneta para rendirlas a fin de mes. Busca permitir ingresar en 20 segundos cualquier compra del día (conductores, automáticos, ferretería, combustible, peajes o colaciones del equipo), validando montos reales y fechas al instante para que la caja chica cuadre siempre al día.

3. **Separación de Costos de Obra vs. Gastos Operativos de la Empresa:**
   Distingue con total claridad a dónde va a parar el dinero:
   - **Costos directos de obra:** Materiales y traslados consumidos por un cliente específico, permitiendo medir cuánto margen real de ganancia nos va quedando frente al presupuesto.
   - **Gastos operativos del negocio:** Gastos necesarios para que la empresa funcione (mantención de la camioneta, calibración de instrumentos de medición, insumos generales de taller) que no pertenecen a ningún cliente y no deben castigar la rentabilidad de las faenas.

4. **Respaldo Inmediato y Control de Comprobantes:**
   La API permite asociar un enlace de comprobante al gasto. La captura y carga de fotografías desde el celular siguen pendientes; todavía no existe un flujo completo de respaldo de archivos desde la interfaz.

---

## 🏗️ Módulo 1: Gestión de Obras y Proyectos

---

### 📌 Funcionalidad: Crear Nueva Obra
💡 **¿Para qué sirve?:**  
Registra un trabajo nuevo con cliente, nombre de la faena, alcance técnico y presupuesto estimado. Comienza automáticamente en estado **Planificación**.

✍️ **Espacio para feedback del Socio:**
> - [ ] 
> - [ ] 
> *¿Qué dato clave necesitas registrar sí o sí al inicio? (ej. dirección exacta, contacto en obra, fecha límite):*

---

### 📌 Funcionalidad: Actualizar Estado de la Obra
💡 **¿Para qué sirve?:**  
Refleja el avance real de faena (*Planificación*, *En Ejecución*, *Pausada*, *Completada*, *Cancelada*) y permite ajustar presupuestos por trabajos adicionales. Rechaza nuevos gastos si la obra se cancela, pero admite gastos rezagados si ya fue completada.

✍️ **Espacio para feedback del Socio:**
> - [ ] 
> - [ ] 
> *¿Estos 5 estados reflejan tu día a día o falta/sobra alguno?:*

---

### 📌 Funcionalidad: Listado y Filtro de Obras
💡 **¿Para qué sirve?:**  
Muestra todas las faenas activas o históricas, permitiendo filtrar al instante por su estado actual (ej. ver solo lo que está hoy en ejecución).

✍️ **Espacio para feedback del Socio:**
> - [ ] 
> - [ ] 
> *¿Cómo prefieres verlas en el teléfono? (ej. tarjetas con colores por estado, buscador rápido por cliente):*

---

## 💰 Módulo 2: Finanzas en Terreno

---

### 📌 Funcionalidad: Rendir un Gasto Rápido en Ruta
💡 **¿Para qué sirve?:**  
Carga compras del día en segundos (cables, combustible, peajes, colaciones, ferretería). Valida que el monto sea positivo, que la fecha sea la correcta y clasifica por tipo de gasto.

✍️ **Espacio para feedback del Socio:**
> - [ ] 
> - [ ] 
> *¿Las categorías actuales cubren tu rutina? (Materiales, Combustible/Transporte, Comida, Herramientas, Mantenimiento, Servicios/Arriendos, Otros):*

---

### 📌 Funcionalidad: Respaldo con Foto y Comprobantes
💡 **¿Para qué sirve?:**  
Evita perder boletas térmicas. El backend admite asociar un enlace de comprobante. La captura con cámara, la carga del archivo y sus controles en la interfaz todavía están pendientes.

✍️ **Espacio para feedback del Socio:**
> - [ ] 
> - [ ] 
> *¿Cómo resolvemos gastos menores cuando no entregan boleta? (ej. flete informal, estacionador):*

---

### 📌 Funcionalidad: Asignar Gasto a una Obra (Costo Directo)
💡 **¿Para qué sirve?:**  
Imputa el gasto directo al presupuesto del cliente correspondiente, permitiendo ver en tiempo real cuánto dinero va consumiendo la faena.

✍️ **Espacio para feedback del Socio:**
> - [ ] 
> - [ ] 
> *Cuando compras materiales para varias obras en una misma boleta, ¿cómo prefieres ingresarlo?:*

---

### 📌 Funcionalidad: Gastos Operativos de la Empresa
💡 **¿Para qué sirve?:**  
Registra compras generales necesarias para funcionar (mantención de camioneta, calibración de instrumentos, insumos de taller) sin cargárselas a ningún cliente ni castigar el margen de las obras.

✍️ **Espacio para feedback del Socio:**
> - [ ] 
> - [ ] 
> *¿Qué otros costos frecuentes deben ir siempre a esta cuenta general?:*

---

### 📌 Funcionalidad: Consulta de Gastos por Período
💡 **¿Para qué sirve?:**  
Permite ver los totales gastados filtrando por fechas (día, semana, mes), ya sea para una faena específica o para los gastos generales de la empresa.

✍️ **Espacio para feedback del Socio:**
> - [ ] 
> - [ ] 
> *¿Qué resumen te sirve tener más a mano? (ej. "Total gastado hoy", "Gasto semanal de esta obra"):*

---

### 📋 Acuerdos de la Reunión
> **Anotaciones finales antes del diseño visual:**
> - 
> - 
