# Control de Finanzas V8 — Supabase

Esta versión ya no usa SQLite. Guarda directamente en Supabase/PostgreSQL.

## Secrets de Streamlit

[auth]
username = "Joan Santos"
password = "TU_CONTRASEÑA_DE_LA_APP"

[database]
url = "TU_CADENA_SESSION_POOLER_COMPLETA_DE_SUPABASE"

## GitHub
Sube:
- app.py
- requirements.txt
- assets/
- .gitignore

El SQL se incluye solo como referencia, ya que las tablas ya fueron creadas.

## Verificación
En la aplicación abre:
☁️ Base de datos

Debe mostrar "Conexión a Supabase activa" y los conteos de registros.
