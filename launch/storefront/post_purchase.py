"""Three post-purchase emails for each brand's lead product: thank-you (day 0), how to use it (day 3), cross-sell (day 7).

    python launch/storefront/build_storefront.py      # writes dist/emails/ with the rest of the storefront kit

"Lead product" is the one each storefront features (build_storefront.BRANDS[...]["featured"]); there are no sales
yet, so this is the expected best seller, not a measured one. 1099 Money's tracker already has this exact sequence
on its branch (PR #10, apps/freelance-tax/emails/buyers/), so it's referenced, not rewritten.

Placeholders in {{double_braces}} are filled by the email tool or by hand; no real link or payment URL is in here.
Trigger: the purchase (Gumroad > Workflows, or a purchase tag in the email tool). Drop the day-7 email for anyone
who already owns the product it recommends. Nothing here is sent or scheduled.
"""
from __future__ import annotations

FOOT_EN = {"Money Made Simple": "*Educational content, not financial advice.*",
           "Scam Decoded": "*General education, not legal or financial advice. No product can promise you'll never be scammed; "
                           "this kit helps your family slow down and check.*",
           "Dinero Simple": "*Contenido educativo, no es asesoría financiera, fiscal ni legal.*"}

SEQUENCES = {
    "Money Made Simple": dict(
        product="The 20-Minute Budget", next="The Debt-Free Date Planner", code="BUDGET5", key="money-made-simple", lang="en",
        placeholders={"{{download_url}}": "the buyer's Gumroad download link", "{{planner_url}}": "The Debt-Free Date Planner's product page"},
        emails=[
            dict(day=0, subject="Your 20-Minute Budget (start here)", preheader="One evening to set up, then 20 minutes a week.",
                 goal="Delivery and setup; no pitch", body="""Hi,

Thank you for buying The 20-Minute Budget. Your files: {{download_url}}

The fastest way to start:

1. Read the method and the 6-step setup at the start of the guide (about 10 minutes).
2. Open the spreadsheet. On **Setup**, type your take-home pay and how often you're paid.
3. On **Monthly Plan**, list your bills and goals. The sheet gives you your weekly spending number.
4. Delete the example rows once you've seen how they work. Yellow cells are yours; everything else calculates itself.

Set a weekly 20-minute alarm called "money check-in". That's the habit that makes it work.

If anything is confusing, reply to this email. A real person reads it.

The Money Made Simple team"""),
            dict(day=3, subject="Your first 20-minute check-in", preheader="One number a week, and what to do when it runs out.",
                 goal="Get them to do the weekly check-in once", body="""Hi,

Here's the weekly check-in, step by step:

1. **Look at one number:** what you spent from your weekly number since last time. Your bank app is enough.
2. **Type it into Weekly Check-in.** The sheet shows what's left and rolls it over (or takes it out of next week).
3. **Ran out early?** That's information, not failure. Check whether a "surprise" cost belongs in **Sinking Funds** instead.
4. **Money left?** Pick where it goes: a fund, a goal or a debt. Don't let it drift back into spending.
5. **Once a month:** the monthly reset in the guide. Also about 20 minutes.

The first two or three weeks are the hardest. After that, it's mostly typing one number.

The Money Made Simple team"""),
            dict(day=7, subject="What the leftover is for: a date on your debts", preheader="Your $5-off code, if it's useful.",
                 goal="One honest cross-sell: The Debt-Free Date Planner with BUDGET5", body="""Hi,

Once the weekly number is working, the question is what to do with what's left. If you have debts, the next step is a date: the month and year you owe nothing.

That's what **The Debt-Free Date Planner** does:

- Up to 10 debts, avalanche, snowball or your own order.
- Your exact debt-free date, and what each extra payment is worth.
- Calculators that show whether a balance transfer or a consolidation loan would actually save you money.

You already have the budget, so code **BUDGET5** takes $5 off ($12 instead of $17): {{planner_url}}

No debts? Then skip this one. That's it from this series.

The Money Made Simple team"""),
        ]),
    "Scam Decoded": dict(
        product="The Family Scam-Proofing Kit", next="Protect Your Parents (guide)", code="KITPARENTS", key="scam-decoded", lang="en",
        placeholders={"{{download_url}}": "the buyer's Gumroad download link", "{{parents_url}}": "Protect Your Parents' product page"},
        emails=[
            dict(day=0, subject="Your Family Scam-Proofing Kit (start with page 2)", preheader="Book the 15-minute family meeting this week.",
                 goal="Delivery and one action: book the meeting; no pitch", body="""Hi,

Thank you for getting the kit. Your file: {{download_url}}

Start here:

1. Read page 2. It's the family meeting, scripted minute by minute.
2. Pick a time this week and send the family a message: "15 minutes on Sunday, I want us to have a plan for scam calls."
3. Print the family plan sheet and the fridge card before the meeting.

That's all for today. If you have a question, reply to this email. A real person reads it.

The Scam Decoded team"""),
            dict(day=3, subject="The 15-minute family meeting, in order", preheader="Safe word, call-back rule, payment rule, trusted person.",
                 goal="Get the meeting done and the plan written down", body="""Hi,

Here's the meeting, in order. The script on page 2 has the words.

1. **Safe word** (3 minutes). Something nobody would guess and nobody posts online. Anyone who calls in a panic asking for money gets asked for it.
2. **Call-back rule** (2 minutes). Hang up and call back on the number you already have. Caller ID can be faked, and voices can be cloned.
3. **Payment rule** (2 minutes). Nobody real asks for gift cards, crypto, a wire or cash in a box. That request is the tell.
4. **Trusted person** (3 minutes). The one person everyone calls before sending money.
5. **Write it on the plan sheet** and put the fridge card by the phone (5 minutes).

After the meeting, the account lockdown checklist is one lock a night for five nights, and the credit freeze tracker covers each adult and child.

The Scam Decoded team"""),
            dict(day=7, subject="If you're helping a parent", preheader="Your $10-off code, if it's useful.",
                 goal="One honest cross-sell: Protect Your Parents with KITPARENTS", body="""Hi,

Most people who make the family plan end up helping a parent next: their phone, their bank, their credit, and the calls they get.

That's what **Protect Your Parents** covers:

- Every setting to change on their phone, bank and credit, step by step.
- 10 word-for-word phone scripts for the calls that worry you most.

You already have the kit, so code **KITPARENTS** takes $10 off ($19 instead of $29): {{parents_url}}

Not helping a parent right now? Then skip it. That's the last email in this series.

The Scam Decoded team"""),
        ]),
    "Dinero Simple": dict(
        product="El Presupuesto de 20 Minutos", next="Tu Fecha Sin Deudas", code="SEMANA5", key="dinero-simple", lang="es",
        review=("NATIVE REVIEW PENDING: estos correos se escribieron en español pero falta que una persona que hable "
                "español con fluidez los revise. No se envían antes de eso."),
        placeholders={"{{download_url}}": "el enlace de descarga de Gumroad del comprador",
                      "{{fecha_url}}": "la página de Tu Fecha Sin Deudas"},
        emails=[
            dict(day=0, subject="Tu Presupuesto de 20 Minutos (empieza aquí)", preheader="Lo armas una noche y luego son 20 minutos a la semana.",
                 goal="Entrega y configuración; sin venta", body="""Hola:

Gracias por comprar El Presupuesto de 20 Minutos. Tus archivos: {{download_url}}

Para empezar rápido:

1. Lee el método y los 6 pasos al principio de la guía (unos 10 minutos).
2. Abre la hoja de cálculo. En **Configuración**, escribe tu sueldo neto y cada cuánto te pagan.
3. En **Plan mensual**, anota tus gastos fijos y tus metas. La hoja te da tu número semanal para gastar.
4. Mira el ejemplo de Daniela y después cambia las celdas amarillas por tus números. Lo demás se calcula solo.

Pon una alarma semanal de 20 minutos: "Revisión de dinero". Ese hábito es lo que hace que funcione.

Si algo no queda claro, contesta este correo. Lo lee una persona.

El equipo de Dinero Simple"""),
            dict(day=3, subject="Tu primera revisión de 20 minutos", preheader="Un número a la semana, y qué hacer si se acaba antes.",
                 goal="Que haga la revisión semanal una vez", body="""Hola:

Así es la revisión semanal, paso a paso:

1. **Mira un solo número:** cuánto gastaste de tu número semanal desde la última vez. Con la app de tu banco basta.
2. **Escríbelo en Revisión semanal.** La hoja te dice cuánto queda y lo pasa a la semana siguiente (o lo descuenta).
3. **¿Se acabó antes?** Eso te da información; no es un fracaso. Revisa si un gasto "sorpresa" va mejor en **Fondos de previsión**.
4. **¿Sobró?** Decide a dónde va: un fondo, una meta o una deuda. Que no se vuelva a ir en gastos.
5. **Una vez al mes:** el ajuste mensual de la guía. Unos 20 minutos.

Las primeras dos o tres semanas son las más difíciles. Después, casi todo es escribir un número.

El equipo de Dinero Simple"""),
            dict(day=7, subject="Lo que sobra: ponle fecha a tus deudas", preheader="Tu código de $5 de descuento, por si te sirve.",
                 goal="Una sola venta cruzada honesta: Tu Fecha Sin Deudas con SEMANA5", body="""Hola:

Cuando el número semanal ya funciona, la pregunta es qué hacer con lo que sobra. Si tienes deudas, el siguiente paso es una fecha: el mes y el año en que ya no debes nada.

Para eso es **Tu Fecha Sin Deudas**:

- Hasta 10 deudas, con avalancha, bola de nieve o tu propio orden.
- Tu fecha exacta, y cuánto vale cada pago extra.
- Calculadoras que te dicen si una transferencia de saldo o un préstamo de consolidación de verdad te conviene.

Como ya tienes el presupuesto, el código **SEMANA5** te da $5 de descuento ($12 en lugar de $17): {{fecha_url}}

¿No tienes deudas? Entonces no lo necesitas. Este es el último correo de esta serie.

El equipo de Dinero Simple"""),
        ]),
}

