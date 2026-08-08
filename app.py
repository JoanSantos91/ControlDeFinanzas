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
  --bg:#f6f8fb;
  --panel:#ffffff;
  --card:#ffffff;
  --line:#dde5ef;
  --text:#132238;
  --muted:#69778a;
  --accent:#1769e0;
  --accent-soft:#eaf2ff;
  --good:#198754;
  --good-soft:#eaf8f1;
  --warn:#a56a00;
  --warn-soft:#fff7df;
  --bad:#c33a4a;
  --bad-soft:#fff0f2;
}
html,body,[class*="css"]{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.stApp{background:var(--bg);color:var(--text)}
.block-container{max-width:1480px;padding-top:1.15rem;padding-bottom:4rem}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}
[data-testid="stSidebar"] *{color:var(--text)}
h1,h2,h3,h4,p,span,label{color:var(--text)}
.hero{background:#fff;border:1px solid var(--line);border-radius:24px;padding:24px 26px;margin-bottom:16px;box-shadow:0 8px 26px rgba(23,42,69,.06)}
.kicker{color:var(--accent);font-size:.78rem;font-weight:850;letter-spacing:.15em;text-transform:uppercase}
.hero-title{font-size:2rem;font-weight:900;margin:.22rem 0 .35rem;color:var(--text)}
.hero-sub{color:var(--muted);font-size:.96rem}
.metric-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:14px 0 16px}
.metric-card{background:#fff;border:1px solid var(--line);border-radius:20px;padding:17px;min-height:112px;box-shadow:0 6px 18px rgba(23,42,69,.045)}
.metric-label{font-size:.77rem;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.045em}
.metric-value{font-size:1.48rem;font-weight:900;margin-top:7px;color:var(--text)}
.metric-note{font-size:.78rem;color:var(--muted);margin-top:5px}
.section-title{font-size:1.16rem;font-weight:900;margin:22px 0 10px;color:var(--text)}
.debt-card{background:#fff;border:1px solid var(--line);border-radius:22px;padding:15px;min-height:306px;box-shadow:0 7px 20px rgba(23,42,69,.045)}
.logo{height:92px;border-radius:15px;background:#fff;display:flex;align-items:center;justify-content:center;padding:8px;margin-bottom:12px;border:1px solid #edf1f5}
.logo img{max-width:100%;max-height:76px;object-fit:contain}
.logo-fallback{height:92px;border:1px dashed var(--line);border-radius:15px;display:flex;align-items:center;justify-content:center;margin-bottom:12px;font-weight:900;color:var(--text)}
.debt-name{font-size:1.02rem;font-weight:900;color:var(--text)}
.debt-value{font-size:1.52rem;font-weight:900;margin:4px 0;color:var(--text)}
.small{font-size:.80rem;color:var(--muted)}
.badge{display:inline-flex;border-radius:999px;padding:5px 9px;font-size:.72rem;font-weight:850;margin-top:8px}
.good{background:var(--good-soft);color:var(--good)}.warn{background:var(--warn-soft);color:var(--warn)}.bad{background:var(--bad-soft);color:var(--bad)}
.progress-track{height:10px;border-radius:999px;background:#e9eef5;overflow:hidden;margin-top:11px}
.progress-fill{height:100%;background:var(--accent);border-radius:999px}
.payline{display:grid;grid-template-columns:1.45fr .85fr .9fr .8fr;gap:10px;align-items:center;border:1px solid var(--line);background:#fff;border-radius:15px;padding:11px;margin:7px 0}
.info-box{background:#fff;border:1px solid var(--line);border-radius:18px;padding:16px;margin-bottom:12px}
.commitment-card{background:#fff;border:1px solid var(--line);border-radius:20px;padding:14px;box-shadow:0 6px 18px rgba(23,42,69,.04);margin-bottom:12px;min-height:260px}
.commitment-logo{height:82px;border-radius:14px;background:#fff;border:1px solid #edf1f5;display:flex;align-items:center;justify-content:center;padding:8px;margin-bottom:10px}
.commitment-logo img{max-height:66px;max-width:100%;object-fit:contain}
.commitment-fallback{height:82px;border-radius:14px;border:1px dashed var(--line);display:flex;align-items:center;justify-content:center;margin-bottom:10px;font-weight:900;color:var(--text)}
.commitment-name{font-size:1rem;font-weight:900;color:var(--text)}
.commitment-amount{font-size:1.3rem;font-weight:900;color:var(--text);margin:3px 0}
.payment-logo-row{display:grid;grid-template-columns:74px 1.5fr .8fr .8fr .85fr;gap:10px;align-items:center;border:1px solid var(--line);background:#fff;border-radius:16px;padding:10px 12px;margin:8px 0}
.payment-logo-box{width:64px;height:54px;border:1px solid #edf1f5;border-radius:12px;background:#fff;display:flex;align-items:center;justify-content:center;padding:5px;overflow:hidden}
.payment-logo-box img{max-width:100%;max-height:44px;object-fit:contain}
.login-wrap{max-width:460px;margin:8vh auto 0;background:white;border:1px solid var(--line);border-radius:26px;padding:26px;box-shadow:0 16px 42px rgba(23,42,69,.08)}
.login-title{text-align:center;font-size:1.65rem;font-weight:900;margin-bottom:4px}
.login-sub{text-align:center;color:var(--muted);margin-bottom:18px}
/* native widgets */
.stButton>button{border-radius:12px;border:1px solid #cfd9e7;background:#fff;color:var(--text);font-weight:750}
.stButton>button:hover{border-color:var(--accent);color:var(--accent)}
.stButton>button[kind="primary"]{background:var(--accent);color:#fff;border-color:var(--accent)}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:16px;padding:12px}
[data-testid="stMetricLabel"]{color:var(--muted)}
[data-testid="stMetricValue"]{color:var(--text)}
[data-testid="stDataFrame"]{background:#fff}
@media(max-width:900px){.metric-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:650px){.metric-grid{grid-template-columns:1fr}.payline{grid-template-columns:1fr 1fr}.hero-title{font-size:1.55rem}}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# AUTH
# ---------------------------
def auth_config():
    try:
        username = str(st.secrets["auth"]["username"])
        password = str(st.secrets["auth"]["password"])
        return username, password
    except Exception:
        return None, None

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    username_cfg, password_cfg = auth_config()
    st.markdown("<div class='login-wrap'><div class='login-title'>Control de Finanzas</div><div class='login-sub'>Acceso privado</div></div>", unsafe_allow_html=True)
    if not username_cfg or not password_cfg:
        st.error("Falta configurar el usuario y la contraseña en Streamlit Secrets.")
        st.code('[auth]\nusername = "Joan Santos"\npassword = "TU_CONTRASEÑA"', language="toml")
        st.stop()
    with st.form("login_form"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        ok = st.form_submit_button("Entrar", use_container_width=True, type="primary")
    if ok:
        if u == username_cfg and p == password_cfg:
            st.session_state.authenticated = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")
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
            notes TEXT DEFAULT ''
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
PAGES=["🏠 Resumen","💳 Deudas","📅 Pagos","🧾 Compromisos","💵 Ingresos","🛒 Gastos diarios","💾 Respaldo","⚙️ Configuración"]
if "nav" not in st.session_state: st.session_state.nav="🏠 Resumen"
if "selected_debt_id" not in st.session_state: st.session_state.selected_debt_id=None

st.sidebar.markdown(f"**Usuario:** {st.session_state.get('user','Joan Santos')}")
if st.sidebar.button("Cerrar sesión", use_container_width=True):
    st.session_state.authenticated=False
    st.session_state.pop("user",None)
    st.rerun()

page = st.sidebar.radio("Navegación",PAGES,index=PAGES.index(st.session_state.nav),key="nav_radio")
if page != st.session_state.nav:
    st.session_state.nav=page

fx=float(setting("mxn_per_usd","18.50"))
goal=float(setting("debt_goal_start","92664.81"))
ds=debts(); pmap=debt_paid_map(); expmap=expense_paid_map()
total_debt=sum(float(d["current_balance"] or 0) for d in ds)
minimum_total=sum(float(d["minimum_payment"] or 0) for d in ds)
paid_total=max(goal-total_debt,0)
progress=min(max(paid_total/goal if goal else 0,0),1)

st.markdown("""
<div class="hero">
  <div class="kicker">Panel personal</div>
  <div class="hero-title">Control de Finanzas</div>
  <div class="hero-sub">Prioridad principal: pagar tarjetas y préstamos. Vivienda, servicios, suscripciones y gastos diarios se muestran por separado.</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# RESUMEN
# ---------------------------
if st.session_state.nav == "🏠 Resumen":
    rs=recurring()
    fixed_mxn=sum(float(r["amount"] or 0)*(fx if r["currency"]=="USD" else 1) for r in rs)
    daily_month=one("SELECT COALESCE(SUM(amount_mxn),0) total FROM daily_expenses WHERE substr(expense_date,1,7)=?",(date.today().strftime("%Y-%m"),))
    daily_mxn=float(daily_month["total"] or 0) if daily_month else 0
    avg_income_usd=2000+(220*4)

    st.markdown(f"""
    <div class="metric-grid">
      <div class="metric-card"><div class="metric-label">Deuda principal</div><div class="metric-value">{money(total_debt)}</div><div class="metric-note">Tarjetas + préstamos</div></div>
      <div class="metric-card"><div class="metric-label">Pago mínimo mensual</div><div class="metric-value">{money(minimum_total)}</div><div class="metric-note">Compromiso mínimo de deuda</div></div>
      <div class="metric-card"><div class="metric-label">Compromisos fijos</div><div class="metric-value">{money(fixed_mxn)}</div><div class="metric-note">Vivienda, servicios y suscripciones</div></div>
      <div class="metric-card"><div class="metric-label">Gastos diarios del mes</div><div class="metric-value">{money(daily_mxn)}</div><div class="metric-note">Compras y gastos variables registrados</div></div>
    </div>
    """, unsafe_allow_html=True)

    b1,b2,b3=st.columns([1,1,1])
    with b1:
        if st.button("🔎 Ver de qué se componen mis compromisos",use_container_width=True): navigate("🧾 Compromisos")
    with b2:
        if st.button("🛒 Ver de qué se componen mis gastos",use_container_width=True): navigate("🛒 Gastos diarios")
    with b3:
        st.caption(f"Ingreso promedio estimado: US${avg_income_usd:,.0f}/mes · Tipo de cambio configurado: {fx:.2f}")

    st.subheader("🎯 Meta: llevar tarjetas y préstamos a $0")
    st.progress(progress,text=f"Avance {progress*100:.1f}% · Reducido {money(paid_total)} · Restante {money(total_debt)}")

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
    ids=[d["id"] for d in ds]
    default_idx=ids.index(st.session_state.selected_debt_id) if st.session_state.selected_debt_id in ids else 0
    d=st.selectbox("Selecciona una tarjeta o préstamo",ds,index=default_idx,format_func=lambda x:x["name"])
    st.session_state.selected_debt_id=d["id"]
    st.markdown(image_html(d["image_path"],d["institution"]),unsafe_allow_html=True)
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
    total_fixed=sum(float(r["amount"] or 0)*(fx if r["currency"]=="USD" else 1) for r in rs)
    st.metric("Total mensual aproximado",money(total_fixed))

    categories={}
    for r in rs:
        categories.setdefault(r["category"],[]).append(r)

    for cat,items in categories.items():
        st.markdown(f"<div class='section-title'>{cat}</div>",unsafe_allow_html=True)
        cols=st.columns(3)
        for i,r in enumerate(items):
            paid_now=expmap.get(r["id"],0)>0
            with cols[i%3]:
                logo=compact_image_html(r.get("image_path"),r["name"],"commitment-logo")
                status_html = "<span class='badge good'>✅ Pagado este mes</span>" if paid_now else "<span class='badge warn'>⏳ Pendiente</span>"
                st.markdown(f"""
                <div class='commitment-card'>
                  {logo}
                  <div class='commitment-name'>{r['name']}</div>
                  <div class='commitment-amount'>{money(r['amount'],r['currency'])}</div>
                  <div class='small'>Vence: {('día '+str(r['due_day'])) if r['due_day'] else r['frequency']}</div>
                  <div class='small'>Frecuencia: {r['frequency']}</div>
                  {status_html}
                </div>
                """,unsafe_allow_html=True)
                if not paid_now:
                    if st.button("Marcar como pagado",key=f"exp_{r['id']}",use_container_width=True):
                        execute("INSERT INTO expense_payments(expense_id,amount,currency,payment_date,period_year,period_month,note) VALUES(?,?,?,?,?,?,?)",(r["id"],r["amount"],r["currency"],t.isoformat(),t.year,t.month,"Marcado desde Compromisos"))
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
