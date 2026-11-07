"""Build the Spanish spreadsheet from the English 20-Minute Budget template.

Translates every label, renames the tabs (and every formula that points at them),
translates the dropdown values together with the formulas that test them, and
renames the example person (Maya -> Daniela) to match the Spanish guide.

    python launch/dinero-simple/src/build_xlsx.py
"""
from __future__ import annotations

import re
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "launch" / "product" / "20-Minute-Budget-Template.xlsx"
OUT = ROOT / "launch" / "dinero-simple" / "product" / "Presupuesto-20-Minutos-Plantilla.xlsx"

SHEETS = {
    "Setup": "Configuración", "Monthly Plan": "Plan mensual", "Weekly Check-in": "Revisión semanal",
    "Sinking Funds": "Fondos de previsión", "Debt Payoff": "Pago de deudas", "Payoff Schedule": "Calendario de pagos",
}

# Values that formulas and dropdowns compare against: translated everywhere at once.
VALUES = {
    "Weekly": "Cada semana", "Every two weeks": "Cada dos semanas", "Twice a month": "Dos veces al mes",
    "Monthly": "Una vez al mes", "Yes": "Sí", "No": "No",
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", "Thursday": "Jueves", "Friday": "Viernes",
    "Saturday": "Sábado", "Sunday": "Domingo",
}

# Other quoted text inside formulas.
FORMULA_TEXT = {
    "Enter your pay on the Setup tab": "Escribe tu pago en la pestaña Configuración",
    "Over-planned by $": "Planeaste de más por $",
    ". Trim Goals or Funds first, then Bills.": ". Recorta Metas o Fondos primero, luego Gastos fijos.",
    "OK: every dollar has a job.": "Bien: cada dólar tiene un trabajo.",
    "Over 30 yrs": "Más de 30 años",
    "Extra payment can't be negative.": "El pago extra no puede ser negativo.",
    ": bal+int": ": saldo+int",
}

