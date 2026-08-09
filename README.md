# Control de Finanzas — Streamlit V7

Mejoras V7:
- Barra lateral corregida: botones blancos con texto azul marino grande y legible.
- Resumen y meta visual conservados.
- Se agregó bloque de próximos compromisos importantes en el inicio.
- La lógica de compromisos ahora calcula el próximo vencimiento usando el último pago.
- Al marcar un compromiso mensual como pagado, deja de mostrarlo vencido y pasa al próximo mes.
- Compromisos bimestrales avanzan dos meses desde el último pago.
- Latino Seguros conserva fecha exacta trimestral y al pagar avanza automáticamente tres meses.
- Cada compromiso muestra la fecha del último pago registrado.
- Compatible con la base SQLite existente.

Secrets:
[auth]
username = "Joan Santos"
password = "TU_CONTRASEÑA"
