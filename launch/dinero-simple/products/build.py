"""Build the Spanish (Dinero Simple) versions of two Money Made Simple products.

    python launch/dinero-simple/products/build.py            # PDFs, workbooks, covers, zips -> dist/
    python launch/dinero-simple/products/build.py --check    # also recalc workbooks in LibreOffice

* El Kit para Recortar Gastos ($5)   <- The Bill Cut Kit
* Tu Fecha Sin Deudas ($17)          <- The Debt-Free Date Planner
* Empieza a Invertir con $100 al Mes ($19) <- Start Investing With $100 a Month
* El Paquete Dinero Simple ($29)     <- the four Spanish kits together (no Spanish credit audit kit yet)

The English originals live in launch/products/ on branch claude/project-thread-uqg0ro. The guides
are rewritten in Spanish (recorte-de-gastos/guide.html, fecha-sin-deudas/guide.html); the workbooks
are built by the English builders (vendored as sheets_en.py, recoloured) and translated in memory
just before saving, so charts, dropdowns and conditional formats survive. Any English label left
untranslated stops the build. Everything still needs a native-speaker read before it is sold.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import openpyxl  # noqa: E402

import sheets_en  # noqa: E402

PRODUCTS = [
    {"slug": "recorte-de-gastos", "name": "El Kit para Recortar Gastos", "price": 5,
     "pdf": "El-Kit-para-Recortar-Gastos.pdf", "xlsx": "Recorte-de-Gastos-Control.xlsx",
     "builder": "build_bill_cut", "zip": "El-Kit-para-Recortar-Gastos.zip", "tag": "Lista + guiones + hoja"},
    {"slug": "fecha-sin-deudas", "name": "Tu Fecha Sin Deudas", "price": 17,
     "pdf": "Tu-Fecha-Sin-Deudas.pdf", "xlsx": "Tu-Fecha-Sin-Deudas.xlsx",
     "builder": "build_debt_planner", "zip": "Tu-Fecha-Sin-Deudas.zip", "tag": "Guía + hoja de cálculo"},
    {"slug": "invertir-con-100", "name": "Empieza a Invertir con $100 al Mes", "price": 19,
     "pdf": "Empieza-a-Invertir-con-100-al-Mes.pdf", "xlsx": "Invertir-Calculadoras.xlsx",
     "builder": "build_investing", "zip": "Empieza-a-Invertir-con-100-al-Mes.zip", "tag": "Guía + calculadoras"},
    {"slug": "paquete", "name": "El Paquete Dinero Simple", "price": 29,
     "pdf": "Empieza-Aqui-Mapa-del-Paquete.pdf", "zip": "El-Paquete-Dinero-Simple.zip", "tag": "Los 4 kits",
     "bundle": ["recorte-de-gastos", "presupuesto-20-minutos", "fecha-sin-deudas", "invertir-con-100"]},
]

# Already built elsewhere (launch/dinero-simple/product/): goes into the bundle as-is.
EXISTING = {"presupuesto-20-minutos": {"name": "El Presupuesto de 20 Minutos", "dir": HERE.parent / "product",
                                       "files": ["El-Presupuesto-de-20-Minutos.pdf",
                                                 "Presupuesto-20-Minutos-Plantilla.xlsx"]}}

SHEETS = {
    "Summary": "Resumen", "Audit": "Revisión", "Negotiation Log": "Registro de llamadas",
    "Plan": "Plan", "Balance Transfer": "Transferencia", "Consolidation": "Consolidación",
    "Progress": "Avance", "Schedule": "Calendario",
    "Order Checklist": "Orden", "Growth": "Crecimiento", "Fee Drag": "Comisiones", "401k Match": "Match 401k",
    "Roth vs Traditional": "Roth o Traditional", "Contributions": "Aportaciones",
}

# Values that formulas and dropdowns compare against: translated everywhere at once.
VALUES = {
    "Weekly": "Cada semana", "Every 2 weeks": "Cada dos semanas", "Monthly": "Cada mes",
    "Quarterly": "Cada 3 meses", "Twice a year": "Dos veces al año", "Yearly": "Cada año",
    "Keep": "Me quedo", "Cut": "Cancelar", "Downgrade": "Bajar de plan", "Negotiate": "Negociar",
    "Emergency fund": "Fondo de emergencia", "Extra debt payment": "Pago extra a deudas",
    "Investing": "Invertir", "Sinking fund": "Fondo de previsión",
    "Avalanche": "Avalancha", "Snowball": "Bola de nieve", "Custom": "Mi orden",
    **{f"Debt {i}": f"Deuda {i}" for i in range(1, 11)},
    # investing kit: account types and step status (dropdowns + formulas)
    "401(k) / 403(b)": "401(k) / 403(b)", "Roth IRA": "Roth IRA", "Traditional IRA": "Traditional IRA", "HSA": "HSA",
    "Taxable brokerage": "Cuenta normal", "Not started": "Sin empezar", "In progress": "En proceso",
    "Done": "Listo", "Not applicable": "No aplica", "Roth": "Roth", "Traditional": "Traditional",
}

FORMULA_TEXT = {
    "30+ years": "Más de 30 años", "Never": "Nunca", "Increase payments": "Sube tus pagos",
    "Cheaper than your current plan.": "Más barato que tu plan actual.",
    "Not worth it at this payment.": "No conviene con este pago.",
    "Worth it, IF you stop adding new spending to either card.":
        "Conviene, SI dejas de hacer compras nuevas con las dos tarjetas.",
    "Your current plan is cheaper. Keep going.": "Tu plan actual sale más barato. Síguele.",
    " of ": " de ", "IRA total within the limit": "Total de IRA dentro del límite", "No limit": "Sin límite",
    "Over the combined IRA limit!": "¡Te pasaste del límite combinado de IRA!",
    "Raise your contribution: this is part of your pay.": "Sube tu aportación: esto es parte de tu sueldo.",
    "Same": "Igual", "You get the full match.": "Recibes el match completo.",
}

FOOT_ES = ("Herramienta educativa, no es asesoría financiera, de impuestos, legal ni de inversión. El ejemplo es "
           "inventado. Para uso personal del comprador; por favor no la revendas ni la compartas. (c) Dinero Simple")
INTRO_ES = "Celdas amarillas = tus datos. Las blancas se calculan solas. Viene con un ejemplo; escribe encima."

LABELS = {
    sheets_en.FOOT: FOOT_ES,
    "Yellow cells = your inputs. White cells calculate automatically. Example data shown; type over it.": INTRO_ES,
    # ---- Kit para Recortar Gastos
    "'Remind me on' is two weeks before the deal ends: call again then.":
        "'Recordarme el' es dos semanas antes de que termine la promoción: vuelve a llamar ese día.",
    "12-month loyalty rate": "Precio de lealtad por 12 meses",
    "Adds up the Audit tab. Give this money a job (guide, page 9).":
        "Suma la pestaña Revisión. Dale un trabajo a este dinero (guía, página 9).",
    "Amount": "Cantidad", "Automatic transfer per month": "Transferencia automática al mes",
    "Car insurance": "Seguro del carro", "Charge": "Cobro", "Chat agent": "Agente del chat",
    "Cloud storage 2 TB": "Nube, 2 TB", "Company": "Empresa", "Cuts": "Cancelaciones", "Date": "Fecha",
    "Deal ends": "Termina la promo", "Decision": "Decisión", "Device protection": "Seguro del celular",
    "Downgrades": "Bajas de plan",
    "Every call: what you paid, what you pay now, and when the deal ends.":
        "Cada llamada: lo que pagabas, lo que pagas ahora y cuándo termina la promoción.",
    "Every recurring charge, converted to a yearly cost, with one decision each.":
        "Cada cobro que se repite, convertido a costo anual, con una decisión para cada uno.",
    "Food delivery membership": "Membresía de comida a domicilio", "Gym": "Gimnasio",
    "How often": "Cada cuándo", "Internet": "Internet", "Internet provider": "Compañía de internet",
    "Language app": "App de idiomas", "Moved to 15 GB plan, no contract": "Pasé al plan de 15 GB, sin contrato",
    "Music app": "App de música", "Negotiation Log": "Registro de llamadas", "Negotiations": "Negociaciones",
    "New / month": "Nuevo / mes", "New amount (if D/N)": "Cantidad nueva (si B/N)", "New yearly": "Nuevo al año",
    "Next audit (6 months from today)": "Próxima revisión (en 6 meses)",
    "Not opened since summer": "No la abro desde el verano", "Notes": "Notas", "Off-peak plan": "Plan de horas tranquilas",
    "Old / month": "Antes / mes", "Ordered twice since June": "Pedí dos veces desde junio",
    "Phone carrier": "Compañía de celular", "Phone is paid off": "El celular ya está pagado",
    "Phone plan": "Plan de celular", "Quote shopping in Jan": "Cotizar otras en enero",
    "Recurring charges found": "Cobros encontrados", "Remind me on": "Recordarme el",
    "Renewal / cancel date": "Fecha de renovación / cancelación", "Renews Feb; cancel before": "Se renueva en feb.; cancelar antes",
    "Sam (retention)": "Sam (retención)", "Saved per month": "Ahorro al mes", "Saved per week": "Ahorro a la semana",
    "Saved per year": "Ahorro al año", "Saves / yr": "Ahorra / año", "See Negotiation Log": "Ver Registro de llamadas",
    "Spoke to": "Hablé con", "Subscription & Bill Audit": "Revisión de suscripciones y cuentas", "Total": "Total",
    "Used weekly": "La uso cada semana", "Using 120 GB": "Uso 120 GB", "Video streaming #1": "Streaming de video #1",
    "Video streaming #2": "Streaming de video #2", "What they offered": "Qué me ofrecieron",
    "Where it goes (pick one and automate it this week)": "A dónde va (elige uno y ponlo en automático esta semana)",
    "Yearly cost": "Costo al año", "Yearly cost after": "Costo al año después", "Yearly cost before": "Costo al año antes",
    "Your savings": "Tu ahorro",
    # ---- Tu Fecha Sin Deudas
    "% paid off": "% pagado",
    "A loan only helps if the cards stay paid off. Watch for prepayment penalties, and compare the APR (which includes fees) across a few lenders. Pre-qualification usually uses a soft inquiry.":
        "Un préstamo solo ayuda si las tarjetas se quedan en cero. Revisa si cobra por pagar antes y compara la APR (que incluye comisiones) en varios prestamistas. La precalificación casi siempre usa una consulta suave.",
    "APR %": "APR %", "APR after the promo ends %": "APR al terminar la promo %", "Actual balance": "Saldo real",
    "Ahead by": "Adelantado por", "Amount of debt to consolidate": "Deuda a consolidar",
    "Avalanche = highest APR first (least interest). Snowball = smallest balance first. Custom = your order (column F).":
        "Avalancha = APR más alta primero (menos interés). Bola de nieve = saldo más chico primero. Mi orden = tu orden (columna F).",
    "Balance": "Saldo", "Balance to move": "Saldo a transferir", "Budget / mo": "Presupuesto / mes",
    "Car loan": "Préstamo del carro",
    "Check before you apply: the exact fee, how long the promo lasts, whether the promo needs a minimum payment every month, and the rate on new purchases. Applying is a hard credit inquiry.":
        "Revisa antes de solicitar: la comisión exacta, cuánto dura la promo, si pide un pago mínimo cada mes y la tasa para compras nuevas. Solicitar genera una consulta dura de crédito.",
    "Compares one fixed-rate loan with your current plan (from the Plan tab).":
        "Compara un préstamo de tasa fija con tu plan actual (de la pestaña Plan).",
    "Compares paying a card as it is vs moving it to a promo-rate card with a transfer fee.":
        "Compara pagar la tarjeta como está contra pasarla a una con tasa promocional y comisión.",
    "Credit card": "Tarjeta de crédito", "Current APR %": "APR actual %",
    "Current plan: monthly payment": "Plan actual: pago mensual", "Current plan: months to debt-free": "Plan actual: meses para terminar",
    "Current plan: total interest": "Plan actual: interés total", "Custom order": "Mi orden", "Debt": "Deuda",
    "Debt-free date": "Fecha sin deudas",
    "Each month: interest is added, every debt gets its minimum, then the rest of your monthly debt budget goes to debts in the order shown in row 4.":
        "Cada mes: se suma el interés, cada deuda recibe su mínimo y el resto de tu presupuesto para deudas va en el orden de la fila 4.",
    "Extra paid": "Extra pagado", "Extra per month": "Extra al mes", "First payment month": "Mes del primer pago",
    "Interest you save with this plan": "Interés que te ahorras con este plan", "Interest you'll pay": "Interés que vas a pagar",
    "Is a balance transfer worth it?": "¿Conviene transferir el saldo?", "Left after minimums": "Sobra después de mínimos",
    "Linked to your Plan total. Type a number to override.": "Viene del total de tu Plan. Escribe un número para cambiarlo.",
    "List your debts, pick a method, set your extra payment. Everything else is worked out for you.":
        "Anota tus deudas, elige un método y pon tu pago extra. Lo demás se calcula solo.",
    "Loan APR %": "APR del préstamo %", "Loan saves you (interest)": "El préstamo te ahorra (interés)",
    "Loan size so the fee is covered": "Préstamo para cubrir la comisión", "Loan term (months)": "Plazo del préstamo (meses)",
    "Loan: months to debt-free": "Préstamo: meses para terminar", "Loan: total interest + fee": "Préstamo: interés total + comisión",
    "Method": "Método", "Min paid": "Mín. pagado", "Minimum": "Mínimo", "Minimum / mo": "Mínimo / mes",
    "Minimums only: interest": "Solo mínimos: interés", "Minimums only: months": "Solo mínimos: meses",
    "Minimums only: months until debt-free": "Solo mínimos: meses para terminar",
    "Minimums only: total interest": "Solo mínimos: interés total", "Month": "Mes", "Monthly loan payment": "Pago mensual del préstamo",
    "Monthly payment to clear it inside the promo": "Pago mensual para liquidarla dentro de la promo",
    "Monthly rate": "Tasa mensual", "Months sooner": "Meses antes", "Months until debt-free": "Meses para terminar",
    "On top of all the minimums. When a debt is paid off, its minimum rolls into the next one automatically.":
        "Además de todos los mínimos. Cuando una deuda se paga, su mínimo pasa solo a la siguiente.",
    "Once a month, type your actual total balance. See if you're ahead of the plan.":
        "Una vez al mes, escribe tu saldo total real. Ve si vas adelantado.",
    "Order": "Orden", "Order used": "Orden usado", "Origination fee %": "Comisión de apertura %", "Owed": "Debe",
    "Paid off": "Pagada", "Paid off in month #": "Pagada en el mes #",
    "Payoff schedule (calculated; no inputs here)": "Calendario de pagos (calculado; aquí no se escribe)",
    "Personal loan": "Préstamo personal", "Plan says": "Según el plan", "Progress tracker": "Tu avance",
    "Promo APR %": "APR promocional %", "Promo length (months)": "Duración de la promo (meses)",
    "Red minimum = the minimum doesn't cover the monthly interest, so that balance never shrinks on minimums alone. Interest is estimated monthly (APR / 12); your lender's daily calculation will differ slightly. Change the method or the extra payment and watch the date move.":
        "Mínimo en rojo = no cubre el interés del mes, así que ese saldo nunca baja con puros mínimos. El interés se estima por mes (APR / 12); el cálculo diario de tu banco va a variar un poco. Cambia el método o el pago extra y mira cómo se mueve la fecha.",
    "Stay put: interest": "Quedarte: interés", "Stay put: months to pay off": "Quedarte: meses para pagar",
    "Store card": "Tarjeta de tienda", "Student loan": "Préstamo de estudiante", "Total balance": "Saldo total",
    "Total interest on this plan": "Interés total con este plan", "Total paid toward debt each month": "Total a deudas cada mes",
    "Transfer fee %": "Comisión de transferencia %", "Transfer: balance left when the promo ends": "Transferencia: saldo al terminar la promo",
    "Transfer: fee": "Transferencia: comisión", "Transfer: months to pay off": "Transferencia: meses para pagar",
    "Transfer: total cost (fee + interest)": "Transferencia: costo total (comisión + interés)",
    "What you can pay each month": "Lo que puedes pagar cada mes", "Would a consolidation loan help?": "¿Te ayuda un préstamo de consolidación?",
    "You save by transferring": "Ahorras al transferir",
    # ---- Empieza a Invertir con $100 al Mes
    "#": "#", "$100/month to Roth IRA": "$100 al mes a la Roth IRA",
    "...on contributions up to (% of salary)": "...en aportaciones hasta (% del sueldo)",
    "401(k) / 403(b) up to the full employer match": "401(k) / 403(b) hasta el match completo",
    "Account": "Cuenta", "After your chosen years": "Después de los años que elegiste",
    "An illustration using an assumed average return. Real returns vary and can be negative.":
        "Una ilustración con un rendimiento promedio supuesto. Los rendimientos reales cambian y pueden ser negativos.",
    "Assumed average yearly return %": "Rendimiento anual promedio supuesto %",
    "Assumed yearly return %": "Rendimiento anual supuesto %",
    "Assumed yearly return before fees %": "Rendimiento anual supuesto antes de comisiones %",
    "Better choice with these numbers": "Mejor opción con estos números",
    "Check IRS.gov for the current year and catch-up amounts if you're 50+.":
        "Revisa IRS.gov para el año en curso y las aportaciones adicionales si tienes 50 o más.",
    "Contribute at least this % to get it all": "Aporta por lo menos este % para recibirlo todo",
    "Contributing 4% = full match": "Aportar 4% = match completo", "Employer adds per year": "Tu empleador pone al año",
    "Employer matches (% of what you put in)": "Tu empleador iguala (% de lo que pones)", "Ending value": "Valor final",
    "Expected tax rate in retirement %": "Tasa de impuestos esperada en el retiro %",
    "Full emergency fund: 3-6 months of essentials": "Fondo de emergencia completo: 3-6 meses de gastos básicos",
    "Fund A": "Fondo A", "Fund B": "Fondo B", "Goes into the account each year": "Entra a la cuenta cada año",
    "Growth so far": "Crecimiento hasta ahora", "HSA, if you have a high-deductible health plan": "HSA, si tienes seguro médico con deducible alto",
    "HYSA": "Ahorro de alto rendimiento",
    "How much free money your employer adds, and whether you're leaving any behind.":
        "Cuánto dinero gratis pone tu empleador, y si estás dejando algo en la mesa.",
    "IRA limit is shared: Roth + Traditional together. HSA figure is self-only coverage.":
        "El límite de IRA es compartido: Roth + Traditional juntas. La cifra de HSA es para cobertura individual.",
    "IRA: Roth or Traditional": "IRA: Roth o Traditional", "Increase the monthly amount each year by %": "Sube la cantidad mensual cada año en %",
    "Log each deposit. Totals are checked against the yearly limits (2026 figures; update each year).":
        "Anota cada depósito. Los totales se comparan con los límites anuales (cifras de 2026; actualízalas cada año).",
    "Lost to the higher fee": "Perdido por la comisión más alta", "Match you're leaving on the table": "Match que estás dejando ir",
    "Maximum match available": "Match máximo disponible", "Monthly amount": "Cantidad al mes",
    "Monthly compounding. No fees, taxes or inflation. Max 50 years. Not a prediction or a promise.":
        "Interés compuesto mensual. Sin comisiones, impuestos ni inflación. Máximo 50 años. No es una predicción ni una promesa.",
    "Monthly investment": "Inversión mensual", "More in the 401(k), beyond the match": "Más al 401(k), por arriba del match",
    "Note": "Nota", "Pay off high-interest debt (above ~8-10%)": "Paga las deudas caras (más de ~8-10%)",
    "Per paycheck to reach that (26 paychecks)": "Por cheque para llegar (26 cheques)",
    "Pre-tax money you can set aside per year": "Dinero antes de impuestos que puedes apartar al año",
    "Put in (total)": "Lo que pusiste (total)", "Room left": "Te queda", "Roth or Traditional?": "¿Roth o Traditional?",
    "Same deposits, same market, two different yearly fees.": "Mismos depósitos, mismo mercado, dos comisiones anuales distintas.",
    "Same pre-tax money, two tax treatments. The one that wins depends on tax rates now vs later.":
        "El mismo dinero antes de impuestos, dos tratamientos. Cuál gana depende de tu tasa de impuestos hoy contra después.",
    "Simplified: assumes the Traditional tax saving is invested too, yearly compounding, flat tax rates. Ignores income limits, state tax and employer matches. Illustration only.":
        "Simplificado: supone que el ahorro de impuestos de la Traditional también se invierte, interés compuesto anual y tasas fijas. No considera límites de ingreso, impuesto estatal ni match. Solo para ilustrar.",
    "Simplified: the fee is subtracted from the yearly return. Illustration only.":
        "Simplificado: la comisión se resta del rendimiento anual. Solo para ilustrar.",
    "So far": "Hasta ahora",
    "Some matches 'vest' over a few years: if you leave before then, you may keep only part. Check your plan.":
        "Algunos match tardan unos años en ser tuyos ('vesting'): si te vas antes, quizá solo te quedas con una parte. Revisa tu plan.",
    "Starter emergency fund ($500-$1,000)": "Fondo de emergencia inicial ($500-$1,000)", "Starting amount": "Cantidad inicial",
    "Status": "Estado", "Step": "Paso", "Steps done": "Pasos listos", "Store card gone; credit card next": "Tarjeta de tienda pagada; sigue la tarjeta de crédito",
    "Tax when you withdraw": "Impuestos al sacar", "Taxable brokerage account": "Cuenta de inversión normal (con impuestos)",
    "This year's contributions": "Aportaciones de este año", "Value (end of year)": "Valor (fin de año)",
    "Value at retirement (before tax)": "Valor al retiro (antes de impuestos)", "What a fund's fee costs you": "Lo que te cuesta la comisión de un fondo",
    "What regular investing might grow to": "Cuánto podría crecer invertir cada mes", "What you keep": "Lo que te queda",
    "Where each dollar goes first": "A dónde va cada dólar primero",
    "Work down the list. Mark each step as you get to it. (Guide, chapter 2.)": "Ve bajando por la lista. Marca cada paso cuando llegues. (Guía, capítulo 2.)",
    "Year": "Año", "Yearly fee (expense ratio) %": "Comisión anual (expense ratio) %", "Yearly limit": "Límite anual",
    "Years": "Años", "Years until retirement": "Años para tu retiro", "You contribute (% of salary)": "Tú aportas (% del sueldo)",
    "You put in": "Pusiste", "You put in per year": "Pones al año", "Your employer match": "El match de tu empleador",
    "Your tax rate now %": "Tu tasa de impuestos hoy %", "Your yearly salary": "Tu sueldo anual",
    "e.g. '100% up to 4%', or '50% up to 6%'. Check your plan documents.": "Ej.: '100% hasta 4%' o '50% hasta 6%'. Revisa los documentos de tu plan.", "Your debt-free date": "Tu fecha sin deudas", "Your plan": "Tu plan",
}

CHARTS = {"Total debt: plan": ("Deuda total: plan", "Saldo"), "Put in vs growth": ("Lo que pones vs. crecimiento", None)}


def _quoted(formula: str) -> str:
    return re.sub(r'"([^"]*)"', lambda m: '"' + VALUES.get(m.group(1), FORMULA_TEXT.get(m.group(1), m.group(1))) + '"',
                  formula)


def _sheet_refs(formula: str) -> str:
    for en, es in SHEETS.items():
        if en == es:
            continue
        formula = formula.replace(f"'{en}'!", f"'{es}'!")
        formula = re.sub(rf"(?<![\w'.]){re.escape(en)}!", f"'{es}'!", formula)
    return formula


def translate(wb: openpyxl.Workbook, title: str) -> None:
    missing = set()
    for ws in wb:
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if not isinstance(v, str) or not v.strip():
                    continue
                if v.startswith("="):
                    c.value = _sheet_refs(_quoted(v))
                elif v in VALUES:
                    c.value = VALUES[v]
                elif v in LABELS:
                    c.value = LABELS[v]
                else:
                    missing.add(v)
        for dv in ws.data_validations.dataValidation:
            if dv.formula1 and dv.formula1.startswith('"'):
                dv.formula1 = '"' + ",".join(VALUES.get(i, i) for i in dv.formula1.strip('"').split(",")) + '"'
            elif dv.formula1:
                dv.formula1 = _sheet_refs(dv.formula1)
        for cf in ws.conditional_formatting:
            for rule in cf.rules:
                rule.formula = [_sheet_refs(_quoted(f)) for f in (rule.formula or [])]
        for ch in ws._charts:
            # openpyxl keeps the title as rich text; rebuild it from our map.
            en = "".join(r.t for p in ch.title.tx.rich.p for r in (p.r or [])) if ch.title else ""
            if en in CHARTS:
                ch.title = CHARTS[en][0]
                if CHARTS[en][1]:
                    ch.y_axis.title = CHARTS[en][1]
            elif en:
                missing.add(f"chart title: {en}")
    if missing:
        raise SystemExit(f"Untranslated cells: {sorted(missing)}")
    for en, es in SHEETS.items():
        if en in wb.sheetnames:
            wb[en].title = es
    wb.properties.title = title
    wb.properties.language = "es-US"


def build_xlsx(product: dict, path: Path) -> Path:
    """Run the English builder, translating the workbook in memory just before it is written."""
    original = openpyxl.Workbook.save

    def save(wb, filename):
        translate(wb, product["name"])
        return original(wb, filename)

    openpyxl.Workbook.save = save
    try:
        getattr(sheets_en, product["builder"])(path)
    finally:
        openpyxl.Workbook.save = original
    return path


# ---------------------------------------------------------------- PDFs and covers (Node + Playwright)
RENDER_JS = r"""
const { chromium } = require('playwright');
(async () => {
  const jobs = JSON.parse(process.argv[2]);
  const browser = await chromium.launch();
  const report = [];
  try {
    for (const j of jobs) {
      if (j.pdf) {
        const page = await browser.newPage();
        await page.goto('file://' + j.src, { waitUntil: 'load' });
        const over = await page.evaluate(() => [...document.querySelectorAll('.page')]
          .map((p, i) => [i + 1, p.scrollHeight - p.clientHeight]).filter(([, d]) => d > 1));
        await page.pdf({ path: j.pdf, printBackground: true, preferCSSPageSize: true,
                         margin: { top: '0', right: '0', bottom: '0', left: '0' } });
        report.push({ src: j.src, overflow: over });
        await page.close();
      } else {
        const page = await browser.newPage({ viewport: { width: j.w, height: j.h } });
        await page.setContent(j.html, { waitUntil: 'load' });
        await page.screenshot({ path: j.out });
        await page.close();
      }
    }
  } finally { await browser.close(); }
  console.log(JSON.stringify(report));
})().catch(e => { console.error(String(e && e.stack || e)); process.exit(1); });
"""


def wrap_guide(product: dict) -> str:
    body = (HERE / product["slug"] / "guide.html").read_text()
    css = (HERE / "base.css").read_text()
    n = 0


    sections = re.split(r'(?=<section class="page)', body)
    out = []
    for s in sections:
        if s.startswith('<section class="page'):
            n += 1
            if 'class="page cover' not in s[:40]:
                close = s.rfind("</section>")
                s = s[:close] + f'  <div class="folio"><span>{product["name"]}</span><span>{n}</span></div>\n' + s[close:]
        out.append(s)
    return (f'<!doctype html>\n<html lang="es-US">\n<head>\n<meta charset="utf-8">\n<title>{product["name"]}</title>\n'
            f'<style>\n{css}\n</style>\n</head>\n<body>\n{"".join(out)}\n</body>\n</html>\n')


def cover_html(product: dict, w: int, h: int) -> str:
    src = (HERE / product["slug"] / "guide.html").read_text()
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", src, re.S).group(1).replace("<br>", " ")
    art = re.search(r'<svg class="art".*?</svg>', src, re.S).group(0).replace('class="art"', "")
    sq = w == h
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
body{{margin:0;width:{w}px;height:{h}px;background:#14213d;color:#fbf5e9;font-family:Inter,system-ui,sans-serif;
display:flex;{'flex-direction:column;justify-content:space-between' if sq else 'align-items:center'};
padding:{48 if sq else 72}px;box-sizing:border-box;gap:40px;overflow:hidden}}
.t{{flex:1}} .tag{{color:#ff7a59;letter-spacing:.18em;text-transform:uppercase;font-weight:700;font-size:{15 if sq else 18}px}}
h1{{font-size:{58 if sq else 72}px;line-height:.98;font-weight:900;letter-spacing:-.03em;margin:18px 0}}
h1 em{{font-style:normal;color:#2ab7a9}}
.price{{display:inline-block;background:#2ab7a9;color:#14213d;font-weight:900;border-radius:999px;padding:6px 18px;font-size:{22 if sq else 26}px}}
svg{{width:{230 if sq else 340}px;height:{230 if sq else 340}px;flex:none;{'align-self:flex-end;margin-top:-180px' if sq else ''}}}
</style></head><body><div class="t"><div class="tag">Dinero Simple &middot; {product['tag']}</div>
<h1>{h1}</h1><span class="price">${product['price']}</span></div>{art}</body></html>"""


