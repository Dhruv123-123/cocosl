"""Words for Money Dashboard Pro, English and Spanish. Category names match apps/budget/lib/dashboard.js exactly, so the
free tool's Transactions tab pastes straight in. Example data is fictional."""
from __future__ import annotations

from datetime import date

# key, English, Spanish, type, example monthly budget
CATS = [
    ("housing", "Rent & housing", "Renta y vivienda", "spend", 1450),
    ("groceries", "Groceries", "Supermercado", "spend", 450),
    ("dining", "Eating out & delivery", "Comer fuera y a domicilio", "spend", 120),
    ("transport", "Gas & transport", "Gasolina y transporte", "spend", 180),
    ("utilities", "Utilities & phone", "Servicios y teléfono", "spend", 260),
    ("insurance", "Insurance", "Seguros", "spend", 130),
    ("health", "Health & pharmacy", "Salud y farmacia", "spend", 60),
    ("subscriptions", "Subscriptions & streaming", "Suscripciones y streaming", "spend", 40),
    ("shopping", "Shopping", "Compras", "spend", 100),
    ("fun", "Fun & going out", "Diversión y salidas", "spend", 80),
    ("debt", "Loans & debt", "Préstamos y deudas", "spend", 0),
    ("kids", "Kids & school", "Niños y escuela", "spend", 0),
    ("giving", "Gifts & giving", "Regalos y donaciones", "spend", 0),
    ("fees", "Bank fees & interest", "Comisiones e intereses", "spend", 0),
    ("cash", "Cash (ATM)", "Efectivo (cajero)", "spend", 0),
    ("other", "Other", "Otros", "spend", 50),
    ("savings", "Savings & investing", "Ahorro e inversión", "save", 300),
    ("income", "Income", "Ingresos", "income", 5300),
    ("transfers", "Transfers & card payments", "Transferencias y pagos de tarjeta", "move", 0),
]


def _examples(lang: str):
    name = {k: (en if lang == "en" else es) for k, en, es, _, _ in CATS}
    rows = []
    for m, (y, mo) in enumerate([(2026, 9), (2026, 10), (2026, 11)]):
        d = lambda day: date(y, mo, day)  # noqa: E731
        rows += [
            (d(1), "PAYROLL DIRECT DEP ACME CO", "income", 2650), (d(15), "PAYROLL DIRECT DEP ACME CO", "income", 2650),
            (d(2), "PARKVIEW APTS RENT PMT", "housing", -1450), (d(3), "NETFLIX.COM", "subscriptions", -17.99),
            (d(9), "SPOTIFY USA", "subscriptions", -11.99), (d(6), "VERIZON WIRELESS", "utilities", -85),
            (d(12), "DUKE ENERGY", "utilities", -(96 + m * 14)), (d(20), "GEICO AUTO", "insurance", -128),
            (d(4), "KROGER #555", "groceries", -(96.4 + m * 9)), (d(11), "KROGER #555", "groceries", -(88.15 + m * 4)),
            (d(18), "ALDI 77", "groceries", -(71.3 + m * 6)), (d(25), "KROGER #555", "groceries", -(104.9 + m * 12)),
            (d(7), "SHELL OIL 57442", "transport", -(41 + m * 3)), (d(21), "SHELL OIL 57442", "transport", -(39.5 + m * 2)),
            (d(5), "CHIPOTLE 1234", "dining", -14.2), (d(16), "DOORDASH*TACOS", "dining", -(28.5 + m * 9)),
            (d(23), "STARBUCKS #882", "dining", -(6.75 + m)), (d(8), "AMAZON MKTPL", "shopping", -(34 + m * 41)),
            (d(17), "CVS/PHARMACY #0441", "health", -18.4), (d(16), "ONLINE TRANSFER TO SAVINGS", "savings", -300),
            (d(26), "CHASE CREDIT CRD AUTOPAY", "transfers", -420), (d(19), "AMC THEATRES", "fun", -(32 + m * 8)),
        ]
    rows.append((date(2026, 10, 14), "MAPLE STREET VET CLINIC", "other", -140))
    rows.sort(key=lambda r: r[0])
    return [(dt, desc, name[c], round(a, 2)) for dt, desc, c, a in rows]


