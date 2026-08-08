
from pathlib import Path
from datetime import date, datetime
import calendar
import base64
import mimetypes
import sqlite3
import shutil
import io

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "finance_data.db"

st.set_page_config(
    page_title="Mi Libertad Financiera",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- VISUAL ----------
st.markdown("""
<style>
:root{
  --bg:#07111f; --panel:#0f1b2d; --card:#14233a; --line:#253a58;
  --text:#f8fafc; --muted:#a8b3c7; --accent:#55d6be;
  --good:#47d7a7; --warn:#ffd166; --bad:#ff7b8a;
}
.stApp{
  background:
  radial-gradient(circle at 8% 0%,rgba(41,121,255,.20),transparent 26%),
  radial-gradient(circle at 92% 6%,rgba(85,214,190,.12),transparent 24%),
  linear-gradient(180deg,#07111f 0%,#0a1424 100%);
  color:var(--text);
}
.block-container{max-width:1500px;padding-top:1.1rem;padding-bottom:4rem}
[data-testid="stSidebar"]{background:#081321;border-right:1px solid var(--line)}
h1,h2,h3{color:var(--text)}
.hero{
  border:1px solid var(--line); border-radius:26px; padding:26px 28px;
  background:rgba(15,27,45,.84); margin-bottom:16px;
}
.kicker{color:var(--accent);font-size:.78rem;font-weight:850;letter-spacing:.16em;text-transform:uppercase}
.hero-title{font-size:2rem;font-weight:900;margin:.25rem 0}
.muted{color:var(--muted)}
.metric-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:14px 0 18px}
.metric-card{border:1px solid var(--line);background:rgba(20,35,58,.94);border-radius:20px;padding:17px;min-height:112px}
.metric-label{font-size:.78rem;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.04em}
.metric-value{font-size:1.55rem;font-weight:900;margin-top:7px}
.metric-note{font-size:.78rem;color:var(--muted);margin-top:5px}
.debt-card{border:1px solid var(--line);background:rgba(20,35,58,.95);border-radius:22px;padding:15px;min-height:325px;margin-bottom:12px}
.logo{height:92px;border-radius:15px;background:#fff;display:flex;align-items:center;justify-content:center;padding:8px;margin-bottom:12px}
.logo img{max-width:100%;max-height:76px;object-fit:contain}
.logo-fallback{height:92px;border:1px dashed var(--line);border-radius:15px;display:flex;align-items:center;justify-content:center;margin-bottom:12px;font-weight:900}
.debt-name{font-size:1.05rem;font-weight:900}
.debt-value{font-size:1.55rem;font-weight:900;margin:4px 0}
.small{font-size:.80rem;color:var(--muted)}
.badge{display:inline-flex;border-radius:999px;padding:5px 9px;font-size:.72rem;font-weight:850;margin-top:8px}
.good{background:rgba(71,215,167,.13);color:#79e5be}.warn{background:rgba(255,209,102,.13);color:#ffe093}.bad{background:rgba(255,123,138,.13);color:#ffacb7}
.progress-track{height:10px;border-radius:999px;background:#263956;overflow:hidden;margin-top:11px}
.progress-fill{height:100%;background:var(--accent);border-radius:999px}
.payline{display:grid;grid-template-columns:1.5fr .9fr .9fr .8fr;gap:10px;align-items:center;border:1px solid var(--line);background:rgba(15,27,45,.72);border-radius:15px;padding:11px;margin:7px 0}
.section-title{font-size:1.15rem;font-weight:900;margin:20px 0 9px}
@media(max-width:900px){.metric-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:650px){.metric-grid{grid-template-columns:1fr}.payline{grid-template-columns:1fr 1fr}.hero-title{font-size:1.55rem}}
</style>
""", unsafe_allow_html=True)

# ---------- DATABASE ----------
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
        CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """)

        if c.execute("SELECT COUNT(*) FROM debts").fetchone()[0] == 0:
            debts = [
                ("Banorte Oro","Banorte","credit_card",13429.21,13429.21,15000.00,1570.79,990.47,30,"assets/banorte_oro.png",30,""),
                ("BBVA Crédito","BBVA","credit_card",25366.20,25366.20,24200.00,-1166.20,1200.00,5,"assets/bbva_credito.jpg",10,"Límite excedido"),
                ("BanCoppel Crédito","BanCoppel","credit_card",9756.46,9756.46,11000.00,1243.54,794.40,16,"assets/bancoppel_credito.png",40,""),
                ("BanCoppel Crédito Personal","BanCoppel","loan",12023.15,12023.15,12000.00,-23.15,1435.00,7,"assets/bancoppel_credito.png",20,""),
                ("Coppel Préstamo Personal","Coppel","loan",22000.00,22000.00,None,None,1500.00,5,"assets/bancoppel_credito.png",25,""),
                ("DiDi Préstamos","DiDi","loan",10089.79,10089.79,None,None,733.63,14,"assets/didi.png",35,""),
            ]
            c.executemany("""INSERT INTO debts(name,institution,debt_type,current_balance,original_balance,credit_limit,available_credit,minimum_payment,due_day,image_path,priority,notes)
                             VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""", debts)

        if c.execute("SELECT COUNT(*) FROM recurring_expenses").fetchone()[0] == 0:
            expenses = [
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
                             VALUES(?,?,?,?,?,?,?,?,?,?)""", expenses)

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

