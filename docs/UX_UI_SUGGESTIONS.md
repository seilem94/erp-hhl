# Propuestas de UX/UI que requieren ampliar el alcance

Estas propuestas requieren cambios de API o de contrato y se reservan para una iteración posterior. El estado de entrega y su evidencia pertenecen a [PROJECT_STATE](PROJECT_STATE.md); la operación de la interfaz, al [README del frontend](../frontend/README.md).

## Agregados financieros en el servicio

El Dashboard necesita consultar los gastos de cada obra para calcular el resumen. El número de solicitudes y el volumen descargado crecen con las obras y sus registros históricos, afectando la espera en conexiones móviles.

Propuesta: acordar un endpoint de resumen que calcule importes operativos, importes de obras y cantidades en el servidor, con semántica consistente de fechas y moneda. Requiere definir el contrato y validar sus resultados antes de sustituir las consultas actuales.

## Confirmación idempotente de escrituras

Si la conexión se pierde después de que el servicio acepte una escritura, el navegador puede desconocer su resultado. Un reenvío manual de un alta podría generar otro registro.

Propuesta: acordar claves de idempotencia y una forma de consultar el resultado de una operación. Deben definirse persistencia, expiración y respuesta ante conflictos en la API antes de ofrecer reenvíos seguros o una cola offline en la interfaz.
