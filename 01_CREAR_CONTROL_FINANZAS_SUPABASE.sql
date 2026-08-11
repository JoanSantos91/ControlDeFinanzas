-- CONTROL DE FINANZAS - SUPABASE / POSTGRESQL
-- PASO 1: CREAR TABLAS Y CARGAR DATOS INICIALES
BEGIN;

CREATE TABLE IF NOT EXISTS public.debts (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    institution TEXT NOT NULL,
    debt_type TEXT NOT NULL CHECK (debt_type IN ('credit_card','loan')),
    current_balance NUMERIC(14,2) NOT NULL DEFAULT 0,
    original_balance NUMERIC(14,2),
    credit_limit NUMERIC(14,2),
    available_credit NUMERIC(14,2),
    minimum_payment NUMERIC(14,2) NOT NULL DEFAULT 0,
    due_day INTEGER CHECK (due_day BETWEEN 1 AND 31),
    image_path TEXT,
    priority INTEGER NOT NULL DEFAULT 100,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.debt_history (
    id BIGSERIAL PRIMARY KEY,
    debt_id BIGINT NOT NULL REFERENCES public.debts(id) ON DELETE CASCADE,
    previous_balance NUMERIC(14,2),
    new_balance NUMERIC(14,2) NOT NULL,
    reason TEXT NOT NULL,
    note TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_debt_history_debt_id ON public.debt_history(debt_id);

CREATE TABLE IF NOT EXISTS public.debt_payments (
    id BIGSERIAL PRIMARY KEY,
    debt_id BIGINT NOT NULL REFERENCES public.debts(id) ON DELETE CASCADE,
    amount NUMERIC(14,2) NOT NULL CHECK (amount >= 0),
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    period_year INTEGER NOT NULL,
    period_month INTEGER NOT NULL CHECK (period_month BETWEEN 1 AND 12),
    note TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_debt_payments_debt_id ON public.debt_payments(debt_id);
CREATE INDEX IF NOT EXISTS idx_debt_payments_period ON public.debt_payments(period_year, period_month);

CREATE TABLE IF NOT EXISTS public.recurring_expenses (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'MXN' CHECK (currency IN ('MXN','USD')),
    amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    frequency TEXT NOT NULL DEFAULT 'monthly',
    due_day INTEGER CHECK (due_day BETWEEN 1 AND 31),
    variable_amount BOOLEAN NOT NULL DEFAULT FALSE,
    image_path TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT DEFAULT '',
    next_due_date DATE,
    coverage_start DATE,
    coverage_end DATE,
    policy_end DATE,
    subsequent_amount NUMERIC(14,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.expense_payments (
    id BIGSERIAL PRIMARY KEY,
    expense_id BIGINT NOT NULL REFERENCES public.recurring_expenses(id) ON DELETE CASCADE,
    amount NUMERIC(14,2) NOT NULL CHECK (amount >= 0),
    currency TEXT NOT NULL CHECK (currency IN ('MXN','USD')),
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    period_year INTEGER NOT NULL,
    period_month INTEGER NOT NULL CHECK (period_month BETWEEN 1 AND 12),
    note TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_expense_payments_expense_id ON public.expense_payments(expense_id);
CREATE INDEX IF NOT EXISTS idx_expense_payments_period ON public.expense_payments(period_year, period_month);

CREATE TABLE IF NOT EXISTS public.incomes (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    amount NUMERIC(14,2) NOT NULL CHECK (amount >= 0),
    currency TEXT NOT NULL DEFAULT 'USD' CHECK (currency IN ('MXN','USD')),
    income_date DATE NOT NULL DEFAULT CURRENT_DATE,
    exchange_rate NUMERIC(12,4),
    amount_mxn NUMERIC(14,2),
    note TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_incomes_date ON public.incomes(income_date);

CREATE TABLE IF NOT EXISTS public.daily_expenses (
    id BIGSERIAL PRIMARY KEY,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    amount NUMERIC(14,2) NOT NULL CHECK (amount >= 0),
    currency TEXT NOT NULL CHECK (currency IN ('MXN','USD')),
    expense_date DATE NOT NULL DEFAULT CURRENT_DATE,
    exchange_rate NUMERIC(12,4),
    amount_mxn NUMERIC(14,2),
    note TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_daily_expenses_date ON public.daily_expenses(expense_date);

CREATE TABLE IF NOT EXISTS public.settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT INTO public.settings(key,value)
VALUES ('mxn_per_usd','18.50'), ('debt_goal_start','92664.81')
ON CONFLICT (key) DO NOTHING;

INSERT INTO public.debts
(name,institution,debt_type,current_balance,original_balance,credit_limit,available_credit,minimum_payment,due_day,image_path,priority,notes)
SELECT * FROM (VALUES
('Banorte Oro','Banorte','credit_card',13429.21,13429.21,15000.00,1570.79,990.47,30,'assets/banorte_oro.png',30,'Saldo inicial'),
('BBVA Crédito','BBVA','credit_card',25366.20,25366.20,24200.00,-1166.20,1200.00,5,'assets/bbva_credito.jpg',10,'Límite excedido'),
('BanCoppel Crédito','BanCoppel','credit_card',9756.46,9756.46,11000.00,1243.54,794.40,16,'assets/bancoppel_credito.png',40,'Saldo inicial'),
('BanCoppel Crédito Personal','BanCoppel','loan',12023.15,12023.15,12000.00,-23.15,1435.00,7,'assets/bancoppel_credito.png',20,'Crédito personal'),
('Coppel Préstamo Personal','Coppel','loan',22000.00,22000.00,NULL,NULL,1500.00,5,'assets/bancoppel_credito.png',25,'Préstamo personal'),
('DiDi Préstamos','DiDi','loan',10089.79,10089.79,NULL,NULL,733.63,14,'assets/didi.png',35,'Saldo inicial')
) AS v(name,institution,debt_type,current_balance,original_balance,credit_limit,available_credit,minimum_payment,due_day,image_path,priority,notes)
WHERE NOT EXISTS (SELECT 1 FROM public.debts);

INSERT INTO public.recurring_expenses
(name,category,currency,amount,frequency,due_day,variable_amount,image_path,active,notes,next_due_date,coverage_start,coverage_end,policy_end,subsequent_amount)
SELECT * FROM (VALUES
('ChatGPT Plus','Suscripción','MXN',399.00,'monthly',1,FALSE,'assets/chatgpt.jpg',TRUE,'',NULL::DATE,NULL::DATE,NULL::DATE,NULL::DATE,NULL::NUMERIC),
('iCloud Drive','Suscripción','MXN',49.00,'monthly',2,FALSE,'assets/icloud.png',TRUE,'',NULL::DATE,NULL::DATE,NULL::DATE,NULL::DATE,NULL::NUMERIC),
('Amazon Prime','Suscripción','MXN',99.00,'monthly',17,FALSE,'assets/amazon_prime.png',TRUE,'',NULL::DATE,NULL::DATE,NULL::DATE,NULL::DATE,NULL::NUMERIC),
('Infonavit','Vivienda México','MXN',4000.00,'monthly',30,FALSE,'assets/infonavit.png',TRUE,'Deuda total Infonavit: $347,534.72 MXN',NULL::DATE,NULL::DATE,NULL::DATE,NULL::DATE,NULL::NUMERIC),
('Megacable','Servicios México','MXN',700.00,'monthly',5,FALSE,'assets/megacable.png',TRUE,'',NULL::DATE,NULL::DATE,NULL::DATE,NULL::DATE,NULL::NUMERIC),
('JAPAC','Servicios México','MXN',140.00,'monthly',24,FALSE,'assets/japac.jpg',TRUE,'',NULL::DATE,NULL::DATE,NULL::DATE,NULL::DATE,NULL::NUMERIC),
('CFE','Servicios México','MXN',87.00,'bimonthly',21,TRUE,'assets/cfe.jpg',TRUE,'Monto variable. Último recibo conocido: $87 MXN.',NULL::DATE,NULL::DATE,NULL::DATE,NULL::DATE,NULL::NUMERIC),
('Telcel','Telefonía','MXN',699.00,'monthly',18,FALSE,'assets/telcel.png',TRUE,'',NULL::DATE,NULL::DATE,NULL::DATE,NULL::DATE,NULL::NUMERIC),
('Renta actual','Vivienda USA','USD',560.00,'monthly',1,FALSE,NULL,TRUE,'',NULL::DATE,NULL::DATE,NULL::DATE,NULL::DATE,NULL::NUMERIC),
('Latino Seguros - Auto','Seguro de auto','MXN',3486.00,'quarterly',29,FALSE,'assets/latino_seguros.png',TRUE,
 'Primer pago: $3,486 MXN. Pagos subsecuentes: $2,673.95 MXN. Póliza con vigencia de un año.',
 DATE '2026-10-29',DATE '2026-07-29',DATE '2026-10-29',DATE '2027-07-29',2673.95)
) AS v(name,category,currency,amount,frequency,due_day,variable_amount,image_path,active,notes,next_due_date,coverage_start,coverage_end,policy_end,subsequent_amount)
WHERE NOT EXISTS (SELECT 1 FROM public.recurring_expenses);

INSERT INTO public.expense_payments(expense_id,amount,currency,payment_date,period_year,period_month,note)
SELECT r.id,3486.00,'MXN',DATE '2026-07-29',2026,7,
       'Primer pago de póliza. Cobertura del 29/07/2026 al 29/10/2026.'
FROM public.recurring_expenses r
WHERE r.name='Latino Seguros - Auto'
  AND NOT EXISTS (
      SELECT 1 FROM public.expense_payments ep
      WHERE ep.expense_id=r.id
        AND ep.payment_date=DATE '2026-07-29'
        AND ep.amount=3486.00
  );

INSERT INTO public.expense_payments(expense_id,amount,currency,payment_date,period_year,period_month,note)
SELECT r.id,87.00,'MXN',DATE '2026-08-11',2026,8,'Último recibo conocido marcado como pagado.'
FROM public.recurring_expenses r
WHERE r.name='CFE'
  AND NOT EXISTS (
      SELECT 1 FROM public.expense_payments ep
      WHERE ep.expense_id=r.id
        AND ep.period_year=2026
        AND ep.period_month=8
  );

COMMIT;

SELECT 'debts' AS tabla, COUNT(*) AS registros FROM public.debts
UNION ALL SELECT 'debt_history', COUNT(*) FROM public.debt_history
UNION ALL SELECT 'debt_payments', COUNT(*) FROM public.debt_payments
UNION ALL SELECT 'recurring_expenses', COUNT(*) FROM public.recurring_expenses
UNION ALL SELECT 'expense_payments', COUNT(*) FROM public.expense_payments
UNION ALL SELECT 'incomes', COUNT(*) FROM public.incomes
UNION ALL SELECT 'daily_expenses', COUNT(*) FROM public.daily_expenses
UNION ALL SELECT 'settings', COUNT(*) FROM public.settings;