def node_env() -> dict:
    env = dict(os.environ)
    if not env.get("NODE_PATH") and shutil.which("npm"):
        env["NODE_PATH"] = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    return env


def render(jobs: list[dict]) -> list[dict]:
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(RENDER_JS)
    try:
        proc = subprocess.run(["node", fh.name, json.dumps(jobs)], capture_output=True, text=True,
                              env=node_env(), timeout=300)
    finally:
        Path(fh.name).unlink(missing_ok=True)
    if proc.returncode:
        raise SystemExit(f"render failed:\n{proc.stderr}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def recalc_check(xlsx: Path) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", "--headless", "--calc", "--convert-to", "xlsx", "--outdir", tmp, str(xlsx)],
                       capture_output=True, timeout=180, check=True)
        wb = openpyxl.load_workbook(Path(tmp) / xlsx.name, data_only=True)
        return [f"{ws.title}!{c.coordinate}={c.value}" for ws in wb for row in ws.iter_rows() for c in row
                if isinstance(c.value, str) and re.match(r"^#(REF|VALUE|NAME|DIV/0|N/A|NUM|NULL)", c.value)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="recalculate workbooks in LibreOffice")
    ap.add_argument("--out", default=str(HERE / "dist"))
    args = ap.parse_args()
    out_root = Path(args.out)
    jobs, failures = [], []
    for p in PRODUCTS:
        d = out_root / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        html = d / f'{p["slug"]}.html'
        html.write_text(wrap_guide(p))
        jobs.append({"src": str(html), "pdf": str(d / p["pdf"])})
        for name, w, h in (("cover.png", 1280, 720), ("cover-square.png", 600, 600)):
            jobs.append({"html": cover_html(p, w, h), "w": w, "h": h, "out": str(d / name)})
        if p.get("xlsx"):
            build_xlsx(p, d / p["xlsx"])
        shutil.copy(HERE / p["slug"] / "LISTING.md", d / "LISTING.md")
    for r in render(jobs):
        if r["overflow"]:
            failures.append(f'{Path(r["src"]).name}: content overflows on pages {r["overflow"]}')
    if args.check:
        for p in (p for p in PRODUCTS if p.get("xlsx")):
            bad = recalc_check(out_root / p["slug"] / p["xlsx"])
            if bad:
                failures.append(f'{p["xlsx"]}: {len(bad)} formula errors, e.g. {bad[:5]}')
    for p in PRODUCTS:
        d = out_root / p["slug"]
        files = [(d / p["pdf"], p["pdf"])] + ([(d / p["xlsx"], p["xlsx"])] if p.get("xlsx") else [])
        for idx, slug in enumerate(p.get("bundle", []), start=1):
            if slug in EXISTING:
                e = EXISTING[slug]
                files += [(e["dir"] / f, f"{idx}. {e['name']}/{f}") for f in e["files"]]
                continue
            o = next(x for x in PRODUCTS if x["slug"] == slug)
            files += [(out_root / slug / o["pdf"], f"{idx}. {o['name'].replace('$', '')}/{o['pdf']}"),
                      (out_root / slug / o["xlsx"], f"{idx}. {o['name'].replace('$', '')}/{o['xlsx']}")]
        missing = [str(f) for f, _ in files if not f.exists()]
        if missing:
            failures.append(f'{p["zip"]}: missing {missing}')
            continue
        with zipfile.ZipFile(d / p["zip"], "w", zipfile.ZIP_DEFLATED) as z:
            for f, arc in files:
                z.write(f, arc)
    for f in failures:
        print("FAIL", f)
    print(f"built {len(PRODUCTS)} product(s) into {out_root}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