FUNDS = {
    "en": [("Car insurance (6-month)", 780, date(2027, 3, 1)), ("Holiday gifts", 600, date(2026, 12, 15)),
           ("Car repairs and tires", 1200, date(2027, 9, 1)), ("Summer trip", 1500, date(2027, 7, 1)),
           ("Annual subscriptions", 240, date(2027, 2, 1)), ("Back to school", 350, date(2027, 8, 1))],
    "es": [("Seguro del carro (6 meses)", 780, date(2027, 3, 1)), ("Regalos de fin de año", 600, date(2026, 12, 15)),
           ("Reparaciones y llantas", 1200, date(2027, 9, 1)), ("Viaje de verano", 1500, date(2027, 7, 1)),
           ("Suscripciones anuales", 240, date(2027, 2, 1)), ("Regreso a clases", 350, date(2027, 8, 1))],
}


def _contrib(lang):
    f = [x[0] for x in FUNDS[lang]]
    out = []
    for mo in (9, 10, 11):
        out += [(date(2026, mo, 2), f[0], 130), (date(2026, mo, 2), f[1], 150), (date(2026, mo, 16), f[2], 60), (date(2026, mo, 16), f[3], 100)]
    out += [(date(2026, 10, 16), f[4], 40), (date(2026, 11, 16), f[4], 40)]
    return sorted(out, key=lambda r: r[0])