# Codes the day-7 emails use that don't exist in any plan yet: create them in Gumroad > Checkout > Discounts first.
NEW_CODES = {"SEMANA5": "$5 off Tu Fecha Sin Deudas, for buyers of El Presupuesto de 20 Minutos (mirrors BUDGET5)"}
ELSEWHERE = {"1099 Money": ("The Quarterly Tax Tracker", "PR #10, apps/freelance-tax/emails/buyers/ (day 0 welcome, "
                            "day 3 first payment, day 7 bundle upgrade with TRACKER15)")}


def email_md(brand: str, i: int, e: dict) -> str:
    seq = SEQUENCES[brand]
    head = ["---", f"order: {i}", f"day: {e['day']}", f"subject: {e['subject']}", f"preheader: {e['preheader']}",
            f"goal: {e['goal']}", "---", ""]
    if seq.get("review"):
        head += [f"> {seq['review']}", "", ""]
    return "\n".join(head) + e["body"] + "\n\n" + FOOT_EN[brand] + "\n"


def slug(subject: str) -> str:
    import re
    import unicodedata
    s = unicodedata.normalize("NFKD", subject).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s if len(s) <= 40 else s[:41].rsplit("-", 1)[0]


def index_md() -> str:
    out = ["# Post-purchase emails, one sequence per brand", "",
           "Three emails after someone buys each brand's lead product (the one its storefront features; there's no "
           "sales data yet, so it's the expected best seller). Day 0 thank-you and setup, day 3 how to use it, day 7 "
           "one cross-sell with the buyer's code. Plain text, one link per email, no fake urgency. Nothing is sent or "
           "scheduled; set the trigger in Gumroad > Workflows (or the email tool) after review.", "",
           "| Brand | After buying | Day 7 recommends | Code | Files |", "|---|---|---|---|---|"]
    for brand, seq in SEQUENCES.items():
        out.append(f"| {brand} | {seq['product']} | {seq['next']} | `{seq['code']}` | `{seq['key']}/` |")
    for brand, (prod, where) in ELSEWHERE.items():
        out.append(f"| {brand} | {prod} | The Freelancer Money Bundle | `TRACKER15` | already written: {where} |")
    out += ["", "## Before sending", "",
            "- Create the codes that don't exist yet: " + "; ".join(f"`{c}` ({w})" for c, w in NEW_CODES.items()) + ".",
            "- Fill the placeholders. Per brand:"]
    for brand, seq in SEQUENCES.items():
        out.append(f"  - {brand}: " + "; ".join(f"`{k}` = {v}" for k, v in seq["placeholders"].items()))
    out += ["- Skip the day-7 email for buyers who already own what it recommends.",
            "- Dinero Simple: a fluent Spanish speaker reviews the three emails first (NATIVE REVIEW PENDING).", ""]
    for brand, seq in SEQUENCES.items():
        out += [f"## {brand}: after {seq['product']}", ""]
        for i, e in enumerate(seq["emails"], 1):
            out += [f"**{i}. Day {e['day']}: {e['subject']}** ({e['goal']})", ""]
    return "\n".join(out)