# ---------- HELPERS ----------
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

def debts():
    return rows("SELECT * FROM debts WHERE active=1 ORDER BY priority,id")

def recurring():
    return rows("SELECT * FROM recurring_expenses WHERE active=1 ORDER BY due_day,id")

def debt_paid_map():
    t=date.today()
    r=rows("""SELECT debt_id,COALESCE(SUM(amount),0) amount FROM debt_payments
              WHERE period_year=? AND period_month=? GROUP BY debt_id""",(t.year,t.month))
    return {x["debt_id"]:float(x["amount"] or 0) for x in r}

def expense_paid_map():
    t=date.today()
    r=rows("""SELECT expense_id,COALESCE(SUM(amount),0) amount FROM expense_payments
              WHERE period_year=? AND period_month=? GROUP BY expense_id""",(t.year,t.month))
    return {x["expense_id"]:float(x["amount"] or 0) for x in r}

# ---------- APP ----------
fx = float(setting("mxn_per_usd","18.50"))
goal = float(setting("debt_goal_start","92664.81"))
ds = debts()
total_debt = sum(float(d["current_balance"] or 0) for d in ds)
minimum_total = sum(float(d["minimum_payment"] or 0) for d in ds)
paid_total = max(goal-total_debt,0)
goal_progress = min(max(paid_total/goal if goal else 0,0),1)

page = st.sidebar.radio(
    "Navegación",
    ["🏠 Resumen","💳 Deudas","📅 Pagos","💵 Ingresos","🧾 Gastos fijos","🛒 Gastos diarios","💾 Respaldo","⚙️ Configuración"]
)

st.markdown("""
<div class="hero">
  <div class="kicker">Control financiero personal</div>
  <div class="hero-title">Mi Libertad Financiera</div>
  <div class="muted">Objetivo principal: liquidar tarjetas y préstamos. Infonavit, vivienda, servicios y gastos diarios se controlan por separado.</div>
</div>
""", unsafe_allow_html=True)

