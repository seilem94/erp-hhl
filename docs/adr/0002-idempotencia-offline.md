# 0002. Idempotencia con UUIDs del cliente para operaciones offline

- **Fecha:** 2026-11-05
- **Estado:** Aceptado
- **Ámbito:** identificación de comandos, prevención de duplicados y recuperación de confirmaciones

## Contexto

Una escritura puede confirmarse en el servicio y perder su respuesta antes de llegar al navegador. La [propuesta de confirmación idempotente](../UX_UI_SUGGESTIONS.md#confirmación-idempotente-de-escrituras) identifica el riesgo de que un reenvío genere otro registro. Una futura cola offline amplifica este caso al sobrevivir a desconexiones, recargas y sesiones renovadas.

Las altas de [obras](../../backend/src/use_cases/create_project.py) y [gastos](../../backend/src/use_cases/register_daily_expense.py) generan identificadores en el servidor. Generar otro UUID al repetir el comando no identifica la intención original. Deshabilitar el botón durante el envío tampoco permite resolver una respuesta perdida ni dos solicitudes concurrentes.

## Decisión

### Identidad estable de la operación

1. Generar un **UUIDv4 en el cliente antes del primer envío** de cada comando que modifique datos. Persistirlo junto con el contenido y el usuario propietario hasta resolver la operación. Todos sus reintentos conservan ese UUID; una nueva intención utiliza uno nuevo.
2. Usar este UUID como clave de idempotencia de la operación, diferenciándolo del identificador del recurso. Para altas sincronizables, permitir también preasignar el UUID del recurso en el cliente, de modo que otras operaciones locales puedan referenciarlo antes de sincronizar. Un UUID de recurso aislado no cubre modificaciones ni sustituye el registro de operaciones.
3. Identificar de forma única la operación por **identidad autenticada y UUID**. Asociarle tipo de comando, recurso objetivo, huella del contenido normalizado y resultado. Una sesión renovada de la misma persona conserva la identidad de deduplicación; otra persona no puede asumir su cola ni consultar sus resultados.

### Confirmación persistente y concurrencia

- La misma clave y el mismo contenido recuperan el resultado confirmado, con sus identificadores originales, sin volver a ejecutar efectos de negocio. El resultado representa aquella operación, aunque el recurso se haya modificado después.
- La misma clave con otro contenido, recurso o tipo de comando se rechaza como conflicto; nunca actualiza silenciosamente el registro anterior.
- Persistir el cambio de negocio y su confirmación en **una misma transacción**. Una restricción única en persistencia arbitra solicitudes concurrentes: solo una ejecuta el efecto; las demás esperan su resolución o reciben un estado recuperable. Un diccionario en memoria de un proceso no aporta esta garantía.
- Si la transacción revierte, no queda una confirmación exitosa. Si se confirma y se pierde la respuesta, la repetición recupera el resultado persistido. No declarar éxito antes de asegurar la confirmación transaccional, respetando la [propiedad de las transacciones](../02_reglas_arquitectura.md).
- Revalidar identidad y permisos actuales antes de ejecutar o revelar resultados. Conservar el actor original para auditoría; un UUID no es una credencial ni otorga acceso al recurso.

La garantía es un único efecto confirmado para una misma operación dentro de la base de datos. No se promete ejecución exactamente una vez en redes o proveedores externos. Archivos y pagos externos necesitan confirmación y conciliación propias, vinculadas a la operación; no se vuelven atómicos por compartir un UUID.

### Recuperación y conservación

Ofrecer una consulta autorizada del estado o resultado por UUID. Distinguir confirmación, procesamiento en curso y operación no conocida; no conocerla puede deberse a una solicitud todavía en tránsito y no autoriza a crear otra clave para el mismo envío.

Mientras reserva y confirmación permanezcan sin commit, PostgreSQL no las hace visibles a otra transacción. La consulta no puede inferir procesamiento a partir de esa ausencia. Una reserva visible o un bloqueo efectivo de lectura sí permiten informar resolución incierta; los fallos de persistencia tampoco acreditan ausencia. Mantener este límite al interpretar una respuesta desconocida.

Conservar la identidad de deduplicación y su huella sin reutilización, incluso si se elimina el recurso mediante una marca histórica. El cuerpo completo de la respuesta puede tener una retención acotada, que deberá fijarse antes de implementar la cola. Si ese cuerpo vence, conservar una referencia suficiente para reconciliar o exigir intervención; la expiración nunca habilita ejecutar de nuevo una clave conocida. Evitar guardar credenciales o binarios en el registro de idempotencia.

Los errores de validación, falta de permisos y conflictos se distinguen de una confirmación exitosa. La interfaz no cambia de UUID para ocultar una incertidumbre: primero recupera o reconcilia el resultado. Los cambios concurrentes del mismo recurso requieren además una versión o condición esperada; la idempotencia no resuelve por sí sola conflictos entre intenciones distintas.

### Adopción y límites

La introducción de claves requiere evolucionar deliberadamente esquemas HTTP, DTO de casos de uso y persistencia. Mantener los identificadores de datos existentes y definir una transición compatible. Conforme al ajuste de adopción acordado el 2026-11-10 para integrar los comandos, las rutas de escritura existentes conservan su flujo anterior cuando falta la clave o el proveedor del servidor no resuelve una identidad válida. Ese flujo genera el UUID del recurso en el servidor y no reserva operaciones ni ofrece deduplicación, incluso si se recibió una clave sin actor. Una clave mal formada se rechaza; una denegación de permisos o un fallo durante el camino idempotente no permiten degradar al anterior. Esta compatibilidad de escrituras no relaja la identidad requerida por las lecturas autorizadas.

Exigir clave, identidad y permisos verificados antes de habilitar reenvíos automáticos o sincronización para usuarios. Los clientes deben distinguir el camino que ofrece la garantía antes de repetir una escritura.

Esta decisión no selecciona almacenamiento de sesión, política completa de cola, resolución funcional de conflictos ni estrategia de caché PWA. Su secuencia y los criterios de verificación pertenecen al [Módulo 1 de Fase 4](../07_fase4_evolucion_y_resiliencia.md#módulo-1-arquitectura-y-resiliencia).

## Consecuencias

- **Positivas:** una desconexión o recarga no obliga a adivinar si debe repetirse una escritura; se pueden recuperar confirmaciones y enlazar operaciones offline sin duplicar sus efectos persistentes.
- **Compensaciones:** se incorporan almacenamiento local por identidad, huellas normalizadas, restricciones únicas, conservación histórica y tratamiento de carreras y respuestas vencidas. Los archivos y servicios de pago mantienen sus propios límites transaccionales.
- **Alternativas descartadas:** depender solo del bloqueo del botón, de un UUID nuevo generado por el servidor en cada alta o de coincidencias de fecha, importe y descripción. Estas últimas pueden suprimir operaciones legítimas y no identifican de forma estable el comando original.
