# Control de Finanzas — Streamlit V2

Esta versión usa Streamlit + SQLite local. No usa Supabase todavía.

## Acceso privado
La app requiere usuario y contraseña usando Streamlit Secrets.

En Streamlit Community Cloud abre:

Manage app → Settings → Secrets

y pega:

```toml
[auth]
username = "Joan Santos"
password = "TU_CONTRASEÑA_PRIVADA"
```

No subas tu contraseña real a GitHub.

## Archivos que debes subir a GitHub
- app.py
- requirements.txt
- .gitignore
- assets/

El archivo `.streamlit/secrets.toml.example` es solo una guía y no contiene tu contraseña.

## Funciones V2
- Fondo blanco y diseño claro.
- Nombre: Control de Finanzas.
- Inicio de sesión privado.
- Tarjetas y préstamos con imagen.
- Botón para abrir el detalle de cada tarjeta/préstamo sin cerrar sesión.
- Actualización manual del saldo total.
- Registro de pagos.
- Pago mínimo marcado como pagado desde la pestaña Pagos.
- Historial de saldos y pagos.
- Compromisos fijos desglosados por categoría.
- Gastos diarios desglosados por categoría.
- Botones en Resumen para ver de qué se componen Compromisos y Gastos.
- Ingresos en USD con conversión a MXN.
- Respaldo y restauración SQLite.

## Importante
SQLite dentro de Streamlit Cloud no debe considerarse almacenamiento permanente. Usa la pestaña Respaldo con frecuencia hasta que migremos esta app a Supabase.


## V3 - Logos visuales
Se agregaron logos en Compromisos y Pagos, además de las tarjetas/préstamos del resumen y detalle.
