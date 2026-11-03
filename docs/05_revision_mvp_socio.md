# ⚡ Sistema de Control Operativo y Financiero de Obras
## Guía de Validación Funcional para Trabajo en Terreno (MVP)

---

### 🎯 1. Introducción: ¿Qué resuelve este sistema hoy para nuestra empresa?

En el día a día de nuestras instalaciones eléctricas, el ritmo entre faena, compras de último minuto, traslados y coordinación de cuadrillas hace que el control de los números se vuelva un desafío. Muchas veces las boletas quedan arrugadas en la guantera de la camioneta, no está claro cuánto margen real nos va quedando en cada obra, o se mezclan los gastos propios de mantener el negocio en marcha con los costos directos de un cliente particular.

Este sistema nace para resolver exactamente eso: **dar orden, claridad y tranquilidad inmediata a nuestras faenas**.

Hoy la lógica de negocio ya está completamente construida y lista para:
1. **Controlar el ciclo de cada obra:** Saber con certeza en qué estado está cada faena (cotizándose, en ejecución, pausada o entregada) y monitorear su presupuesto acordado.
2. **Rendir gastos en segundos desde el celular:** Cargar compras de materiales en distribuidores eléctricos o ferreterías, combustible, peajes o colaciones de cuadrilla en el momento exacto en que ocurren, con respaldo de comprobante físico o fotografía.
3. **Separar las finanzas con precisión:** Diferenciar qué costo pertenece a un cliente específico de obra y qué gasto corresponde a la operación general de la empresa (mantenciones de vehículos, herramientas comunes, traslados generales).

Antes de construir las pantallas de la aplicación móvil y de escritorio, este documento presenta cada función disponible para que tú, como socio a cargo de las operaciones en terreno, nos des tu visto bueno, detectes falencias y propongas ajustes prácticos según lo que realmente vives día a día en la calle.

---

## 🏗️ Módulo 1: Gestión de Obras y Proyectos

Organiza el flujo completo de los trabajos eléctricos, desde el primer contacto comercial hasta la entrega final al cliente.

---

### 📌 Funcionalidad: Apertura y Registro de una Nueva Obra
💡 **¿Para qué sirve?:**
Permite dar de alta formalmente cualquier trabajo eléctrico nuevo (por ejemplo: *"Instalación Tablero General Edificio Central"* o *"Remodelación Eléctrica Local Comercial"*). Se ingresa el nombre de la obra, el cliente, una breve descripción técnica de lo que se va a ejecutar y el presupuesto estimado acordado. Al crearse, queda automáticamente registrada en estado de **Planificación** para comenzar a gestionar sus costos.

✍️ **Espacio para feedback del Socio:**
> **Observaciones y mejoras propuestas:**
> - [ ] 
> - [ ] 
> - [ ] 
> 
> **¿Qué datos adicionales de la obra te gustaría registrar al inicio desde el teléfono?** (Ej: dirección exacta, contacto del jefe de obra en terreno, número de empalme, fecha límite comprometida):
> 

---

### 📌 Funcionalidad: Control y Cambio de Estado de la Obra
💡 **¿Para qué sirve?:**
Las faenas en terreno son dinámicas: se inician los trabajos (**En Ejecución**), se detienen temporalmente por falta de materiales o permisos (**Pausada**), se entregan con las pruebas correspondientes (**Completada**) o se suspenden formalmente (**Cancelada**). Esta función permite cambiar el estado con un toque, actualizar presupuestos si el cliente pidió adicionales, o ajustar la descripción. Además, protege el negocio: si una obra se canceló, no permite que nadie le cargue gastos por error; pero si ya fue entregada, aún permite ingresar compras de última hora que hayan quedado rezagadas.

✍️ **Espacio para feedback del Socio:**
> **Observaciones y mejoras propuestas:**
> - [ ] 
> - [ ] 
> - [ ] 
> 
> **¿Te hacen sentido estos 5 estados (Planificación, En Ejecución, Pausada, Completada, Cancelada) o falta algún hito típico de tus faenas?**:
> 

---

### 📌 Funcionalidad: Tablero y Consulta de Obras Activas e Históricas
💡 **¿Para qué sirve?:**
Ofrece una vista limpia y ordenada de todas las obras de la empresa. Permite ver el listado completo o filtrar instantáneamente según su estado actual: por ejemplo, ver únicamente las obras que están hoy **En Ejecución** para coordinar las cuadrillas de la semana, o revisar las obras **Completadas** para balance financiero.

✍️ **Espacio para feedback del Socio:**
> **Observaciones y mejoras propuestas:**
> - [ ] 
> - [ ] 
> - [ ] 
> 
> **¿Cómo te resulta más cómodo ver este listado en el celular?** (Ej: tarjetas con colores según el estado, buscador rápido por cliente, o acceso directo con un solo botón a "Mis obras de hoy"):
> 

---

## 💰 Módulo 2: Finanzas en Terreno

