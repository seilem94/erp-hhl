# 0003. Separación de flujos de caja y política salarial por condición de IVA

- **Fecha:** 2026-11-05
- **Estado:** Aceptado
- **Ámbito:** clasificación financiera de obras, destino de fondos y selección de reglas de remuneración

## Contexto

Las notas acordadas con el cliente distinguen dos modalidades de trabajo con diferente cuenta responsable, formas de cobro y cálculo salarial. El modelo de [obra](../../backend/src/domain/entities/project.py) y el de [gasto](../../backend/src/domain/entities/expense.py) deben poder evolucionar para representar esa distinción sin inferirla de nombres, de la existencia de una boleta ni del rol del usuario.

Un único saldo indiferenciado mezclaría fondos de HHL con fondos de socios. Repetir la condición en formularios, resúmenes y liquidaciones permitiría que cada consumidor aplicara reglas distintas y dificultaría corregir datos históricos.

## Decisión

### Condición fiscal explícita

Incorporar en la obra una propiedad booleana obligatoria **`has_iva`** como fuente de clasificación: `true` significa trabajo **Con IVA** y `false`, trabajo **Sin IVA**. Es un nombre de diseño para la evolución del dominio; su publicación HTTP debe acompañarse del correspondiente contrato ejecutable.

La clasificación pertenece al trabajo, no al usuario ni al comprobante. No derivarla de `has_receipt`, de una URL, de la categoría del gasto o de una cuenta elegida por el navegador. Los movimientos y liquidaciones conservan una referencia trazable a la clasificación y versión de política aplicadas; una copia histórica para auditoría no permite elegir una condición incompatible al registrar una nueva operación.

### Cuentas y modalidades de cobro

- **Con IVA (`has_iva = true`):** canalizar el flujo financiero de la obra por la **cuenta HHL**. Habilitar las modalidades de cobro mediante **cuotas o link de pago** cuando se acuerden para ese trabajo.
- **Sin IVA (`has_iva = false`):** canalizar el flujo por **cuentas de socios**, identificando cuenta y socio responsable. No habilitar cuotas ni link de pago para esta modalidad.

Validar la compatibilidad de cuenta y modalidad en los casos de uso, incluso en llamadas directas y reintentos. Mantener separados el destino de los fondos y su imputación a una obra: ambos datos son necesarios. Una transferencia excepcional entre cuentas requiere un movimiento explícito y trazable, sin reclasificar silenciosamente la obra ni contarlo dos veces en el consolidado.

Los gastos operativos sin obra necesitan cuenta y criterio de imputación propios; no se consideran automáticamente trabajos sin IVA. La selección de las cuentas concretas, su reparto entre socios y los mecanismos de conciliación se precisan durante el diseño financiero.

### Política salarial

Seleccionar una **política de remuneración diferente para cada valor de `has_iva`**, centralizada en dominio y casos de uso. Cada política recibe la asistencia aprobada y las tarifas o parámetros vigentes; devuelve un cálculo trazable con su versión y la clasificación aplicada. Las fórmulas no pertenecen a componentes de interfaz, routers ni consultas agregadas.

El acuerdo establece que los sueldos varían entre modalidades, pero no fija porcentajes, montos, descuentos, base de cálculo ni redondeo. Esos parámetros deben aprobarse antes de automatizar liquidaciones; no se deducen de una tasa fiscal supuesta. Distinguir cálculo, aprobación y pago efectivo, conservando la referencia a jornadas y movimientos para conciliar cada desembolso.

### Respaldos y autorización

La obligación de respaldo y la excepción de captura no dependen de `has_iva`. Su única definición se mantiene en los [permisos del Módulo 2](../07_fase4_evolucion_y_resiliencia.md#módulo-2-identidad-y-seguridad). La validación financiera debe aplicar esa política junto con la de cuentas y cobros, sin interpretar «Sin IVA» como autorización para omitir respaldo.

### Historial y evolución

Exigir una elección explícita para obras nuevas. Para las existentes, planificar una clasificación asistida y revisada antes de activar las restricciones; no rellenar masivamente `false` ni presentar un valor desconocido como booleano confirmado. Cualquier nulabilidad temporal de migración queda fuera del modelo final y bloquea operaciones financieras dependientes hasta regularizarse.

Una vez registrados movimientos o liquidaciones, impedir que una edición común de `has_iva` altere el historial. Corregir mediante un procedimiento autorizado y auditado que identifique sus efectos, preserve las políticas aplicadas y genere ajustes cuando corresponda. No recalcular ni trasladar automáticamente cobros o sueldos ya confirmados.

La secuencia de construcción, los resúmenes y los criterios de aceptación pertenecen al [Módulo 4 de Fase 4](../07_fase4_evolucion_y_resiliencia.md#módulo-4-motor-financiero-avanzado). Las operaciones financieras reutilizan la decisión de [idempotencia](0002-idempotencia-offline.md); la condición de IVA no sustituye la identificación de pagos.

## Consecuencias

- **Positivas:** separación auditable de fondos empresariales y de socios; una única condición selecciona cuentas elegibles, modalidades de cobro y política salarial; las lecturas y liquidaciones comparten la misma interpretación.
- **Compensaciones:** se requieren clasificación de históricos, cuentas identificadas, políticas versionadas y ajustes explícitos. Un booleano representa las dos modalidades acordadas, pero no modela por sí solo tasas, documentos tributarios ni escenarios fiscales adicionales.
- **Alternativas descartadas:** inferir la modalidad de la boleta, deducirla del usuario o mantener fórmulas distintas en cada pantalla. Esas opciones mezclan clasificación del trabajo, autorización y evidencia y permiten resultados contradictorios.