LABELS = {
    "The 20-Minute Budget: Setup": "El Presupuesto de 20 Minutos: Configuración",
    "Fill this tab first. It feeds every other tab.": "Llena esta pestaña primero. Alimenta a todas las demás.",
    "Yellow cells = your inputs. White cells calculate automatically. Example data shown is fictional (Maya, from the guide): replace it with yours.":
        "Celdas amarillas = tus datos. Las blancas se calculan solas. El ejemplo es ficticio (Daniela, de la guía): cámbialo por tus números.",
    "Your name": "Tu nombre", "Maya (example)": "Daniela (ejemplo)",
    "HOW TO USE THIS TEMPLATE": "CÓMO USAR ESTA PLANTILLA",
    "Budget month starts on": "El mes del presupuesto empieza el",
    "1. Setup (this tab): pay frequency + one typical paycheck. The sheet converts it to a monthly figure.":
        "1. Configuración (esta pestaña): cada cuánto te pagan + un cheque típico. La hoja lo convierte a cifra mensual.",
    "How often are you paid?": "¿Cada cuánto te pagan?",
    "2. Monthly Plan: list every fixed bill and your goals. It calculates your weekly number.":
        "2. Plan mensual: anota cada gasto fijo y tus metas. Calcula tu número semanal.",
    "Typical take-home paycheck (after tax)": "Cheque neto típico (después de impuestos)",
    "3. Sinking Funds: costs that aren't monthly (car repairs, gifts...). Monthly amount = cost / months.":
        "3. Fondos de previsión: gastos que no son mensuales (carro, regalos...). Cantidad mensual = costo / meses.",
    "Monthly take-home pay": "Sueldo neto mensual",
    "4. Weekly Check-in: once a week, type what you spent. That's it.":
        "4. Revisión semanal: una vez a la semana, escribe lo que gastaste. Y ya.",
    "Other regular monthly income": "Otros ingresos mensuales fijos",
    "5. Debt Payoff: enter your debts. Compare avalanche vs snowball side by side.":
        "5. Pago de deudas: escribe tus deudas. Compara avalancha y bola de nieve lado a lado.",
    "Total monthly income": "Ingreso mensual total",
    "Buffer to keep in checking": "Colchón en la cuenta de cheques",
    "TO START FRESH": "PARA EMPEZAR DE CERO",
    "Weekly check-in day": "Día de la revisión semanal",
    "Clear the yellow cells on every tab (select them and press Delete). Don't delete white cells.":
        "Borra las celdas amarillas de cada pestaña (selecciónalas y presiona Suprimir). No borres las blancas.",
    "Emergency fund target (months of bills)": "Meta del fondo de emergencia (meses de gastos fijos)",
    "Emergency fund target ($)": "Meta del fondo de emergencia ($)",
    "GOOGLE SHEETS": "GOOGLE SHEETS",
    "Emergency fund saved so far": "Fondo de emergencia ahorrado hasta hoy",
    "File > Import > Upload this .xlsx (or open it from Google Drive). Formulas and dropdowns carry over.":
        "Archivo > Importar > Subir este .xlsx (o ábrelo desde Google Drive). Las fórmulas y listas se conservan.",
    "Emergency fund progress": "Avance del fondo de emergencia",
    "Educational tool only. Not financial, tax or investment advice.":
        "Herramienta educativa. No es asesoría financiera, fiscal ni de inversión.",
    "Monthly Plan": "Plan mensual",
    "Bills + Funds + Goals are paid first. What's left becomes your weekly number.":
        "Gastos fijos + Fondos + Metas se pagan primero. Lo que queda es tu número semanal.",
    "Monthly income (from Setup)": "Ingreso mensual (de Configuración)",
    "Line 1: Bills": "Línea 1: Gastos fijos",
    "Line 2: Funds (from Sinking Funds tab)": "Línea 2: Fondos (de la pestaña Fondos de previsión)",
    "Line 3: Goals": "Línea 3: Metas",
    "Monthly pool (income - bills - funds - goals)": "Bolsa mensual (ingreso - gastos fijos - fondos - metas)",
    "Line 4: YOUR WEEKLY NUMBER": "Línea 4: TU NÚMERO SEMANAL",
    "per week": "por semana",
    "Bills as % of income": "Gastos fijos como % del ingreso",
    "Status": "Estado",
    "LINE 1: BILLS (fixed monthly costs, incl. minimum debt payments)":
        "LÍNEA 1: GASTOS FIJOS (costos mensuales fijos, incluye pagos mínimos de deudas)",
    "Bill": "Gasto", "Monthly amount": "Cantidad mensual", "Due day": "Día de pago", "Autopay?": "¿Pago automático?",
    "Notes": "Notas", "Rent": "Renta",
    "Renters + car insurance": "Seguro de inquilino + carro",
    "Get a new quote every 6 months": "Cotiza de nuevo cada 6 meses",
    "Utilities": "Luz, agua y gas", "Averaged; higher in summer": "Promedio; sube en verano",
    "Internet": "Internet", "Phone": "Celular", "Subscriptions (3)": "Suscripciones (3)",
    "Review at monthly reset": "Revisar en el ajuste mensual",
    "Car loan minimum": "Mínimo del carro", "Also listed on Debt Payoff": "También está en Pago de deudas",
    "Student loan minimum": "Mínimo préstamo estudiantil", "Credit card minimum": "Mínimo tarjeta de crédito",
    "Personal loan minimum": "Mínimo préstamo personal", "Bills total": "Total gastos fijos",
    "LINE 3: GOALS (pay yourself first)": "LÍNEA 3: METAS (págate a ti primero)",
    "Goal": "Meta", "Emergency fund": "Fondo de emergencia",
    "Target is on the Setup tab": "La meta está en Configuración",
    "Extra debt payment": "Pago extra a deudas", "Used by the Debt Payoff tab": "Lo usa la pestaña Pago de deudas",
    "Investing / retirement": "Inversión / retiro",
    "Start once starter emergency fund is done": "Empieza cuando tengas el fondo de emergencia inicial",
    "Goals total": "Total metas",
    "Weekly Check-in": "Revisión semanal",
    "20 minutes, once a week: Look (5) > Log (5) > Check (5) > Decide one thing (5).":
        "20 minutos, una vez a la semana: Mira (5) > Anota (5) > Revisa (5) > Decide una cosa (5).",
    "Weekly number (from Monthly Plan)": "Número semanal (del Plan mensual)",
    "THE 20-MINUTE ROUTINE": "LA RUTINA DE 20 MINUTOS",
    "Carry-over from last month (+ or -)": "Lo que pasa del mes anterior (+ o -)",
    "0-5 min  LOOK: open bank + card apps. Pay off any card used for weekly spending.":
        "0-5 min  MIRA: abre las apps del banco y las tarjetas. Paga la tarjeta que usaste para el gasto semanal.",
    "Roll weekly leftovers into next week?": "¿Pasar lo que sobra a la próxima semana?",
    "5-10 min  LOG: type this week's total in the Spent column.":
        "5-10 min  ANOTA: escribe el total de la semana en la columna Gastado.",
    "10-15 min  CHECK: bills out at the right amounts? Payday transfers happened?":
        "10-15 min  REVISA: ¿salieron los gastos fijos correctos? ¿Se hicieron las transferencias?",
    "Week": "Semana", "Week of": "Semana del", "Allowance": "Asignado", "Spent": "Gastado",
    "Left this week": "Queda esta semana", "Bills + transfers checked?": "¿Gastos fijos + transferencias revisados?",
    "One decision / notes": "Una decisión / notas",
    "              Any unknown charges? Update Sinking Funds balances if you used one.":
        "              ¿Cargos desconocidos? Actualiza Fondos de previsión si usaste alguno.",
    "Under by $12.60, rolled into next week.": "Sobraron $12.60, pasan a la próxima semana.",
    "15-20 min  DECIDE ONE THING: roll leftover / plan a make-up week /":
        "15-20 min  DECIDE UNA COSA: pasa lo que sobró / planea una semana de reponer /",
    "Birthday dinner. Over by $18.25: cheaper week 3.": "Cena de cumpleaños. Me pasé $18.25: semana 3 más barata.",
    "              pick a fund for an upcoming cost / cancel one unused subscription.":
        "              elige un fondo para un gasto que viene / cancela una suscripción que no usas.",
    "Make-up week worked. Cancelled unused streaming sub.": "La semana de reponer funcionó. Cancelé un streaming que no usaba.",
    "MONTHLY RESET (a few days before payday)": "AJUSTE MENSUAL (unos días antes del día de pago)",
    "Review the weeks > update Monthly Plan > assign leftovers > update transfers.":
        "Repasa las semanas > actualiza el Plan mensual > asigna lo que sobró > actualiza transferencias.",
    "Then clear the Spent, checked and notes cells for the new month.":
        "Luego borra Gastado, revisados y notas para el nuevo mes.",
    "Weeks logged": "Semanas anotadas", "Total spent so far": "Total gastado hasta hoy",
    "Leftover to assign at monthly reset": "Sobrante para asignar en el ajuste mensual",
    "Week 5 only happens in five-week months. Overspending always carries into next week; underspending carries only if you chose Yes above.":
        "La semana 5 solo existe en meses de cinco semanas. Si te pasas, siempre baja la siguiente semana; lo que sobra pasa solo si elegiste Sí arriba.",
    "Sinking Funds": "Fondos de previsión",
    "Save a little every month for costs that are predictable but not monthly.":
        "Aparta un poco cada mes para gastos predecibles que no son mensuales.",
    "Fund": "Fondo", "Yearly / target cost": "Costo anual / meta", "Months to save": "Meses para ahorrar",
    "Monthly contribution": "Aportación mensual", "Current balance": "Saldo actual", "Progress": "Avance",
    "What it covers": "Qué cubre", "Car maintenance": "Mantenimiento del carro",
    "Oil changes, tyres, registration": "Cambios de aceite, llantas, registro",
    "Gifts & holidays": "Regalos y fiestas", "Birthdays, December holidays": "Cumpleaños, fiestas de diciembre",
    "Travel": "Viajes", "One trip home a year": "Un viaje a ver a la familia al año",
    "Clothing": "Ropa", "Shoes, work clothes": "Zapatos, ropa de trabajo",
    "Medical / copays": "Médico / copagos", "Copays, prescriptions, dental": "Copagos, recetas, dentista",
    "Annual renewals": "Renovaciones anuales", "Annual app + membership renewals": "Apps y membresías anuales",
    "Total": "Total",
    "When you spend from a fund, lower its Current balance. When the monthly transfer lands, raise it. Update during your weekly check-in.":
        "Cuando gastes de un fondo, baja su Saldo actual. Cuando llegue la transferencia del mes, súbelo. Actualízalo en tu revisión semanal.",
    "Debt Payoff: Avalanche vs Snowball": "Pago de deudas: avalancha o bola de nieve",
    "Minimums on everything, all extra to one target. Freed-up minimums roll to the next debt.":
        "Mínimos en todo, todo el extra a un objetivo. Los mínimos liberados pasan a la siguiente deuda.",
    "Debt": "Deuda", "Balance": "Saldo", "APR %": "APR %", "Minimum / mo": "Mínimo / mes",
    "Avalanche order": "Orden avalancha", "Snowball order": "Orden bola de nieve",
    "Paid off: avalanche (month #)": "Liquidada: avalancha (mes #)",
    "Paid off: snowball (month #)": "Liquidada: bola de nieve (mes #)",
    "Credit card": "Tarjeta de crédito", "Personal loan": "Préstamo personal", "Car loan": "Préstamo del carro",
    "Student loan": "Préstamo estudiantil", "Extra payment per month": "Pago extra al mes",
    "Linked to 'Extra debt payment' on Monthly Plan. Type a number to override; set 0 to see minimums-only.":
        "Viene de 'Pago extra a deudas' en el Plan mensual. Escribe un número para cambiarlo; pon 0 para ver solo mínimos.",
    "Total monthly debt budget": "Presupuesto mensual total para deudas",
    "Comparison": "Comparación", "Avalanche": "Avalancha", "Snowball": "Bola de nieve", "Difference": "Diferencia",
    "Months to debt-free": "Meses para quedar sin deudas", "Debt-free month": "Mes sin deudas",
    "Total interest paid": "Interés total pagado", "First debt paid off (month #)": "Primera deuda liquidada (mes #)",
    "Difference = snowball minus avalanche. Positive interest difference = what avalanche saves you. Negative 'first debt' difference = how many months sooner snowball gives you a win.":
        "Diferencia = bola de nieve menos avalancha. Diferencia de interés positiva = lo que te ahorra la avalancha. Diferencia negativa en 'primera deuda' = cuántos meses antes te da un triunfo la bola de nieve.",
    "Estimate only: lenders calculate interest daily and may apply payments differently. Month-by-month detail is on the Payoff Schedule tab.":
        "Solo es un estimado: los prestamistas calculan el interés diario y pueden aplicar los pagos de otra forma. El detalle mes a mes está en la pestaña Calendario de pagos.",
    "Payoff Schedule (calculated automatically, no inputs here)":
        "Calendario de pagos (se calcula solo, aquí no escribes nada)",
    "Simple monthly model: interest = balance x APR / 12, then minimums, then extra to the target debt. Real lenders compute daily, so treat as an estimate.":
        "Modelo mensual simple: interés = saldo x APR / 12, luego mínimos, luego el extra a la deuda objetivo. Los prestamistas calculan diario: tómalo como estimado.",
    "AVALANCHE (highest APR first)": "AVALANCHA (primero el APR más alto)",
    "SNOWBALL (smallest balance first)": "BOLA DE NIEVE (primero el saldo más chico)",
    "Month": "Mes", "min": "mín", "extra": "extra", "end bal": "saldo final", "extra pool": "bolsa extra",
    "total balance": "saldo total", "interest this month": "interés del mes",
}