if page == "🏠 Resumen":
    rs = recurring()
    recurring_mxn = sum(float(r["amount"] or 0)*(fx if r["currency"]=="USD" else 1) for r in rs)
    avg_income_usd = 2000 + (220*4)
    avg_income_mxn = avg_income_usd*fx

    st.markdown(f"""
    <div class="metric-grid">
      <div class="metric-card"><div class="metric-label">Deuda principal</div><div class="metric-value">{money(total_debt)}</div><div class="metric-note">Tarjetas + préstamos</div></div>
      <div class="metric-card"><div class="metric-label">Pago mínimo mensual</div><div class="metric-value">{money(minimum_total)}</div><div class="metric-note">Compromiso mínimo conocido</div></div>
      <div class="metric-card"><div class="metric-label">Ingreso promedio</div><div class="metric-value">US${avg_income_usd:,.0f}</div><div class="metric-note">≈ {money(avg_income_mxn)} al TC configurado</div></div>
      <div class="metric-card"><div class="metric-label">Gastos fijos conocidos</div><div class="metric-value">{money(recurring_mxn)}</div><div class="metric-note">Incluye renta convertida a MXN</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🎯 Camino hacia $0")
    st.progress(goal_progress, text=f"Avance {goal_progress*100:.1f}% · Has reducido {money(paid_total)} · Restante {money(total_debt)}")

    st.markdown("<div class='section-title'>Tarjetas y préstamos</div>", unsafe_allow_html=True)
    pmap = debt_paid_map()
    cols = st.columns(3)
    for i,d in enumerate(ds):
        paid = pmap.get(d["id"],0)
        minimum = float(d["minimum_payment"] or 0)
        due = due_date(d["due_day"])
        days=(due-date.today()).days
        if paid >= minimum and minimum > 0:
            status, cls = "Pagado este mes","good"
        elif days < 0:
            status, cls = f"Vencido hace {abs(days)} días","bad"
        elif days <= 3:
            status, cls = f"Vence en {days} días","bad"
        elif days <= 7:
            status, cls = f"Vence en {days} días","warn"
        else:
            status, cls = f"Vence día {due.day}","good"
        original=float(d["original_balance"] or d["current_balance"] or 0)
        indiv=max(0,min(1,(original-float(d["current_balance"] or 0))/original if original else 0))
        with cols[i%3]:
            st.markdown(f"""
            <div class="debt-card">
              {image_html(d["image_path"],d["institution"])}
              <div class="debt-name">{d["name"]}</div>
              <div class="debt-value">{money(d["current_balance"])}</div>
              <div class="small">Mínimo: {money(d["minimum_payment"])} · Fecha límite: día {d["due_day"]}</div>
              {"<div class='small'>Disponible: "+money(d["available_credit"])+"</div>" if d["credit_limit"] is not None else ""}
              <span class="badge {cls}">{status}</span>
              <div class="progress-track"><div class="progress-fill" style="width:{indiv*100:.1f}%"></div></div>
              <div class="small" style="margin-top:6px">Reducción individual: {indiv*100:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Próximos pagos de deuda</div>", unsafe_allow_html=True)
    upcoming=[]
    for d in ds:
        due=due_date(d["due_day"])
        paid=pmap.get(d["id"],0)
        rem=max(float(d["minimum_payment"] or 0)-paid,0)
        upcoming.append((due,d,rem))
    upcoming.sort(key=lambda x:x[0])
    for due,d,rem in upcoming:
        st.markdown(f"""
        <div class="payline">
          <div><b>{d["name"]}</b><div class="small">{d["institution"]}</div></div>
          <div><b>{due.strftime("%d/%m/%Y")}</b><div class="small">Fecha límite</div></div>
          <div><b>{money(rem)}</b><div class="small">Pendiente mínimo</div></div>
          <div>{"✅ Pagado" if rem<=0.001 else "⏳ Pendiente"}</div>
        </div>
        """, unsafe_allow_html=True)

elif page == "💳 Deudas":
    d = st.selectbox("Selecciona una deuda", ds, format_func=lambda x:x["name"])
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Saldo actual",money(d["current_balance"]))
    c2.metric("Pago mínimo",money(d["minimum_payment"]))
    c3.metric("Vence",f"Día {d['due_day']}")
    c4.metric("Disponible",money(d["available_credit"]) if d["available_credit"] is not None else "—")

    t1,t2,t3=st.tabs(["Actualizar saldo total","Registrar pago","Historial"])
    with t1:
        with st.form("update_balance"):
            newbal=st.number_input("Nuevo saldo total",min_value=0.0,value=float(d["current_balance"] or 0),step=100.0)
            minpay=st.number_input("Pago mínimo actual",min_value=0.0,value=float(d["minimum_payment"] or 0),step=50.0)
            reason=st.selectbox("Motivo",["Actualización del banco","Intereses","Compra nueva","Comisión","Ajuste manual","Otro"])
            avail=st.number_input("Crédito disponible",value=float(d["available_credit"] or 0),step=100.0,disabled=d["debt_type"]!="credit_card")
            note=st.text_input("Nota opcional")
            if st.form_submit_button("Guardar actualización",use_container_width=True):
                prev=float(d["current_balance"] or 0)
                execute("UPDATE debts SET current_balance=?,minimum_payment=?,available_credit=?,updated_at=? WHERE id=?",
                        (newbal,minpay,avail,datetime.now().isoformat(timespec="seconds"),d["id"]))
                execute("INSERT INTO debt_history(debt_id,previous_balance,new_balance,reason,note) VALUES(?,?,?,?,?)",
                        (d["id"],prev,newbal,reason,note))
                st.success("Saldo actualizado.")
                st.rerun()
    with t2:
        with st.form("register_payment"):
            amt=st.number_input("Monto pagado",min_value=0.01,step=100.0)
            pdate=st.date_input("Fecha de pago",value=date.today())
            reduce=st.checkbox("Reducir también el saldo actual con este pago",value=True)
            note=st.text_input("Nota")
            if st.form_submit_button("Registrar pago",use_container_width=True):
                execute("""INSERT INTO debt_payments(debt_id,amount,payment_date,period_year,period_month,note)
                           VALUES(?,?,?,?,?,?)""",(d["id"],amt,pdate.isoformat(),pdate.year,pdate.month,note))
                if reduce:
                    prev=float(d["current_balance"] or 0); new=max(prev-amt,0)
                    execute("UPDATE debts SET current_balance=?,updated_at=? WHERE id=?",(new,datetime.now().isoformat(timespec="seconds"),d["id"]))
                    execute("INSERT INTO debt_history(debt_id,previous_balance,new_balance,reason,note) VALUES(?,?,?,?,?)",
                            (d["id"],prev,new,"Pago",note))
                st.success("Pago registrado.")
                st.rerun()
    with t3:
        hist=rows("SELECT created_at,previous_balance,new_balance,reason,note FROM debt_history WHERE debt_id=? ORDER BY id DESC",(d["id"],))
        if hist: st.dataframe(pd.DataFrame(hist),use_container_width=True,hide_index=True)
        else: st.info("Todavía no hay historial.")

elif page == "📅 Pagos":
    st.subheader("📅 Pagos de tarjetas y préstamos")
    pmap=debt_paid_map()
    for d in ds:
        paid=pmap.get(d["id"],0)
        minp=float(d["minimum_payment"] or 0)
        remaining=max(minp-paid,0)
        st.write(f"**{d['name']}** · vence día **{d['due_day']}** · mínimo **{money(minp)}** · pagado **{money(paid)}** · pendiente **{money(remaining)}**")

elif page == "💵 Ingresos":
    st.subheader("💵 Registrar ingresos en USD")
    with st.form("income_form"):
        source=st.selectbox("Fuente",["Cheque quincenal","Tips semanales","Ingreso extra","Otro"])
        amt=st.number_input("Monto USD",min_value=0.0,step=10.0)
        idate=st.date_input("Fecha",value=date.today())
        rate=st.number_input("Tipo de cambio MXN/USD",min_value=1.0,value=fx,step=.05)
        note=st.text_input("Nota")
        if st.form_submit_button("Guardar ingreso",use_container_width=True):
            execute("""INSERT INTO incomes(source,amount,currency,income_date,exchange_rate,amount_mxn,note)
                       VALUES(?,?,?,?,?,?,?)""",(source,amt,"USD",idate.isoformat(),rate,amt*rate,note))
            st.success("Ingreso guardado.")
    data=rows("SELECT * FROM incomes ORDER BY income_date DESC,id DESC")
    if data: st.dataframe(pd.DataFrame(data),use_container_width=True,hide_index=True)

elif page == "🧾 Gastos fijos":
    st.subheader("🧾 Vivienda, servicios y suscripciones")
    rs=recurring(); pmap=expense_paid_map(); t=date.today()
    for r in rs:
        c=st.columns([2,1,1,1])
        c[0].write(f"**{r['name']}**  \n{r['category']}")
        c[1].write(money(r["amount"],r["currency"]))
        c[2].write(f"Día {r['due_day']}" if r["due_day"] else r["frequency"])
        if pmap.get(r["id"],0)>0:
            c[3].success("Pagado")
        elif c[3].button("Marcar pagado",key=f"exp_{r['id']}"):
            execute("""INSERT INTO expense_payments(expense_id,amount,currency,payment_date,period_year,period_month,note)
                       VALUES(?,?,?,?,?,?,?)""",(r["id"],r["amount"],r["currency"],t.isoformat(),t.year,t.month,"Marcado desde la app"))
            st.rerun()

elif page == "🛒 Gastos diarios":
    st.subheader("🛒 Gastos diarios")
    with st.form("daily_form"):
        cat=st.selectbox("Categoría",["Comida","Gasolina","Supermercado","Ocio","Compras","Transporte","Salud","Otro"])
        desc=st.text_input("Descripción")
        cur=st.selectbox("Moneda",["USD","MXN"])
        amt=st.number_input("Monto",min_value=0.0,step=5.0)
        dte=st.date_input("Fecha",value=date.today())
        rate=st.number_input("Tipo de cambio",min_value=1.0,value=fx,step=.05,disabled=cur=="MXN")
        note=st.text_input("Nota")
        if st.form_submit_button("Guardar gasto",use_container_width=True):
            mxn=amt if cur=="MXN" else amt*rate
            execute("""INSERT INTO daily_expenses(category,description,amount,currency,expense_date,exchange_rate,amount_mxn,note)
                       VALUES(?,?,?,?,?,?,?,?)""",(cat,desc,amt,cur,dte.isoformat(),None if cur=="MXN" else rate,mxn,note))
            st.success("Gasto guardado.")
    data=rows("SELECT * FROM daily_expenses ORDER BY expense_date DESC,id DESC")
    if data: st.dataframe(pd.DataFrame(data),use_container_width=True,hide_index=True)

elif page == "💾 Respaldo":
    st.subheader("💾 Respaldo de la información")
    st.warning("Mientras esta versión use SQLite dentro de Streamlit, descarga respaldos con frecuencia. Streamlit Cloud puede reiniciar el contenedor y el archivo local no es una base permanente.")
    if DB_PATH.exists():
        st.download_button("⬇️ Descargar respaldo completo",data=DB_PATH.read_bytes(),file_name=f"mi_libertad_financiera_{date.today().isoformat()}.db",mime="application/octet-stream",use_container_width=True)
    up=st.file_uploader("Restaurar respaldo .db",type=["db"])
    if up is not None:
        if st.button("Restaurar este respaldo",type="primary",use_container_width=True):
            DB_PATH.write_bytes(up.getvalue())
            st.success("Respaldo restaurado.")
            st.rerun()

else:
    st.subheader("⚙️ Configuración")
    newfx=st.number_input("Tipo de cambio: MXN por 1 USD",min_value=1.0,value=fx,step=.05)
    newgoal=st.number_input("Deuda inicial de la meta",min_value=0.0,value=goal,step=100.0)
    if st.button("Guardar configuración",use_container_width=True):
        set_setting("mxn_per_usd",newfx); set_setting("debt_goal_start",newgoal)
        st.success("Configuración guardada.")
        st.rerun()
