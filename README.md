# Control de Finanzas V9 — Supabase · Control de pagos

Mejoras:
- Compromisos: pago marcado/desmarcado.
- Se eliminó el mensaje permanente "Pago registrado".
- Al registrar un pago, el próximo vencimiento se recalcula.
- Al deshacer un pago, se elimina el registro del periodo.
- Latino Seguros revierte/avanza su ciclo trimestral al marcar/desmarcar.
- Deudas: alertas de vencimiento por días.
- Deudas: botón para marcar el pago mínimo como realizado.
- Deudas: botón para deshacer un pago mínimo marcado por error.
- Al pagar una deuda, muestra el vencimiento del siguiente mes.
- Los cambios siguen guardándose directamente en Supabase.

No se requiere ejecutar SQL adicional para esta versión.
