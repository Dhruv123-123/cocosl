"""Build the Spanish (Dinero Simple) versions of two Money Made Simple products.

    python launch/dinero-simple/products/build.py            # PDFs, workbooks, covers, zips -> dist/
    python launch/dinero-simple/products/build.py --check    # also recalc workbooks in LibreOffice

* El Kit para Recortar Gastos ($5)   <- The Bill Cut Kit
* Tu Fecha Sin Deudas ($17)          <- The Debt-Free Date Planner

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
]

SHEETS = {
    "Summary": "Resumen", "Audit": "Revisión", "Negotiation Log": "Registro de llamadas",
    "Plan": "Plan", "Balance Transfer": "Transferencia", "Consolidation": "Consolidación",
    "Progress": "Avance", "Schedule": "Calendario",
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
}

FORMULA_TEXT = {
    "30+ years": "Más de 30 años", "Never": "Nunca", "Increase payments": "Sube tus pagos",
    "Cheaper than your current plan.": "Más barato que tu plan actual.",
    "Not worth it at this payment.": "No conviene con este pago.",
    "Worth it, IF you stop adding new spending to either card.":
        "Conviene, SI dejas de hacer compras nuevas con las dos tarjetas.",
    "Your current plan is cheaper. Keep going.": "Tu plan actual sale más barato. Síguele.",
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
    "You save by transferring": "Ahorras al transferir", "Your debt-free date": "Tu fecha sin deudas", "Your plan": "Tu plan",
}

CHARTS = {"Total debt: plan": ("Deuda total: plan", "Saldo")}


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
                ch.title, ch.y_axis.title = CHARTS[en]
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
        build_xlsx(p, d / p["xlsx"])
        shutil.copy(HERE / p["slug"] / "LISTING.md", d / "LISTING.md")
    for r in render(jobs):
        if r["overflow"]:
            failures.append(f'{Path(r["src"]).name}: content overflows on pages {r["overflow"]}')
    if args.check:
        for p in PRODUCTS:
            bad = recalc_check(out_root / p["slug"] / p["xlsx"])
            if bad:
                failures.append(f'{p["xlsx"]}: {len(bad)} formula errors, e.g. {bad[:5]}')
    for p in PRODUCTS:
        d = out_root / p["slug"]
        with zipfile.ZipFile(d / p["zip"], "w", zipfile.ZIP_DEFLATED) as z:
            z.write(d / p["pdf"], p["pdf"])
            z.write(d / p["xlsx"], p["xlsx"])
    for f in failures:
        print("FAIL", f)
    print(f"built {len(PRODUCTS)} product(s) into {out_root}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