def _quoted(formula: str) -> str:
    def swap(m: re.Match) -> str:
        text = m.group(1)
        return '"' + VALUES.get(text, FORMULA_TEXT.get(text, text)) + '"'
    return re.sub(r'"([^"]*)"', swap, formula)


def _sheet_refs(formula: str) -> str:
    for en, es in SHEETS.items():
        formula = formula.replace(f"'{en}'!", f"'{es}'!")
        formula = re.sub(rf"(?<![\w'.]){re.escape(en)}!", f"'{es}'!", formula)
    return formula


def build() -> Path:
    wb = openpyxl.load_workbook(SRC)
    missing = set()
    for ws in wb:
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if not isinstance(v, str):
                    continue
                if v.startswith("="):
                    c.value = _sheet_refs(_quoted(v))
                elif v in VALUES:
                    c.value = VALUES[v]
                elif v in LABELS:
                    c.value = LABELS[v]
                elif v.strip():
                    missing.add(v)
        for dv in ws.data_validations.dataValidation:
            if dv.formula1 and dv.formula1.startswith('"'):
                items = dv.formula1.strip('"').split(",")
                dv.formula1 = '"' + ",".join(VALUES.get(i, i) for i in items) + '"'
            elif dv.formula1:
                dv.formula1 = _sheet_refs(dv.formula1)
            for attr in ("error", "errorTitle", "prompt", "promptTitle"):
                val = getattr(dv, attr)
                if val:
                    setattr(dv, attr, FORMULA_TEXT.get(val, val))
        for cf in ws.conditional_formatting:
            for rule in cf.rules:
                rule.formula = [_sheet_refs(_quoted(f)) for f in (rule.formula or [])]
    if missing:
        raise SystemExit(f"Untranslated cells: {sorted(missing)}")
    for en, es in SHEETS.items():
        wb[en].title = es
    wb.properties.title = "El Presupuesto de 20 Minutos"
    wb.properties.language = "es-US"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    return OUT


if __name__ == "__main__":
    print(build().relative_to(ROOT))