Diseñado para registrar gastos de manera ágil, sin papeleo tardío ni pérdidas de boletas al final del mes.

---

### 📌 Funcionalidad: Rendir un Gasto Rápido de Terreno
💡 **¿Para qué sirve?:**
Permite anotar en menos de medio minuto cualquier compra realizada en ruta: rollos de cable, protecciones termomagnéticas, combustible en la estación de servicio, peajes, almuerzos de la cuadrilla o insumos menores de ferretería. El sistema asegura que el monto sea positivo, que la fecha no esté desfasada a futuro y clasifica el ítem en su categoría correspondiente (Materiales, Transporte, Alimentación, Herramientas, Mantenimiento, Servicios/Subcontratos u Otros).

✍️ **Espacio para feedback del Socio:**
> **Observaciones y mejoras propuestas:**
> - [ ] 
> - [ ] 
> - [ ] 
> 
> **¿Las categorías actuales cubren el 100% de lo que compras en el día?** (Materiales, Transporte, Alimentación, Herramientas menores, Mantenimiento, Servicios/Arriendos, Otros):
> 

---

### 📌 Funcionalidad: Respaldo con Foto y Control de Comprobantes
💡 **¿Para qué sirve?:**
Resuelve el problema de las boletas de papel térmico que se borran con el sol o los comprobantes que se extravían. Al rendir el gasto, permite marcar si se tiene boleta/factura física o adjuntar directamente una foto tomada con la cámara del celular. Si se adjunta la foto, el sistema deja constancia inmediata de que el gasto está respaldado y listo para ser validado o reembolsado sin discusiones.

✍️ **Espacio para feedback del Socio:**
> **Observaciones y mejoras propuestas:**
> - [ ] 
> - [ ] 
> - [ ] 
> 
> **¿Qué ocurre en terreno cuando un proveedor informal no emite boleta (ej: cuidador, flete menor, estacionamiento informal)? ¿Cómo prefieres declararlo?**:
> 

---

### 📌 Funcionalidad: Asignar Gastos Directamente a una Obra (Costos de Faena)
💡 **¿Para qué sirve?:**
Permite asociar cada compra a una obra específica. Si pasaste a comprar conductores eléctricos o canalizaciones para el cliente "Edificio Central", ese monto se imputa directamente a la cuenta de esa obra. Esto permite saber en tiempo real cuánto presupuesto se ha consumido y cuánto margen de ganancia le queda al trabajo antes de terminarlo.

✍️ **Espacio para feedback del Socio:**
> **Observaciones y mejoras propuestas:**
> - [ ] 
> - [ ] 
> - [ ] 
> 
> **Cuando compras materiales para 2 o más obras distintas en una misma boleta, ¿cómo sueles manejarlo hoy en la práctica?**:
> 

---

### 📌 Funcionalidad: Registrar Gastos Operativos Generales de la Empresa
💡 **¿Para qué sirve?:**
Hay gastos que no son culpa de ningún cliente en particular, sino que son necesarios para que la empresa funcione: mantención y cambio de aceite de la camioneta, calibración de equipos de medición (telurómetros, multímetros), renovación de herramientas desgastadas o insumos generales de taller. Esta función permite registrar estos costos como gastos operativos independientes, evitando castigar injustamente el margen de las obras.

✍️ **Espacio para feedback del Socio:**
> **Observaciones y mejoras propuestas:**
> - [ ] 
> - [ ] 
> - [ ] 
> 
> **¿Qué otros gastos frecuentes de la empresa identificas que deberían ir siempre a esta bolsa operativa y no a obras?**:
> 

---

### 📌 Funcionalidad: Consulta y Balance de Gastos por Rango de Fechas
💡 **¿Para qué sirve?:**
Permite revisar el historial de gastos filtrando por fecha (ejemplo: lo gastado esta semana, en la quincena o en el mes). Se puede consultar tanto el acumulado de una obra puntual para verificar si estamos dentro del presupuesto, como la suma total de gastos operativos para saber cuánto costó mover la empresa durante el período.

✍️ **Espacio para feedback del Socio:**
> **Observaciones y mejoras propuestas:**
> - [ ] 
> - [ ] 
> - [ ] 
> 
> **¿Qué resúmenes rápidos te gustaría tener disponibles en la pantalla de inicio?** (Ej: "Total gastado hoy en terreno", "Saldo disponible de la caja chica", "Total gastado esta semana en la obra X"):
> 

---

### 📋 Próximos Pasos para el Desarrollo

1. **Reunión de Revisión:** Completar este documento con las anotaciones y comentarios del socio operativo.
2. **Diseño de Pantallas:** Crear los bocetos visuales basados en las necesidades levantadas (botones grandes, pocos toques, pensados para usar con una sola mano en terreno).
3. **Prueba Piloto:** Realizar una marcha blanca en una obra real para validar la agilidad de carga en condiciones reales de faena.