TEXT = {
    "en": {
        "product": "Money Dashboard Pro",
        "file": "Money-Dashboard-Pro.xlsx",
        "tabs": {"start": "Start", "dash": "Dashboard", "tx": "Transactions", "bva": "Budget vs Actual", "trend": "Trends",
                 "funds": "Sinking Funds", "cats": "Categories"},
        "types": {"spend": "Spending", "save": "Saving", "income": "Income", "move": "Transfer"},
        "categories": [(en, t, b) for _, en, _, t, b in CATS],
        "example_tx": _examples("en"), "example_funds": FUNDS["en"], "example_contrib": _contrib("en"),
        "example_settings": (date(2026, 9, 1), date(2026, 11, 1)),
        "cats_title": "Categories and monthly budgets",
        "cats_sub": "Rename, add or remove categories here (yellow cells). Every tab follows this list.",
        "cats_head": ["Category", "Type", "Monthly budget"],
        "cats_note": "Type decides where a category counts. Spending: in your spending total and budget checks. Saving: money you put away "
                     "(counted separately). Income: money in. Transfer: moves between your own accounts and credit card payments, "
                     "listed but never counted, so card spending isn't counted twice. Add your own categories in the empty rows below; "
                     "they appear on Trends and Budget vs Actual straight away.",
        "tx_title": "Transactions",
        "tx_sub": "Money in is positive, money out is negative. Paste from the free Money Dashboard maker's Transactions tab, or type them in.",
        "tx_head": ["Date", "Month", "Description", "Category", "Amount"],
        "trend_title": "12-month trends",
        "trend_sub": "Every category, month by month, from the first month on the Dashboard. Spending shows as a positive number.",
        "category": "Category", "avg": "Average so far", "total": "12-month total", "helper": "Helper",
        "money_in": "Money in", "spending": "Spending", "saved": "Saved & invested", "left": "Left over",
        "rate": "Share of money in kept", "total_label": "Total", "latest_helper": "(helper: latest month with transactions)",
        "chart_trend": "Money in, spending and left over", "chart_bva": "Budget vs actual", "chart_funds": "Sinking funds: target and saved",
        "chart_where": "Where this month's money went",
        "bva_title": "Budget vs actual",
        "bva_sub": "For the month picked on the Dashboard. Red means over budget. Set budgets on the Categories tab.",
        "month_label": "Month",
        "bva_head": ["Category", "Budget", "Actual", "Left (or over)", "Monthly average", "Used", "", "Type"],
        "bva_total": "Spending total", "bva_over": "Categories over budget",
        "funds_title": "Sinking funds",
        "funds_sub": "Save a little each month for bills you know are coming. Add funds in yellow, log each deposit on the right.",
        "funds_head": ["Fund", "Target", "Needed by", "Saved so far", "Still to save", "Months left", "Save each month", "Done", "Progress"],
        "contrib_head": ["Date", "Fund", "Amount"],
        "funds_note": "Moved money to a fund? Log it on the right (date, fund, amount). Taking money out for the bill? Log it as a negative amount.",
        "total": "Total",
        "dash_title": "Money Dashboard",
        "dash_sub": "Pick your first month and the month to look at (yellow). Everything else fills itself in.",
        "first_month": "First month of your 12", "review_month": "Month to look at",
        "months_so_far": "Months counted so far", "column_helper": "(helper: column of that month)",
        "this_month": "That month", "average": "Monthly average so far",
        "biggest": "Biggest spending category", "over_count": "Categories over budget",
        "funds_saved": "Saved in sinking funds", "funds_monthly": "Sinking funds: save each month",
        "start_sub": "Your bank download, turned into a monthly money dashboard. Made for Google Sheets; works in Excel and Numbers.",
        "start": [
            ("h", "Set it up in 5 minutes"),
            ("p", "1. Categories tab: rename or add categories and type a monthly budget for each (yellow cells). The list already matches the free Money Dashboard maker."),
            ("p", "2. Transactions tab: delete the example rows (Sep to Nov 2026), then paste your own. Easiest way: make a free dashboard at moneymadesimple.netlify.app/budget/money-dashboard.html, open its Transactions tab, copy columns A to E and paste them into cell A5 here. Or download your bank's CSV and paste Date, Description, Category and Amount (money out as a negative number)."),
            ("p", "3. Dashboard tab: set the first month of your 12 and the month you want to look at. Trends, Budget vs Actual and the charts follow."),
            ("p", "4. Sinking Funds tab: list the bills you know are coming (car insurance, holidays, repairs), with a target and a date. It works out what to put away each month. Log each deposit on the right."),
            ("h", "Every month (10 minutes)"),
            ("p", "Paste the new month's transactions under the old ones, fix any categories from the dropdown, then move 'Month to look at' on the Dashboard forward. Look at three things: left over, anything red on Budget vs Actual, and whether the sinking funds are on track."),
            ("h", "Good to know"),
            ("p", "Transfers between your own accounts and credit card payments are listed but not counted, so you don't count card spending twice. Give them the Transfers & card payments category."),
            ("p", "Refunds: leave them positive in the same category as the purchase. They lower that category's spending."),
            ("p", "After 12 months, start a fresh copy, or change the first month on the Dashboard: older months stay in Transactions but drop off the trend."),
            ("p", "Charts update by themselves. In Google Sheets, click a chart and use the three-dot menu to edit colours or switch it off."),
        ],
        "legal": "Educational organising tool, not financial advice. Example data is fictional. For personal use by the buyer; please don't resell or share the template.",
    },
    "es": {
        "product": "Tablero de dinero Pro",
        "file": "Tablero-de-Dinero-Pro.xlsx",
        "tabs": {"start": "Inicio", "dash": "Tablero", "tx": "Movimientos", "bva": "Presupuesto vs real", "trend": "Tendencias",
                 "funds": "Fondos de ahorro", "cats": "Categorías"},
        "types": {"spend": "Gasto", "save": "Ahorro", "income": "Ingreso", "move": "Transferencia"},
        "categories": [(es, t, b) for _, _, es, t, b in CATS],
        "example_tx": _examples("es"), "example_funds": FUNDS["es"], "example_contrib": _contrib("es"),
        "example_settings": (date(2026, 9, 1), date(2026, 11, 1)),
        "cats_title": "Categorías y presupuesto mensual",
        "cats_sub": "Cambia, agrega o quita categorías aquí (celdas amarillas). Todas las pestañas siguen esta lista.",
        "cats_head": ["Categoría", "Tipo", "Presupuesto mensual"],
        "cats_note": "El tipo decide dónde cuenta cada categoría. Gasto: entra en tu total de gastos y en el presupuesto. Ahorro: dinero que "
                     "guardas (se cuenta aparte). Ingreso: dinero que entra. Transferencia: movimientos entre tus propias cuentas y pagos "
                     "de tarjeta; aparecen pero no se cuentan, para no contar dos veces lo que gastaste con tarjeta. Agrega tus propias "
                     "categorías en las filas vacías; aparecen enseguida en Tendencias y en Presupuesto vs real.",
        "tx_title": "Movimientos",
        "tx_sub": "Lo que entra es positivo, lo que sale es negativo. Pega la pestaña Movimientos del Tablero de dinero gratis, o escríbelos.",
        "tx_head": ["Fecha", "Mes", "Descripción", "Categoría", "Monto"],
        "trend_title": "Tendencias de 12 meses",
        "trend_sub": "Cada categoría, mes por mes, desde el primer mes que pusiste en el Tablero. Los gastos aparecen como números positivos.",
        "category": "Categoría", "avg": "Promedio hasta ahora", "total": "Total 12 meses", "helper": "Auxiliar",
        "money_in": "Dinero que entra", "spending": "Gastos", "saved": "Ahorrado e invertido", "left": "Te sobra",
        "rate": "Parte de lo que entra que guardas", "total_label": "Total", "latest_helper": "(auxiliar: último mes con movimientos)",
        "chart_trend": "Lo que entra, lo que gastas y lo que sobra", "chart_bva": "Presupuesto vs real", "chart_funds": "Fondos: meta y ahorrado",
        "chart_where": "A dónde se fue el dinero este mes",
        "bva_title": "Presupuesto vs real",
        "bva_sub": "Para el mes que elegiste en el Tablero. Rojo quiere decir que te pasaste. Pon el presupuesto en la pestaña Categorías.",
        "month_label": "Mes",
        "bva_head": ["Categoría", "Presupuesto", "Real", "Queda (o te pasaste)", "Promedio mensual", "Usado", "", "Tipo"],
        "bva_total": "Total de gastos", "bva_over": "Categorías pasadas del presupuesto",
        "funds_title": "Fondos de ahorro",
        "funds_sub": "Guarda un poco cada mes para los gastos que sabes que vienen. Agrega fondos en amarillo y anota cada depósito a la derecha.",
        "funds_head": ["Fondo", "Meta", "Para cuándo", "Ahorrado", "Falta", "Meses que quedan", "Guardar al mes", "Listo", "Avance"],
        "contrib_head": ["Fecha", "Fondo", "Monto"],
        "funds_note": "¿Pasaste dinero a un fondo? Anótalo a la derecha (fecha, fondo, monto). ¿Lo sacaste para pagar? Anótalo en negativo.",
        "total": "Total",
        "dash_title": "Tablero de dinero",
        "dash_sub": "Elige tu primer mes y el mes que quieres ver (amarillo). Todo lo demás se llena solo.",
        "first_month": "Primer mes de tus 12", "review_month": "Mes que quieres ver",
        "months_so_far": "Meses contados hasta ahora", "column_helper": "(auxiliar: columna de ese mes)",
        "this_month": "Ese mes", "average": "Promedio mensual hasta ahora",
        "biggest": "Categoría con más gasto", "over_count": "Categorías pasadas del presupuesto",
        "funds_saved": "Ahorrado en fondos", "funds_monthly": "Fondos: guardar al mes",
        "start_sub": "Lo que descargas de tu banco, convertido en un tablero mensual. Hecho para Google Sheets; funciona en Excel y Numbers.",
        "start": [
            ("h", "Listo en 5 minutos"),
            ("p", "1. Pestaña Categorías: cambia o agrega categorías y escribe un presupuesto mensual para cada una (celdas amarillas). La lista ya coincide con el Tablero de dinero gratis."),
            ("p", "2. Pestaña Movimientos: borra las filas de ejemplo (sep a nov 2026) y pega las tuyas. Lo más fácil: haz un tablero gratis en moneymadesimple.netlify.app/budget/tablero-dinero.html, abre su pestaña Movimientos, copia las columnas A a E y pégalas en la celda A5 de aquí. O descarga el CSV de tu banco y pega Fecha, Descripción, Categoría y Monto (lo que sale, en negativo)."),
            ("p", "3. Pestaña Tablero: elige el primer mes de tus 12 y el mes que quieres ver. Tendencias, Presupuesto vs real y las gráficas se ajustan solas."),
            ("p", "4. Pestaña Fondos de ahorro: anota los gastos que sabes que vienen (seguro del carro, fin de año, reparaciones), con una meta y una fecha. Te dice cuánto guardar cada mes. Anota cada depósito a la derecha."),
            ("h", "Cada mes (10 minutos)"),
            ("p", "Pega los movimientos del mes nuevo debajo de los anteriores, corrige categorías con la lista y cambia «Mes que quieres ver» en el Tablero. Revisa tres cosas: cuánto te sobra, lo que salga en rojo en Presupuesto vs real y si los fondos van bien."),
            ("h", "Bueno saber"),
            ("p", "Las transferencias entre tus cuentas y los pagos de tarjeta aparecen pero no se cuentan, para no contar dos veces lo que gastaste con tarjeta. Ponles la categoría Transferencias y pagos de tarjeta."),
            ("p", "Reembolsos: déjalos en positivo y en la misma categoría de la compra. Bajan el gasto de esa categoría."),
            ("p", "Después de 12 meses, empieza una copia nueva o cambia el primer mes en el Tablero: los meses viejos se quedan en Movimientos pero salen de la tendencia."),
            ("p", "Las gráficas se actualizan solas. En Google Sheets, haz clic en una gráfica y usa el menú de tres puntos para cambiar colores o quitarla."),
        ],
        "legal": "Herramienta educativa para organizarte, no es asesoría financiera. Los datos de ejemplo son ficticios. Para uso personal de quien la compra; por favor no la revendas ni la compartas.",
    },
}
