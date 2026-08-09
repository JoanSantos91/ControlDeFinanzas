from pathlib import Path
from datetime import date, datetime
import calendar
import base64
import mimetypes
import sqlite3
import hashlib

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "finance_data.db"

st.set_page_config(
    page_title="Control de Finanzas",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# VISUAL: TEMA CLARO
# ---------------------------
st.markdown("""
<style>
:root{
  --navy:#08264a;--blue:#1463d6;--bg:#f4f7fb;--line:#dbe4ef;--text:#12233a;
  --muted:#617189;--good:#168356;--good-soft:#e9f8f1;--warn:#9b6500;--warn-soft:#fff6dc;
  --bad:#c03446;--bad-soft:#fff0f2;
}
html,body,[class*="css"]{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.stApp{background:linear-gradient(180deg,#f9fbfe 0%,#f3f6fb 100%);color:var(--text)}
.block-container{max-width:1500px;padding-top:1.25rem;padding-bottom:4rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#071f3b 0%,#0a2a50 100%);border-right:none}
[data-testid="stSidebar"] *{color:#f7fbff}
[data-testid="stSidebar"] .stButton>button{
  width:100%;background:transparent;color:#eef6ff;border:1px solid rgba(255,255,255,.10);
  border-radius:14px;font-size:1rem;font-weight:800;padding:.72rem .85rem;text-align:left
}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(255,255,255,.10);border-color:rgba(255,255,255,.25);color:#fff}
h1{font-size:2.25rem!important;font-weight:900!important;color:var(--text)!important}
h2{font-size:1.65rem!important;font-weight:900!important;color:var(--text)!important}
h3{font-size:1.35rem!important;font-weight:850!important;color:var(--text)!important}
p,span,label{font-size:1rem}
.hero{background:linear-gradient(135deg,#08264a 0%,#104d8f 100%);border-radius:26px;padding:28px 30px;margin-bottom:18px;box-shadow:0 16px 38px rgba(8,38,74,.16)}
.kicker{color:#9fd0ff;font-size:.86rem;font-weight:850;letter-spacing:.15em;text-transform:uppercase}
.hero-title{font-size:2.35rem;font-weight:950;margin:.25rem 0 .35rem;color:white!important}
.hero-sub{color:#dcecff;font-size:1.05rem;max-width:920px}
.hero-user{display:inline-flex;margin-top:14px;padding:7px 12px;border-radius:999px;background:rgba(255,255,255,.12);color:white;font-size:.88rem;font-weight:750}
.debt-card{background:#fff;border:1px solid var(--line);border-radius:24px;padding:17px;min-height:320px;box-shadow:0 9px 26px rgba(28,57,91,.06)}
.logo{height:102px;border-radius:17px;background:#fff;display:flex;align-items:center;justify-content:center;padding:9px;margin-bottom:13px;border:1px solid #edf1f5}
.logo img{max-width:100%;max-height:84px;object-fit:contain}
.logo-fallback{height:102px;border:1px dashed var(--line);border-radius:17px;display:flex;align-items:center;justify-content:center;margin-bottom:13px;font-weight:900;color:var(--navy);font-size:1.1rem}
.debt-name{font-size:1.15rem;font-weight:900;color:var(--navy)}
.debt-value{font-size:1.72rem;font-weight:950;margin:5px 0;color:var(--text)}
.small{font-size:.90rem;color:var(--muted);line-height:1.45}
.badge{display:inline-flex;border-radius:999px;padding:6px 10px;font-size:.80rem;font-weight:850;margin-top:9px}
.good{background:var(--good-soft);color:var(--good)}.warn{background:var(--warn-soft);color:var(--warn)}.bad{background:var(--bad-soft);color:var(--bad)}
.progress-track{height:11px;border-radius:999px;background:#e8eef6;overflow:hidden;margin-top:12px}
.progress-fill{height:100%;background:linear-gradient(90deg,#1463d6,#36a6ff);border-radius:999px}
.section-title{font-size:1.35rem;font-weight:900;margin:24px 0 12px;color:var(--navy)}
.commitment-card{background:#fff;border:1px solid var(--line);border-radius:22px;padding:16px;box-shadow:0 8px 22px rgba(28,57,91,.05);margin-bottom:12px;min-height:275px}
.commitment-logo{height:92px;border-radius:15px;background:#fff;border:1px solid #edf1f5;display:flex;align-items:center;justify-content:center;padding:8px;margin-bottom:11px}
.commitment-logo img{max-height:74px;max-width:100%;object-fit:contain}
.commitment-fallback{height:92px;border-radius:15px;border:1px dashed var(--line);display:flex;align-items:center;justify-content:center;margin-bottom:11px;font-weight:900;color:var(--navy)}
.commitment-name{font-size:1.08rem;font-weight:900;color:var(--navy)}
.commitment-amount{font-size:1.45rem;font-weight:950;color:var(--text);margin:4px 0}
.login-shell{max-width:520px;margin:7vh auto 0;background:#fff;border:1px solid var(--line);border-radius:30px;overflow:hidden;box-shadow:0 24px 60px rgba(8,38,74,.13)}
.login-head{padding:28px 30px 24px;background:linear-gradient(135deg,#08264a,#135ba6);color:white}
.login-head-title{font-size:2rem;font-weight:950;color:white}
.login-head-sub{font-size:1rem;color:#dbeeff;margin-top:5px}
.login-user{margin-top:18px;padding:13px 15px;border-radius:15px;background:rgba(255,255,255,.12);font-size:1.05rem;font-weight:850;color:white}
.stButton>button{border-radius:14px;border:1px solid #cad6e5;background:#fff;color:var(--navy);font-weight:800;font-size:1rem;min-height:48px}
.stButton>button:hover{border-color:var(--blue);color:var(--blue);background:#f7fbff}
.stButton>button[kind="primary"]{background:var(--blue);color:#fff;border-color:var(--blue)}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:18px;padding:15px;box-shadow:0 6px 18px rgba(28,57,91,.04)}
[data-testid="stMetricLabel"] p{font-size:.95rem!important;color:var(--muted)!important;font-weight:800!important}
[data-testid="stMetricValue"]{font-size:1.7rem!important;color:var(--navy)!important;font-weight:900!important}
div[data-testid="stForm"]{background:#fff;border:1px solid var(--line);border-radius:22px;padding:18px;box-shadow:0 7px 20px rgba(28,57,91,.04)}
.stButton>button p{font-size:1.02rem!important;line-height:1.38!important}
@media(max-width:900px){.metric-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:650px){.hero-title{font-size:1.8rem}.block-container{padding-left:.8rem;padding-right:.8rem}}

.goal-shell{
  display:grid;
  grid-template-columns:230px 1fr;
  gap:24px;
  align-items:center;
  background:linear-gradient(135deg,#071f3b 0%,#0b3768 62%,#145aa8 100%);
  border-radius:28px;
  padding:24px 26px;
  margin:12px 0 22px;
  box-shadow:0 18px 42px rgba(8,38,74,.18);
  overflow:hidden;
}
.goal-ring{
  --p:0;
  width:190px;height:190px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  background:conic-gradient(#4ade80 calc(var(--p)*1%), rgba(255,255,255,.16) 0);
  position:relative;margin:auto;
}
.goal-ring:after{
  content:"";position:absolute;width:148px;height:148px;border-radius:50%;
  background:#092a50;box-shadow:inset 0 0 0 1px rgba(255,255,255,.08);
}
.goal-ring-content{position:relative;z-index:2;text-align:center;color:#fff}
.goal-percent{font-size:2.15rem;font-weight:950;line-height:1}
.goal-label{font-size:.82rem;color:#cfe5ff;margin-top:6px;font-weight:700}
.goal-copy h3{color:#fff!important;font-size:1.5rem!important;margin:0 0 5px}
.goal-copy p{color:#d7e9ff;margin:0;font-size:1rem}
.goal-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:18px}
.goal-stat{background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.12);border-radius:16px;padding:12px}
.goal-stat-label{font-size:.78rem;color:#c9ddf5;font-weight:750}
.goal-stat-value{font-size:1.12rem;color:#fff;font-weight:900;margin-top:3px}
.goal-message{margin-top:14px;color:#aee9c9;font-weight:800;font-size:.94rem}
div[data-testid="column"] > div > div > div > div > .stButton > button{
  box-shadow:0 7px 18px rgba(28,57,91,.05);
}
button[kind="secondary"]{
  background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%)!important;
}
button[kind="secondary"]:hover{
  transform:translateY(-1px);
  box-shadow:0 10px 24px rgba(20,99,214,.10)!important;
}
@media(max-width:760px){
  .goal-shell{grid-template-columns:1fr;text-align:center}
  .goal-stats{grid-template-columns:1fr}
}


/* ===== V6: TARJETAS DEL RESUMEN ===== */
.summary-card-label{
  font-size:.77rem;
  font-weight:900;
  letter-spacing:.06em;
  text-transform:uppercase;
  margin-bottom:2px;
}
.st-key-summary_debt button,
.st-key-summary_minimum button,
.st-key-summary_commitments button,
.st-key-summary_daily button{
  min-height:158px!important;
  border-radius:24px!important;
  padding:18px 20px!important;
  text-align:left!important;
  justify-content:flex-start!important;
  align-items:flex-start!important;
  white-space:pre-line!important;
  border-width:1px!important;
  box-shadow:0 10px 26px rgba(25,56,94,.08)!important;
  transition:transform .16s ease, box-shadow .16s ease, border-color .16s ease!important;
}
.st-key-summary_debt button p,
.st-key-summary_minimum button p,
.st-key-summary_commitments button p,
.st-key-summary_daily button p{
  width:100%!important;
  text-align:left!important;
  font-size:1.03rem!important;
  line-height:1.48!important;
  font-weight:760!important;
  color:#13233a!important;
}
.st-key-summary_debt button:hover,
.st-key-summary_minimum button:hover,
.st-key-summary_commitments button:hover,
.st-key-summary_daily button:hover{
  transform:translateY(-3px)!important;
  box-shadow:0 16px 34px rgba(20,70,130,.13)!important;
}
.st-key-summary_debt button{
  background:linear-gradient(145deg,#ffffff 0%,#edf5ff 100%)!important;
  border-color:#b9d6fb!important;
  border-top:5px solid #1463d6!important;
}
.st-key-summary_minimum button{
  background:linear-gradient(145deg,#ffffff 0%,#f2efff 100%)!important;
  border-color:#d5cafa!important;
  border-top:5px solid #7957d5!important;
}
.st-key-summary_commitments button{
  background:linear-gradient(145deg,#ffffff 0%,#eefaf4 100%)!important;
  border-color:#bfe7d1!important;
  border-top:5px solid #168356!important;
}
.st-key-summary_daily button{
  background:linear-gradient(145deg,#ffffff 0%,#fff7e8 100%)!important;
  border-color:#f2dab1!important;
  border-top:5px solid #d98b18!important;
}
.st-key-summary_debt button p::first-line,
.st-key-summary_minimum button p::first-line,
.st-key-summary_commitments button p::first-line,
.st-key-summary_daily button p::first-line{
  font-weight:900!important;
}
@media(max-width:900px){
  .st-key-summary_debt button,
  .st-key-summary_minimum button,
  .st-key-summary_commitments button,
  .st-key-summary_daily button{min-height:140px!important}
}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# AUTH
# ---------------------------
def auth_config():
    try:
        auth = st.secrets["auth"]
        username = str(auth.get("username", "Joan Santos"))
        password = str(auth["password"])
        return username, password
    except Exception:
        return "Joan Santos", None

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    username_cfg, password_cfg = auth_config()
    st.markdown(f"""
    <div class="login-shell">
      <div class="login-head">
        <div class="kicker" style="color:#a8d5ff">Acceso privado</div>
        <div class="login-head-title">Control de Finanzas</div>
        <div class="login-head-sub">Tu panel financiero personal</div>
        <div class="login-user">👤 {username_cfg}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    if not password_cfg:
        st.error("Falta configurar la contraseña en Streamlit Secrets.")
        st.code('[auth]\nusername = "Joan Santos"\npassword = "TU_CONTRASEÑA"', language="toml")
        st.stop()
    c1,c2,c3 = st.columns([1,1.15,1])
    with c2:
        with st.form("login_form"):
            st.markdown("### Bienvenido, Joan")
            st.caption("Tu nombre ya está registrado. Escribe únicamente tu contraseña.")
            p = st.text_input("Contraseña", type="password", placeholder="••••••••")
            ok = st.form_submit_button("Entrar a mi cuenta", use_container_width=True, type="primary")
        if ok:
            if p == password_cfg:
                st.session_state.authenticated = True
                st.session_state.user = username_cfg
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    st.stop()

# ---------------------------
# SQLITE
# ---------------------------
def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c

def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS debts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            institution TEXT NOT NULL,
            debt_type TEXT NOT NULL,
            current_balance REAL NOT NULL DEFAULT 0,
            original_balance REAL,
            credit_limit REAL,
            available_credit REAL,
            minimum_payment REAL NOT NULL DEFAULT 0,
            due_day INTEGER,
            image_path TEXT,
            priority INTEGER DEFAULT 100,
            active INTEGER DEFAULT 1,
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS debt_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            debt_id INTEGER NOT NULL,
            previous_balance REAL,
            new_balance REAL NOT NULL,
            reason TEXT NOT NULL,
            note TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(debt_id) REFERENCES debts(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS debt_payments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            debt_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date TEXT NOT NULL,
            period_year INTEGER NOT NULL,
            period_month INTEGER NOT NULL,
            note TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(debt_id) REFERENCES debts(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS recurring_expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            currency TEXT NOT NULL DEFAULT 'MXN',
            amount REAL NOT NULL DEFAULT 0,
            frequency TEXT NOT NULL DEFAULT 'monthly',
            due_day INTEGER,
            variable_amount INTEGER DEFAULT 0,
            image_path TEXT,
            active INTEGER DEFAULT 1,
            notes TEXT DEFAULT '',
            next_due_date TEXT,
            coverage_start TEXT,
            coverage_end TEXT,
            policy_end TEXT,
            subsequent_amount REAL
        );
        CREATE TABLE IF NOT EXISTS expense_payments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            payment_date TEXT NOT NULL,
            period_year INTEGER NOT NULL,
            period_month INTEGER NOT NULL,
            note TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(expense_id) REFERENCES recurring_expenses(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS incomes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'USD',
            income_date TEXT NOT NULL,
            exchange_rate REAL,
            amount_mxn REAL,
            note TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS daily_expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            expense_date TEXT NOT NULL,
            exchange_rate REAL,
            amount_mxn REAL,
            note TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        """)
        # Migraciones suaves para versiones anteriores del archivo SQLite.
        existing_cols = {r[1] for r in c.execute("PRAGMA table_info(recurring_expenses)").fetchall()}
        for col, ddl in [
            ("next_due_date", "TEXT"),
            ("coverage_start", "TEXT"),
            ("coverage_end", "TEXT"),
            ("policy_end", "TEXT"),
            ("subsequent_amount", "REAL"),
        ]:
            if col not in existing_cols:
                c.execute(f"ALTER TABLE recurring_expenses ADD COLUMN {col} {ddl}")

        if c.execute("SELECT COUNT(*) FROM debts").fetchone()[0] == 0:
            seed = [
                ("Banorte Oro","Banorte","credit_card",13429.21,13429.21,15000.00,1570.79,990.47,30,"assets/banorte_oro.png",30,""),
                ("BBVA Crédito","BBVA","credit_card",25366.20,25366.20,24200.00,-1166.20,1200.00,5,"assets/bbva_credito.jpg",10,"Límite excedido"),
                ("BanCoppel Crédito","BanCoppel","credit_card",9756.46,9756.46,11000.00,1243.54,794.40,16,"assets/bancoppel_credito.png",40,""),
                ("BanCoppel Crédito Personal","BanCoppel","loan",12023.15,12023.15,12000.00,-23.15,1435.00,7,"assets/bancoppel_credito.png",20,""),
                ("Coppel Préstamo Personal","Coppel","loan",22000.00,22000.00,None,None,1500.00,5,"assets/bancoppel_credito.png",25,""),
                ("DiDi Préstamos","DiDi","loan",10089.79,10089.79,None,None,733.63,14,"assets/didi.png",35,""),
            ]
            c.executemany("""INSERT INTO debts(name,institution,debt_type,current_balance,original_balance,credit_limit,available_credit,minimum_payment,due_day,image_path,priority,notes)
                             VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""", seed)
        if c.execute("SELECT COUNT(*) FROM recurring_expenses").fetchone()[0] == 0:
            seed = [
                ("ChatGPT Plus","Suscripción","MXN",399,"monthly",1,0,"assets/chatgpt.jpg",1,""),
                ("iCloud Drive","Suscripción","MXN",49,"monthly",2,0,"assets/icloud.png",1,""),
                ("Amazon Prime","Suscripción","MXN",99,"monthly",17,0,"assets/amazon_prime.png",1,""),
                ("Infonavit","Vivienda México","MXN",4000,"monthly",30,0,"assets/infonavit.png",1,"Deuda total Infonavit: $347,534.72 MXN"),
                ("Megacable","Servicios México","MXN",700,"monthly",5,0,"assets/megacable.png",1,""),
                ("JAPAC","Servicios México","MXN",140,"monthly",24,0,"assets/japac.jpg",1,""),
                ("CFE","Servicios México","MXN",87,"bimonthly",21,1,"assets/cfe.jpg",1,"Variable. Último recibo pagado."),
                ("Telcel","Telefonía","MXN",699,"monthly",18,0,"assets/telcel.png",1,""),
                ("Renta actual","Vivienda USA","USD",560,"monthly",1,0,None,1,""),
            ]
            c.executemany("""INSERT INTO recurring_expenses(name,category,currency,amount,frequency,due_day,variable_amount,image_path,active,notes)
                             VALUES(?,?,?,?,?,?,?,?,?,?)""", seed)
        # Seguro de auto Latino Seguros: se agrega aunque la base ya exista.
        if c.execute("SELECT COUNT(*) FROM recurring_expenses WHERE name='Latino Seguros - Auto'").fetchone()[0] == 0:
            c.execute("""INSERT INTO recurring_expenses(
                name,category,currency,amount,frequency,due_day,variable_amount,image_path,active,notes,
                next_due_date,coverage_start,coverage_end,policy_end,subsequent_amount
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(
                "Latino Seguros - Auto","Seguro de auto","MXN",3486.00,"quarterly",29,0,
                "assets/latino_seguros.png",1,
                "Primer pago realizado por $3,486 MXN. Cobertura inicial del 29/07/2026 al 29/10/2026. "
                "Los pagos subsecuentes son de $2,673.95 MXN. Póliza con vigencia de un año.",
                "2026-10-29","2026-07-29","2026-10-29","2027-07-29",2673.95
            ))
            insurance_id = c.execute("SELECT id FROM recurring_expenses WHERE name='Latino Seguros - Auto'").fetchone()[0]
            c.execute("""INSERT INTO expense_payments(expense_id,amount,currency,payment_date,period_year,period_month,note)
                         VALUES(?,?,?,?,?,?,?)""",(
                insurance_id,3486.00,"MXN","2026-07-29",2026,7,
                "Primer pago de póliza. Cobertura 29/07/2026 a 29/10/2026."
            ))

        c.execute("INSERT OR IGNORE INTO settings(key,value) VALUES('mxn_per_usd','18.50')")
        c.execute("INSERT OR IGNORE INTO settings(key,value) VALUES('debt_goal_start','92664.81')")
        c.commit()

def rows(sql, params=()):
    with conn() as c:
        return [dict(r) for r in c.execute(sql, params).fetchall()]

def one(sql, params=()):
    with conn() as c:
        r = c.execute(sql, params).fetchone()
        return dict(r) if r else None

def execute(sql, params=()):
    with conn() as c:
        c.execute(sql, params)
        c.commit()

def setting(key, default):
    r = one("SELECT value FROM settings WHERE key=?", (key,))
    return r["value"] if r else default

def set_setting(key, value):
    execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value)))

init_db()

# ---------------------------
# HELPERS
# ---------------------------
def money(v, currency="MXN"):
    v = float(v or 0)
    return f"US${v:,.2f}" if currency == "USD" else f"${v:,.2f} MXN"

def due_date(day):
    t = date.today()
    last = calendar.monthrange(t.year, t.month)[1]
    return date(t.year, t.month, min(int(day or last), last))

def image_html(relpath, fallback):
    if relpath:
        p = APP_DIR / relpath
        if p.exists():
            mime = mimetypes.guess_type(p.name)[0] or "image/png"
            b64 = base64.b64encode(p.read_bytes()).decode()
            return f"<div class='logo'><img src='data:{mime};base64,{b64}'></div>"
    return f"<div class='logo-fallback'>{fallback}</div>"

def compact_image_html(relpath, fallback, wrapper='commitment-logo'):
    if relpath:
        p = APP_DIR / relpath
        if p.exists():
            mime = mimetypes.guess_type(p.name)[0] or "image/png"
            b64 = base64.b64encode(p.read_bytes()).decode()
            return f"<div class='{wrapper}'><img src='data:{mime};base64,{b64}'></div>"
    fallback_class = 'commitment-fallback' if wrapper == 'commitment-logo' else 'payment-logo-box'
    return f"<div class='{fallback_class}'>{fallback}</div>"

def debts(): return rows("SELECT * FROM debts WHERE active=1 ORDER BY priority,id")
def recurring(): return rows("SELECT * FROM recurring_expenses WHERE active=1 ORDER BY due_day,id")

def parse_iso_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except Exception:
        return None

def commitment_status(r):
    """Estado visual de un compromiso, incluyendo pagos trimestrales con fecha exacta."""
    next_due = parse_iso_date(r.get("next_due_date"))
    if next_due:
        days = (next_due - date.today()).days
        if days < 0:
            return f"Vencido hace {abs(days)} días", "bad"
        if days <= 7:
            return f"Próximo pago en {days} días", "warn" if days > 2 else "bad"
        return f"Próximo pago: {next_due.strftime('%d/%m/%Y')}", "good"
    due = due_date(r.get("due_day"))
    days = (due - date.today()).days
    if days < 0:
        return f"Vencido hace {abs(days)} días", "bad"
    if days <= 7:
        return f"Vence en {days} días", "warn" if days > 2 else "bad"
    return f"Vence día {due.day}", "good"

def debt_paid_map():
    t=date.today()
    r=rows("SELECT debt_id,COALESCE(SUM(amount),0) amount FROM debt_payments WHERE period_year=? AND period_month=? GROUP BY debt_id",(t.year,t.month))
    return {x["debt_id"]:float(x["amount"] or 0) for x in r}

def expense_paid_map():
    t=date.today()
    r=rows("SELECT expense_id,COALESCE(SUM(amount),0) amount FROM expense_payments WHERE period_year=? AND period_month=? GROUP BY expense_id",(t.year,t.month))
    return {x["expense_id"]:float(x["amount"] or 0) for x in r}

def navigate(page, debt_id=None):
    st.session_state.nav = page
    if debt_id is not None:
        st.session_state.selected_debt_id = debt_id
    st.rerun()

# ---------------------------
# NAVIGATION
# ---------------------------
PAGES=[
    ("🏠","Resumen","🏠 Resumen"),
    ("💳","Deudas","💳 Deudas"),
    ("📅","Pagos","📅 Pagos"),
    ("🧾","Compromisos","🧾 Compromisos"),
    ("💵","Ingresos","💵 Ingresos"),
    ("🛒","Gastos diarios","🛒 Gastos diarios"),
    ("💾","Respaldo","💾 Respaldo"),
    ("⚙️","Configuración","⚙️ Configuración"),
]
if "nav" not in st.session_state: st.session_state.nav="🏠 Resumen"
if "selected_debt_id" not in st.session_state: st.session_state.selected_debt_id=None
if "selected_commitment_id" not in st.session_state: st.session_state.selected_commitment_id=None

st.sidebar.markdown("## 💳 Control de Finanzas")
st.sidebar.caption("Banca personal · Panel privado")
st.sidebar.markdown(f"**👤 {st.session_state.get('user','Joan Santos')}**")
st.sidebar.divider()
for icon,label,target in PAGES:
    active = st.session_state.nav == target
    button_label = f"▸ {icon} {label}" if active else f"{icon} {label}"
    if st.sidebar.button(button_label, key=f"nav_{target}", use_container_width=True):
        navigate(target)
st.sidebar.divider()
if st.sidebar.button("↪ Cerrar sesión", use_container_width=True):
    st.session_state.authenticated=False
    st.session_state.pop("user",None)
    st.rerun()

fx=float(setting("mxn_per_usd","18.50"))
goal=float(setting("debt_goal_start","92664.81"))
ds=debts(); pmap=debt_paid_map(); expmap=expense_paid_map()
total_debt=sum(float(d["current_balance"] or 0) for d in ds)
minimum_total=sum(float(d["minimum_payment"] or 0) for d in ds)
paid_total=max(goal-total_debt,0)
progress=min(max(paid_total/goal if goal else 0,0),1)

st.markdown(f"""
<div class="hero">
  <div class="kicker">Panel financiero privado</div>
  <div class="hero-title">Control de Finanzas</div>
  <div class="hero-sub">Un solo lugar para controlar deudas, pagos, compromisos, ingresos y gastos, con prioridad en liquidar tarjetas y préstamos.</div>
  <div class="hero-user">👤 {st.session_state.get("user","Joan Santos")} &nbsp; · &nbsp; Sesión protegida</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# RESUMEN
# ---------------------------
if st.session_state.nav == "🏠 Resumen":
    rs=recurring()
    fixed_mxn=0.0
    for r in rs:
        amt=float(r["amount"] or 0)
        if r.get("frequency")=="quarterly" and r.get("subsequent_amount"):
            amt=float(r["subsequent_amount"] or amt)/3.0
        elif r.get("frequency")=="bimonthly":
            amt=amt/2.0
        fixed_mxn += amt*(fx if r["currency"]=="USD" else 1)
    daily_month=one("SELECT COALESCE(SUM(amount_mxn),0) total FROM daily_expenses WHERE substr(expense_date,1,7)=?",(date.today().strftime("%Y-%m"),))
    daily_mxn=float(daily_month["total"] or 0) if daily_month else 0
    avg_income_usd=2000+(220*4)

    st.markdown("### Tu panorama financiero")
    st.caption("Haz clic en cualquiera de las tarjetas para abrir el detalle completo.")
    m1,m2,m3,m4=st.columns(4, gap="medium")

    with m1:
        with st.container(key="summary_debt"):
            if st.button(
                f"💳  DEUDA PRINCIPAL\n\n{money(total_debt)}\n\nTarjetas + préstamos\nVer composición  ›",
                key="metric_debt",
                use_container_width=True
            ):
                st.session_state.selected_debt_id=None
                navigate("💳 Deudas")

    with m2:
        with st.container(key="summary_minimum"):
            if st.button(
                f"📅  PAGO MÍNIMO MENSUAL\n\n{money(minimum_total)}\n\nCompromiso de deuda\nRevisar pagos  ›",
                key="metric_minimum",
                use_container_width=True
            ):
                navigate("📅 Pagos")

    with m3:
        with st.container(key="summary_commitments"):
            if st.button(
                f"🧾  COMPROMISOS FIJOS\n\n{money(fixed_mxn)}\n\nVivienda + servicios\nVer obligaciones  ›",
                key="metric_commitments",
                use_container_width=True
            ):
                navigate("🧾 Compromisos")

    with m4:
        with st.container(key="summary_daily"):
            if st.button(
                f"🛒  GASTOS DEL MES\n\n{money(daily_mxn)}\n\nMovimientos registrados\nAbrir gastos  ›",
                key="metric_daily",
                use_container_width=True
            ):
                navigate("🛒 Gastos diarios")

    st.caption(f"💵 Ingreso promedio estimado: US${avg_income_usd:,.0f}/mes · Tipo de cambio configurado: {fx:.2f} MXN/USD")

    st.markdown("<div class='section-title'>🎯 Meta principal · Liquidar tarjetas y préstamos</div>", unsafe_allow_html=True)
    goal_pct = progress * 100
    st.markdown(f"""
    <div class="goal-shell">
      <div class="goal-ring" style="--p:{goal_pct:.2f}">
        <div class="goal-ring-content">
          <div class="goal-percent">{goal_pct:.1f}%</div>
          <div class="goal-label">completado</div>
        </div>
      </div>
      <div class="goal-copy">
        <h3>Camino hacia una deuda de $0</h3>
        <p>Cada actualización de saldo o pago registrado mueve automáticamente tu progreso.</p>
        <div class="goal-stats">
          <div class="goal-stat">
            <div class="goal-stat-label">Deuda inicial</div>
            <div class="goal-stat-value">{money(goal)}</div>
          </div>
          <div class="goal-stat">
            <div class="goal-stat-label">Has reducido</div>
            <div class="goal-stat-value">{money(paid_total)}</div>
          </div>
          <div class="goal-stat">
            <div class="goal-stat-label">Falta por liquidar</div>
            <div class="goal-stat-value">{money(total_debt)}</div>
          </div>
        </div>
        <div class="goal-message">{"🏆 Ya liquidaste todas tus deudas principales." if total_debt <= 0.01 else "💪 Tu objetivo sigue activo. Cada peso que baja el saldo cuenta."}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Mis tarjetas y préstamos</div>",unsafe_allow_html=True)
    cols=st.columns(3)
    for i,d in enumerate(ds):
        paid=pmap.get(d["id"],0); minimum=float(d["minimum_payment"] or 0); due=due_date(d["due_day"]); days=(due-date.today()).days
        if paid>=minimum and minimum>0: status,cls="Pagado este mes","good"
        elif days<0: status,cls=f"Vencido {abs(days)} días","bad"
        elif days<=3: status,cls=f"Vence en {days} días","bad"
        elif days<=7: status,cls=f"Vence en {days} días","warn"
        else: status,cls=f"Vence día {due.day}","good"
        original=float(d["original_balance"] or d["current_balance"] or 0)
        indiv=max(0,min(1,(original-float(d["current_balance"] or 0))/original if original else 0))
        with cols[i%3]:
            st.markdown(f"""
            <div class='debt-card'>
              {image_html(d['image_path'],d['institution'])}
              <div class='debt-name'>{d['name']}</div>
              <div class='debt-value'>{money(d['current_balance'])}</div>
              <div class='small'>Pago mínimo: {money(d['minimum_payment'])}</div>
              <div class='small'>Fecha límite: día {d['due_day']}</div>
              {"<div class='small'>Crédito disponible: "+money(d['available_credit'])+"</div>" if d['credit_limit'] is not None else ""}
              <span class='badge {cls}'>{status}</span>
              <div class='progress-track'><div class='progress-fill' style='width:{indiv*100:.1f}%'></div></div>
              <div class='small' style='margin-top:6px'>Reducción: {indiv*100:.1f}%</div>
            </div>
            """,unsafe_allow_html=True)
            if st.button(f"Ver {d['name']}",key=f"open_{d['id']}",use_container_width=True):
                navigate("💳 Deudas",d["id"])

# ---------------------------
# DEUDAS / DETALLE
# ---------------------------
elif st.session_state.nav == "💳 Deudas":
    st.subheader("💳 Tarjetas y préstamos")
    st.caption("Selecciona una cuenta para abrir su ficha completa, actualizar saldo, registrar pagos y consultar historial.")

    grid=st.columns(3)
    for i,item in enumerate(ds):
        with grid[i%3]:
            st.markdown(f"""
            <div class='debt-card'>
              {image_html(item['image_path'],item['institution'])}
              <div class='debt-name'>{item['name']}</div>
              <div class='debt-value'>{money(item['current_balance'])}</div>
              <div class='small'>Pago mínimo: {money(item['minimum_payment'])}</div>
              <div class='small'>Fecha límite: día {item['due_day']}</div>
              {"<div class='small'>Crédito disponible: "+money(item['available_credit'])+"</div>" if item['credit_limit'] is not None else ""}
            </div>
            """,unsafe_allow_html=True)
            if st.button("Abrir detalle de la cuenta",key=f"debt_open_{item['id']}",use_container_width=True,type="primary" if st.session_state.selected_debt_id==item["id"] else "secondary"):
                st.session_state.selected_debt_id=item["id"]
                st.rerun()

    ids=[x["id"] for x in ds]
    if st.session_state.selected_debt_id not in ids:
        st.info("Selecciona una tarjeta o préstamo arriba para ver su información detallada.")
        st.stop()

    d=next(x for x in ds if x["id"]==st.session_state.selected_debt_id)
    st.divider()
    st.markdown(f"## {d['name']}")
    c_logo,c_info=st.columns([1,2.4])
    with c_logo:
        rel=d.get("image_path")
        if rel and (APP_DIR/rel).exists():
            st.image(str(APP_DIR/rel),use_container_width=True)
    with c_info:
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Saldo actual",money(d["current_balance"]))
        c2.metric("Pago mínimo",money(d["minimum_payment"]))
        c3.metric("Fecha límite",f"Día {d['due_day']}")
        c4.metric("Disponible",money(d["available_credit"]) if d["available_credit"] is not None else "—")

    paid_this=pmap.get(d["id"],0); remaining=max(float(d["minimum_payment"] or 0)-paid_this,0)
    if remaining<=0.001:
        st.success(f"✅ Pago mínimo cubierto este mes. Has registrado {money(paid_this)}.")
    else:
        st.warning(f"Pendiente mínimo este mes: {money(remaining)}")

    t1,t2,t3=st.tabs(["Actualizar saldo total","Registrar pago","Historial"])
    with t1:
        with st.form("update_balance"):
            nb=st.number_input("Nuevo saldo total",min_value=0.0,value=float(d["current_balance"] or 0),step=100.0)
            mp=st.number_input("Pago mínimo actual",min_value=0.0,value=float(d["minimum_payment"] or 0),step=50.0)
            av=st.number_input("Crédito disponible",value=float(d["available_credit"] or 0),step=100.0,disabled=d["debt_type"]!="credit_card")
            reason=st.selectbox("Motivo",["Actualización del banco","Intereses","Compra nueva","Comisión","Ajuste manual","Otro"])
            note=st.text_input("Nota opcional")
            if st.form_submit_button("Guardar actualización",use_container_width=True,type="primary"):
                prev=float(d["current_balance"] or 0)
                execute("UPDATE debts SET current_balance=?,minimum_payment=?,available_credit=?,updated_at=? WHERE id=?",(nb,mp,av,datetime.now().isoformat(timespec="seconds"),d["id"]))
                execute("INSERT INTO debt_history(debt_id,previous_balance,new_balance,reason,note) VALUES(?,?,?,?,?)",(d["id"],prev,nb,reason,note))
                st.success("Saldo actualizado."); st.rerun()
    with t2:
        with st.form("payment"):
            amount=st.number_input("Monto pagado",min_value=0.01,value=max(remaining,0.01),step=100.0)
            pdate=st.date_input("Fecha de pago",value=date.today())
            reduce=st.checkbox("Reducir el saldo actual con este pago",value=True)
            note=st.text_input("Nota")
            if st.form_submit_button("Registrar pago",use_container_width=True,type="primary"):
                execute("INSERT INTO debt_payments(debt_id,amount,payment_date,period_year,period_month,note) VALUES(?,?,?,?,?,?)",(d["id"],amount,pdate.isoformat(),pdate.year,pdate.month,note))
                if reduce:
                    prev=float(d["current_balance"] or 0); new=max(prev-amount,0)
                    execute("UPDATE debts SET current_balance=?,updated_at=? WHERE id=?",(new,datetime.now().isoformat(timespec="seconds"),d["id"]))
                    execute("INSERT INTO debt_history(debt_id,previous_balance,new_balance,reason,note) VALUES(?,?,?,?,?)",(d["id"],prev,new,"Pago",note))
                st.success("Pago registrado."); st.rerun()
    with t3:
        hist=rows("SELECT created_at,previous_balance,new_balance,reason,note FROM debt_history WHERE debt_id=? ORDER BY id DESC",(d["id"],))
        payments=rows("SELECT payment_date,amount,note FROM debt_payments WHERE debt_id=? ORDER BY id DESC",(d["id"],))
        st.markdown("**Cambios de saldo**")
        if hist: st.dataframe(pd.DataFrame(hist),use_container_width=True,hide_index=True)
        else: st.info("Sin cambios registrados todavía.")
        st.markdown("**Pagos realizados**")
        if payments: st.dataframe(pd.DataFrame(payments),use_container_width=True,hide_index=True)
        else: st.info("Sin pagos registrados todavía.")

# ---------------------------
# PAGOS
# ---------------------------
elif st.session_state.nav == "📅 Pagos":
    st.subheader("📅 Pagos de tarjetas y préstamos")
    st.caption("Cada deuda se muestra con su logo. Puedes abrir el detalle o marcar rápidamente el pago mínimo del mes.")
    for d in ds:
        paid=pmap.get(d["id"],0); minp=float(d["minimum_payment"] or 0); remaining=max(minp-paid,0)
        c_logo,c_info,c_min,c_paid,c_action=st.columns([.7,2,1,1,1.15])
        with c_logo:
            rel=d.get("image_path")
            if rel and (APP_DIR/rel).exists():
                st.image(str(APP_DIR/rel),use_container_width=True)
            else:
                st.markdown(f"**{d['institution']}**")
        with c_info:
            st.write(f"**{d['name']}**")
            st.caption(f"Fecha límite: día {d['due_day']}")
            if st.button("Ver detalle",key=f"pay_detail_{d['id']}",use_container_width=True):
                navigate("💳 Deudas",d["id"])
        c_min.write(f"Mínimo  \n**{money(minp)}**")
        c_paid.write(f"Pagado  \n**{money(paid)}**")
        with c_action:
            if remaining<=0.001:
                st.success("✅ Pagado")
            elif st.button("Marcar mínimo pagado",key=f"quickpay_{d['id']}",use_container_width=True):
                t=date.today()
                execute("INSERT INTO debt_payments(debt_id,amount,payment_date,period_year,period_month,note) VALUES(?,?,?,?,?,?)",(d["id"],remaining,t.isoformat(),t.year,t.month,"Pago mínimo marcado desde Pagos"))
                prev=float(d["current_balance"] or 0); new=max(prev-remaining,0)
                execute("UPDATE debts SET current_balance=?,updated_at=? WHERE id=?",(new,datetime.now().isoformat(timespec="seconds"),d["id"]))
                execute("INSERT INTO debt_history(debt_id,previous_balance,new_balance,reason,note) VALUES(?,?,?,?,?)",(d["id"],prev,new,"Pago","Pago mínimo marcado desde Pagos"))
                st.rerun()
        st.divider()

# ---------------------------
# COMPROMISOS
# ---------------------------
elif st.session_state.nav == "🧾 Compromisos":
    st.subheader("🧾 Mis compromisos fijos")
    st.caption("Vivienda, servicios y suscripciones con sus logos. Cada tarjeta te muestra monto, vencimiento y estado del pago del mes.")
    rs=recurring(); t=date.today()
    # Promedio mensual: trimestrales se prorratean entre 3 para no inflar el total del mes.
    total_fixed=0.0
    for r in rs:
        amt=float(r["amount"] or 0)
        if r.get("frequency")=="quarterly" and r.get("subsequent_amount"):
            amt=float(r["subsequent_amount"] or amt)/3.0
        elif r.get("frequency")=="bimonthly":
            amt=amt/2.0
        total_fixed += amt*(fx if r["currency"]=="USD" else 1)
    st.metric("Compromisos promedio por mes",money(total_fixed))

    categories={}
    for r in rs:
        categories.setdefault(r["category"],[]).append(r)

    for cat,items in categories.items():
        st.markdown(f"<div class='section-title'>{cat}</div>",unsafe_allow_html=True)
        cols=st.columns(3)
        for i,r in enumerate(items):
            paid_now=expmap.get(r["id"],0)>0
            status_text,status_cls=commitment_status(r)
            display_amount = float(r["subsequent_amount"] or r["amount"] or 0) if r.get("next_due_date") else float(r["amount"] or 0)
            with cols[i%3]:
                logo=compact_image_html(r.get("image_path"),r["name"],"commitment-logo")
                status_html = f"<span class='badge {status_cls}'>{status_text}</span>"
                due_text = r.get("next_due_date") or (("día "+str(r["due_day"])) if r["due_day"] else r["frequency"])
                freq_label = {"monthly":"Mensual","bimonthly":"Bimestral","quarterly":"Trimestral"}.get(r["frequency"],r["frequency"])
                st.markdown(f"""
                <div class='commitment-card'>
                  {logo}
                  <div class='commitment-name'>{r['name']}</div>
                  <div class='commitment-amount'>{money(display_amount,r['currency'])}</div>
                  <div class='small'>Próximo vencimiento: {due_text}</div>
                  <div class='small'>Frecuencia: {freq_label}</div>
                  {status_html}
                </div>
                """,unsafe_allow_html=True)
                if st.button("Ver detalle",key=f"commit_detail_{r['id']}",use_container_width=True):
                    st.session_state.selected_commitment_id=r["id"]
                    st.rerun()
                if st.session_state.selected_commitment_id == r["id"]:
                    if r.get("next_due_date"):
                        st.info(
                            f"{r['name']} · {r['category']} · Próximo pago {money(r['subsequent_amount'] or r['amount'],r['currency'])} "
                            f"el {r['next_due_date']} · Cobertura actual {r.get('coverage_start') or '—'} a {r.get('coverage_end') or '—'} · "
                            f"Póliza vigente hasta {r.get('policy_end') or '—'}."
                        )
                    else:
                        st.info(
                            f"{r['name']} · {r['category']} · {money(r['amount'],r['currency'])} · "
                            f"Vence {('día '+str(r['due_day'])) if r['due_day'] else r['frequency']} · "
                            f"Frecuencia: {r['frequency']}."
                        )
                    if r.get("notes"):
                        st.caption(r["notes"])
                if not paid_now:
                    if st.button("Marcar como pagado",key=f"exp_{r['id']}",use_container_width=True):
                        pay_amount = float(r["subsequent_amount"] or r["amount"] or 0) if r.get("next_due_date") else float(r["amount"] or 0)
                        execute("INSERT INTO expense_payments(expense_id,amount,currency,payment_date,period_year,period_month,note) VALUES(?,?,?,?,?,?,?)",
                                (r["id"],pay_amount,r["currency"],t.isoformat(),t.year,t.month,"Marcado desde Compromisos"))
                        if r.get("frequency")=="quarterly" and r.get("next_due_date"):
                            from datetime import timedelta
                            old_due=parse_iso_date(r["next_due_date"])
                            if old_due:
                                # Avance trimestral conservando el día 29 cuando sea posible.
                                month=old_due.month+3
                                year=old_due.year+(month-1)//12
                                month=(month-1)%12+1
                                last=calendar.monthrange(year,month)[1]
                                new_due=date(year,month,min(old_due.day,last))
                                execute("""UPDATE recurring_expenses
                                           SET coverage_start=?,coverage_end=?,next_due_date=?,amount=?
                                           WHERE id=?""",
                                        (old_due.isoformat(),new_due.isoformat(),new_due.isoformat(),pay_amount,r["id"]))
                        st.rerun()
                else:
                    st.success("Pago registrado")
                if r.get("notes"):
                    with st.expander("Ver información"):
                        st.write(r["notes"])

# ---------------------------
# INGRESOS
# ---------------------------
elif st.session_state.nav == "💵 Ingresos":
    st.subheader("💵 Ingresos")
    with st.form("income_form"):
        source=st.selectbox("Fuente",["Cheque quincenal","Tips semanales","Ingreso extra","Otro"])
        amount=st.number_input("Monto USD",min_value=0.0,step=10.0)
        idate=st.date_input("Fecha",value=date.today())
        rate=st.number_input("Tipo de cambio MXN/USD",min_value=1.0,value=fx,step=.05)
        note=st.text_input("Nota")
        if st.form_submit_button("Guardar ingreso",use_container_width=True,type="primary"):
            execute("INSERT INTO incomes(source,amount,currency,income_date,exchange_rate,amount_mxn,note) VALUES(?,?,?,?,?,?,?)",(source,amount,"USD",idate.isoformat(),rate,amount*rate,note))
            st.success("Ingreso guardado.")
    data=rows("SELECT source,amount,currency,income_date,exchange_rate,amount_mxn,note FROM incomes ORDER BY income_date DESC,id DESC")
    if data: st.dataframe(pd.DataFrame(data),use_container_width=True,hide_index=True)

# ---------------------------
# GASTOS DIARIOS
# ---------------------------
elif st.session_state.nav == "🛒 Gastos diarios":
    st.subheader("🛒 Mis gastos diarios")
    current=one("SELECT COALESCE(SUM(amount_mxn),0) total FROM daily_expenses WHERE substr(expense_date,1,7)=?",(date.today().strftime("%Y-%m"),))
    st.metric("Gastos registrados este mes",money(current["total"] if current else 0))
    with st.form("daily_form"):
        cat=st.selectbox("Categoría",["Comida","Gasolina","Supermercado","Ocio","Compras","Transporte","Salud","Otro"])
        desc=st.text_input("Descripción")
        cur=st.selectbox("Moneda",["USD","MXN"])
        amount=st.number_input("Monto",min_value=0.0,step=5.0)
        dte=st.date_input("Fecha",value=date.today())
        rate=st.number_input("Tipo de cambio",min_value=1.0,value=fx,step=.05,disabled=cur=="MXN")
        note=st.text_input("Nota")
        if st.form_submit_button("Guardar gasto",use_container_width=True,type="primary"):
            mxn=amount if cur=="MXN" else amount*rate
            execute("INSERT INTO daily_expenses(category,description,amount,currency,expense_date,exchange_rate,amount_mxn,note) VALUES(?,?,?,?,?,?,?,?)",(cat,desc,amount,cur,dte.isoformat(),None if cur=="MXN" else rate,mxn,note))
            st.success("Gasto guardado.")
    data=rows("SELECT category,description,amount,currency,expense_date,amount_mxn,note FROM daily_expenses ORDER BY expense_date DESC,id DESC")
    if data:
        df=pd.DataFrame(data)
        st.markdown("**Desglose por categoría**")
        summary=df.groupby("category",as_index=False)["amount_mxn"].sum().sort_values("amount_mxn",ascending=False)
        st.dataframe(summary,use_container_width=True,hide_index=True)
        st.markdown("**Detalle de movimientos**")
        st.dataframe(df,use_container_width=True,hide_index=True)
    else: st.info("Todavía no has registrado gastos diarios.")

# ---------------------------
# RESPALDO
# ---------------------------
elif st.session_state.nav == "💾 Respaldo":
    st.subheader("💾 Respaldo")
    st.warning("Esta versión usa SQLite local dentro de Streamlit. Descarga el respaldo con frecuencia porque Streamlit Cloud puede reiniciar el contenedor.")
    if DB_PATH.exists():
        st.download_button("⬇️ Descargar respaldo completo",DB_PATH.read_bytes(),file_name=f"control_finanzas_{date.today().isoformat()}.db",mime="application/octet-stream",use_container_width=True)
    up=st.file_uploader("Restaurar respaldo .db",type=["db"])
    if up and st.button("Restaurar respaldo",type="primary",use_container_width=True):
        DB_PATH.write_bytes(up.getvalue()); st.success("Respaldo restaurado."); st.rerun()

# ---------------------------
# CONFIG
# ---------------------------
else:
    st.subheader("⚙️ Configuración")
    newfx=st.number_input("Tipo de cambio: MXN por 1 USD",min_value=1.0,value=fx,step=.05)
    newgoal=st.number_input("Deuda inicial de la meta",min_value=0.0,value=goal,step=100.0)
    if st.button("Guardar configuración",use_container_width=True,type="primary"):
        set_setting("mxn_per_usd",newfx); set_setting("debt_goal_start",newgoal)
        st.success("Configuración guardada."); st.rerun()
