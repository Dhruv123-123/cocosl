"""Dinero Simple printables (Spanish): El Presupuesto Familiar, el Registro de Envíos and la Lista para Construir tu Crédito.

Audience-facing copy is Spanish (tú, neutral Latin American with a Mexican-American lean, per brands/dinero-simple.yaml).
Operator notes stay in English. EVERYTHING here needs a fluent Spanish speaker's review before it is listed
(REVIEW_CHECKLIST_ES.md is written next to the files by the build).

Facts used (US, checked Nov 2026; recheck before listing):
- Remittance Transfer Rule (Regulation E, CFPB): before you pay, the provider must show fees, the exchange rate and the
  amount that arrives; you get a receipt; you can cancel within 30 minutes for a full refund (if the money hasn't been
  picked up or deposited); you have 180 days to report an error. Complaints: consumerfinance.gov or 855-411-2372.
- Since Jan 1 2026 a 1% federal tax applies to remittances paid in cash, money order or cashier's check; paying from a
  bank account or with a debit or credit card is not covered (One Big Beautiful Bill Act). Hedged: "verifica con tu servicio".
- Free credit reports from all three bureaus every week at AnnualCreditReport.com. Credit freezes are free.
- Credit repair companies can't charge before they do the work (Credit Repair Organizations Act). A "CPN" sold as a new
  credit identity is a scam and using one can be a crime (FTC). Nonprofit credit counseling: NFCC.
- An ITIN can be enough to open some bank accounts and secured cards; it depends on the bank or credit union.
"""
from __future__ import annotations

from shop import Brand

REVIEW = ("REVISIÓN NATIVA PENDIENTE / NATIVE REVIEW PENDING: do not list until a fluent Spanish speaker has read the "
          "title, tags, description, Gumroad copy and every page, and signed REVIEW_CHECKLIST_ES.md.")
BRAND = Brand("Dinero Simple", "@dinerosimple", ink="#14213d", cream="#fbf5e9", accent="#2ab7a9", accent_d="#1d7f76",
              warm="#ff7a59", tint="#fdeee8", muted="#5d6470", line="#cdc8bd", lang="es",
              foot_text="solo para uso personal, por favor no lo revendas ni lo compartas", review=REVIEW)
P = BRAND.page
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
         "Noviembre", "Diciembre"]


def _tbl(headers: list[tuple[str, str]], n: int, cls: str = "", first: list[str] | None = None) -> str:
    head = "".join(f'<th style="width:{w}">{h}</th>' if w else f"<th>{h}</th>" for h, w in headers)
    first = first or []
    body = "".join("<tr>" + (f"<td>{first[i]}</td>" if i < len(first) else "<td></td>") + "<td></td>" * (len(headers) - 1)
                   + "</tr>" for i in range(n))
    return f'<table class="{cls}"><tr>{head}</tr>{body}</table>'


def _box(label: str, h: int = 28) -> str:
    return f'<div class="box"><div class="lbl">{label}</div><div style="height:{h}px"></div></div>'


NOTAS = '<h3>Notas</h3><div class="lines"></div>'


def _checks(items: list[str], h: int = 26, col: str = "Hecho") -> str:
    rows = "".join(f'<tr><td class="c"><span class="cb"></span></td><td>{x}</td><td></td></tr>' for x in items)
    return f'<table class="t{h}"><tr><th style="width:6%"></th><th>Paso</th><th style="width:16%">{col}</th></tr>{rows}</table>'


AVISO = ("Contenido educativo, no es asesoría financiera, fiscal ni legal. Pensado para quien vive en Estados Unidos. "
         "Hecho por Dinero Simple con ayuda de herramientas de IA para el borrador y el diseño; revisado por una persona.")

# ---------------------------------------------------------------- El Presupuesto Familiar (12 páginas)


def pf_start() -> str:
    return P("Empieza <em>aquí</em>", "El Presupuesto Familiar", f'''
      <p class="big">Un plan de dinero para toda la casa: lo que entra, lo que sale, lo que siempre llega aunque no sea
      cada mes, y un número semanal para gastar sin culpa.</p>
      <h3>Hazlo así (una hora la primera vez, en familia)</h3>
      <ol class="steps big">
        <li>Anota todo lo que entra en casa, de cada persona (página 2).</li>
        <li>Anota los gastos fijos del mes y el día en que se pagan (página 3).</li>
        <li>Llena los fondos para lo que siempre llega: regreso a clases, diciembre, documentos, el viaje (página 4).</li>
        <li>Saca tu número de la semana (página 5). Ese número es lo que se puede gastar en todo lo demás.</li>
        <li>Cada mes: presupuesto (página 6), semanas (página 7) y una junta familiar de 20 minutos (página 11).</li>
      </ol>
      <h3>Para imprimir</h3>
      <p>Imprime al 100% (tamaño real) en carta o A4. Las páginas 6, 7 y 12 son para cada mes: imprímelas las veces que quieras.</p>
      <div class="box fineprint" style="margin-top:auto">{AVISO}</div>''', kicker="Dinero Simple")


def pf_ingresos() -> str:
    return P("Lo que <em>entra en casa</em>", "Cada persona, cada mes", f'''
      <p>Anota lo que llega a tu cuenta (después de impuestos), no lo que dice el contrato. Si te pagan cada semana,
      multiplica por 4.33 para sacar el mes; si te pagan cada dos semanas, por 2.17.</p>
      {_tbl([("Quién", "20%"), ("De dónde (trabajo, negocio, otro)", "32%"), ("Cada cuánto", "16%"), ("Cuánto llega", "16%"), ("Al mes", "")], 7, "t28")}
      <h3>Lo que no llega cada mes</h3>
      <p class="note">Aguinaldo o bono, devolución de impuestos, horas extra, trabajos de temporada. No cuentes con ello
      para los gastos del mes: mándalo a tus fondos o a tus deudas.</p>
      {_tbl([("Qué", "40%"), ("Cuándo llega", "25%"), ("Más o menos cuánto", "")], 4, "t28")}
      <div class="g3" style="margin-top:auto">{_box("Total al mes (todos)")}{_box("El mes más bajo del año")}{_box("Usamos para el plan")}</div>''')


GASTOS_FIJOS = ["Renta o hipoteca", "Luz", "Gas", "Agua y basura", "Teléfonos", "Internet", "Pago del carro",
                "Seguro del carro", "Gasolina y transporte", "Guardería o escuela", "Envío a la familia", "Seguro médico"]


def pf_fijos() -> str:
    return P("Gastos <em>fijos</em>", "Lo que sale cada mes sí o sí", f'''
      {_tbl([("Gasto", "34%"), ("Día que se paga", "16%"), ("Cuánto", "15%"), ("¿Automático?", "15%"), ("Notas", "")], 18, "t26", GASTOS_FIJOS)}
      <p class="note" style="margin-top:6px">El envío a la familia va aquí si lo mandas cada mes: es un gasto fijo,
      no un extra. Si cambia, usa un promedio de los últimos tres meses.</p>
      <div class="g3" style="margin-top:auto">{_box("Total de gastos fijos")}{_box("De esto, ¿qué se puede bajar?")}{_box("Revisar otra vez el")}</div>''')


FONDOS = ["Regreso a clases", "Diciembre: regalos, posadas, Reyes", "Viaje para ver a la familia", "Documentos, pasaportes y licencias",
          "Reparaciones del carro", "Cumpleaños, bodas y quinceañeras", "Ropa y zapatos de los niños", "Médico, dentista y lentes"]


def pf_fondos() -> str:
    return P("Fondos para lo que <em>siempre llega</em>", "Un poco cada mes", f'''
      <p class="big">Estos gastos no son sorpresa: llegan cada año. Si guardas un poco cada mes, cuando llegan ya está el dinero.</p>
      <table class="t30"><tr><th style="width:34%">Para qué</th><th style="width:15%">Cuánto cuesta</th><th style="width:15%">Para cuándo</th>
      <th style="width:12%">Meses que faltan</th><th style="width:12%">Al mes</th><th>Ya tenemos</th></tr>
      {"".join(f"<tr><td>{f}</td><td></td><td></td><td></td><td></td><td></td></tr>" for f in FONDOS)}
      <tr><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td><td></td></tr>
      <tr class="tot"><td>Total al mes</td><td></td><td></td><td></td><td></td><td></td></tr></table>
      <div class="box" style="margin-top:12px"><b>Cómo se saca "al mes":</b> cuánto cuesta ÷ meses que faltan. Ejemplo:
      el regreso a clases cuesta $480 y faltan 8 meses, así que guardas $60 al mes.</div>
      <p class="note" style="margin-top:8px">Un truco que funciona: una cuenta de ahorro aparte solo para los fondos, con
      una transferencia automática el día que te pagan.</p>''')


def pf_numero() -> str:
    rows = [("Lo que entra al mes (página 2)", "+"), ("Gastos fijos (página 3)", "&minus;"), ("Fondos (página 4)", "&minus;"),
            ("Ahorro de emergencia", "&minus;"), ("Pago extra a deudas (página 9)", "&minus;"), ("Queda para el mes", "=")]
    tr = "".join(f'<tr{" class=tot" if s == "=" else ""}><td style="width:8%;text-align:center;font-weight:900">{s}</td><td>{a}</td>'
                 f'<td style="width:28%"></td></tr>' for a, s in rows)
    return P("Tu número <em>de la semana</em>", "El que manda", f'''
      <p class="big">Lo que queda después de lo fijo, los fondos y el ahorro es para todo lo demás: comida, salidas,
      gasolina extra, antojos. Divídelo entre 4.33 y tienes tu número de la semana.</p>
      <table class="t34">{tr}</table>
      <div class="g2" style="margin-top:14px">
        <div class="box" style="background:var(--ink);color:var(--cream);border-color:var(--ink)"><div class="lbl" style="color:var(--gold)">Queda para el mes ÷ 4.33</div>
          <div style="height:60px"></div><div style="font-size:16pt;font-weight:900">= nuestro número de la semana</div></div>
        <div class="box"><div class="lbl">¿Qué entra en el número?</div>
          <ul style="margin:6px 0 0 16px;padding:0;line-height:1.6"><li>Comida y súper</li><li>Comer fuera</li><li>Gasolina del día a día</li>
          <li>Cosas de la casa</li><li>Gustos y salidas</li></ul></div>
      </div>
      <h3>Si el número sale negativo o muy chico</h3>
      <ol class="steps"><li>Baja primero los fondos (más meses, o menos dinero), no el ahorro de emergencia.</li>
      <li>Revisa los gastos fijos que se pueden bajar: teléfonos, internet, seguros, suscripciones.</li>
      <li>Busca un ingreso extra por unos meses y mándalo todo al plan.</li></ol>''')


CATEGORIAS = ["Renta o hipoteca", "Servicios (luz, gas, agua)", "Teléfonos e internet", "Carro y transporte", "Comida y súper",
              "Comer fuera", "Niños y escuela", "Envío a la familia", "Salud", "Deudas", "Fondos", "Ahorro", "Gustos y salidas", "Otros"]


def pf_mes() -> str:
    return P("Presupuesto <em>del mes</em>", "Mes: ____________", f'''
      <div class="g4">{_box("Entra este mes", 22)}{_box("Planeado", 22)}{_box("Gastado", 22)}{_box("Diferencia", 22)}</div>
      <table class="t28" style="margin-top:10px"><tr><th style="width:36%">Categoría</th><th style="width:16%">Plan</th><th style="width:16%">Real</th>
      <th style="width:16%">Diferencia</th><th>Nota</th></tr>
      {"".join(f"<tr><td>{c}</td><td></td><td></td><td></td><td></td></tr>" for c in CATEGORIAS)}
      <tr class="tot"><td>Total</td><td></td><td></td><td></td><td></td></tr></table>''')


def pf_semanas() -> str:
    sem = "".join(f'''<div class="box"><div class="lbl">Semana {i}</div>
      <table class="t26" style="margin-top:4px"><tr><th>Fecha</th><th>En qué</th><th style="width:24%">Cuánto</th></tr>
      {"<tr><td></td><td></td><td></td></tr>" * 6}<tr class="tot"><td colspan="2">Gastado / queda del número</td><td></td></tr></table></div>'''
                  for i in range(1, 5))
    return P("Las <em>cuatro semanas</em>", "Mes: ____________", f'''
      <div class="g2" style="margin-bottom:10px">{_box("Nuestro número de la semana", 22)}{_box("Si sobra, va a", 22)}</div>
      <div class="g2" style="gap:10px">{sem}</div>
      <p class="note" style="margin-top:6px">Lo que sobra de una semana no se pasa a la siguiente: va al ahorro o a la deuda. Así el número sigue siendo fácil.</p>''')


def pf_calendario() -> str:
    days = "".join(f"<tr><td class='c'><b>{d}</b></td><td></td><td></td><td class='c'><span class='cb'></span></td></tr>" for d in range(1, 32))
    return P("Calendario <em>de pagos</em>", "Qué se paga y cuándo", f'''
      <table style="font-size:8.5pt"><tr><th style="width:8%">Día</th><th>Qué se paga</th><th style="width:16%">Cuánto</th><th style="width:10%">Pagado</th></tr>{days}</table>''')


def pf_deudas() -> str:
    return P("Plan para <em>las deudas</em>", "Una a la vez", f'''
      <p>Anota cada deuda. Paga el mínimo en todas y todo lo extra a una sola: la de interés más alto (ahorras más) o la de
      saldo más chico (ves avance antes). Cuando termines una, su pago se suma a la siguiente.</p>
      {_tbl([("A quién", "26%"), ("Saldo", "14%"), ("Interés (APR)", "14%"), ("Pago mínimo", "14%"), ("Día de pago", "12%"), ("Orden", "")], 8, "t30")}
      <h3>Avance</h3>
      {_tbl([("Mes", "16%"), ("Pagamos extra a", "34%"), ("Cuánto extra", "16%"), ("Saldo total que queda", "")], 12, "t26")}
      <p class="note" style="margin-top:6px">Si una deuda ya está en cobranza o te están llamando, pide todo por escrito
      antes de pagar. Nunca pagues con tarjetas de regalo.</p>{NOTAS}''')


def pf_metas() -> str:
    meta = "".join(f'''<div class="box" style="margin-bottom:10px"><div class="g4" style="grid-template-columns:2fr 1fr 1fr 1fr">
      <div><div class="lbl">Meta {i}</div><div class="line"></div></div><div><div class="lbl">Cuánto</div><div class="line"></div></div>
      <div><div class="lbl">Para cuándo</div><div class="line"></div></div><div><div class="lbl">Cada semana</div><div class="line"></div></div></div>
      <div style="display:grid;grid-template-columns:repeat(10,1fr);gap:4px;margin-top:8px">{"<div style='border:1.3px solid var(--ink);height:22px;border-radius:4px'></div>" * 10}</div>
      <div class="fineprint" style="margin-top:3px">Colorea un cuadro por cada 10% que juntes.</div></div>''' for i in range(1, 4))
    return P("Metas <em>de la familia</em>", "Lo que queremos juntos", f'''
      <p class="big">Una meta con fecha y monto es más fácil de cumplir. Escojan tres, como máximo, y pongan primero el colchón para emergencias.</p>
      {meta}
      <div class="box" style="margin-top:auto"><div class="lbl">¿Por qué es importante para nosotros?</div><div class="line"></div><div class="line"></div></div>''')


def pf_junta() -> str:
    return P("Junta familiar <em>de dinero</em>", "20 minutos, una vez al mes", f'''
      <p class="big">No es para regañar a nadie. Es para que todos sepan el plan y nadie cargue solo con las cuentas.</p>
      <ol class="steps big">
        <li><b>Lo bueno (3 min):</b> algo que salió bien con el dinero este mes.</li>
        <li><b>Los números (5 min):</b> cuánto entró, cuánto se gastó y cómo van los fondos y las metas.</li>
        <li><b>Lo que viene (5 min):</b> pagos grandes, cumpleaños, viajes o gastos de la escuela del próximo mes.</li>
        <li><b>Un cambio (5 min):</b> una sola cosa que vamos a hacer distinto.</li>
        <li><b>Los niños (2 min):</b> una pregunta o una tarea de dinero para ellos, según su edad.</li>
      </ol>
      <h3>Lo que acordamos</h3>
      {_tbl([("Fecha", "16%"), ("Acuerdo", "60%"), ("Quién", "")], 7, "t30")}
      <div class="box fineprint" style="margin-top:auto">Idea para los niños: que ellos lleven la cuenta de una meta (por
      ejemplo, el viaje) y coloreen los cuadros de la página 10.</div>''')


def pf_revision() -> str:
    return P("Revisión <em>del mes</em>", "Mes: ____________", f'''
      <div class="g4">{_box("Entró", 24)}{_box("Salió", 24)}{_box("Ahorramos", 24)}{_box("Pagamos de deudas", 24)}</div>
      <h3>¿Cómo nos fue?</h3>
      <div class="g2">
        <div class="box"><div class="lbl">Lo que salió bien</div><div class="line"></div><div class="line"></div><div class="line"></div><div class="line"></div></div>
        <div class="box"><div class="lbl">Dónde se nos fue el dinero</div><div class="line"></div><div class="line"></div><div class="line"></div><div class="line"></div></div>
      </div>
      <h3>Para el próximo mes</h3>
      {_checks(["Actualizamos el número de la semana si cambió lo que entra", "Revisamos los fondos y lo que viene",
                "Movimos lo que sobró al ahorro o a la deuda", "Pusimos la fecha de la próxima junta familiar",
                "Un gasto que vamos a bajar: ______________________"], 30, "Listo")}
      <div class="box" style="margin-top:auto"><div class="lbl">Nota para nosotros</div><div class="line"></div><div class="line"></div></div>''')


def presupuesto_pages() -> list[str]:
    return [pf_start(), pf_ingresos(), pf_fijos(), pf_fondos(), pf_numero(), pf_mes(), pf_semanas(), pf_calendario(),
            pf_deudas(), pf_metas(), pf_junta(), pf_revision()]


# ---------------------------------------------------------------- El Registro de Envíos (7 páginas + hoja de cálculo)

DERECHOS = [
    ("Antes de pagar", "El servicio te tiene que mostrar la comisión, el tipo de cambio y cuánto va a llegar exactamente."),
    ("Recibo", "Te tienen que dar un recibo con esos datos y con la fecha en que llega el dinero."),
    ("30 minutos", "Puedes cancelar en los primeros 30 minutos y te regresan todo, si el dinero no se ha cobrado ni depositado."),
    ("180 días", "Si llegó menos, tarde o a otra persona, tienes 180 días para reportar el error y el servicio tiene que investigar."),
]


def re_start() -> str:
    der = "".join(f'<div class="flag"><b>{a}</b>{b}</div>' for a, b in DERECHOS)
    return P("Empieza <em>aquí</em>", "El Registro de Envíos", f'''
      <p class="big">Lo que importa no es la comisión: es cuánto llega allá. Este registro te ayuda a comparar antes de
      enviar, a guardar cada envío y a saber cuánto pagaste en el año.</p>
      <h3>Cómo comparar en 1 minuto</h3>
      <ol class="steps"><li>Pide a dos o tres servicios una cotización para el mismo monto (página 2).</li>
      <li>Fíjate en "cuánto llega", no solo en la comisión. Un tipo de cambio bajo puede costar más que una comisión alta.</li>
      <li>Anota el envío (páginas 4 y 5) con el número de confirmación.</li></ol>
      <h3>Tus derechos en EE. UU. (Regla de Transferencias de Remesas)</h3>{der}
      <p class="note">¿Un problema que el servicio no resuelve? Puedes quejarte con la CFPB en consumerfinance.gov o al 855-411-2372.
      Desde 2026 hay un impuesto federal del 1% en envíos pagados en efectivo, giro postal o cheque de caja; pagando desde
      tu cuenta de banco o con tarjeta no aplica. Verifica con tu servicio.</p>
      <div class="box fineprint" style="margin-top:auto">{AVISO} No recomendamos ningún servicio en particular.</div>''',
             kicker="Dinero Simple")


def re_comparar() -> str:
    cot = "".join(f'''<tr><td><b>Servicio {c}</b><div class="line"></div></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>''' for c in "ABC")
    return P("Comparar <em>antes de enviar</em>", "Mismo monto, tres servicios", f'''
      <div class="g3">{_box("Monto a enviar (USD)", 22)}{_box("Fecha", 22)}{_box("Tipo de cambio de referencia hoy", 22)}</div>
      <table class="t34" style="margin-top:10px"><tr><th style="width:24%">Servicio</th><th>Comisión</th><th>Tipo de cambio</th>
      <th>Llega allá</th><th>Total que pagas</th><th>Cuándo llega</th><th>Cómo se recoge</th></tr>{cot}</table>
      <div class="box" style="margin-top:12px"><b>El costo escondido.</b> Tipo de cambio de referencia × monto, menos lo que
      llega, es lo que te cobran en el cambio. Ejemplo: envías $300; la referencia es 18.00, así que serían 5,400 pesos.
      Si llegan 5,250, el cambio te costó 150 pesos, unos $8.33, además de la comisión.</div>
      <h3>Para elegir</h3>
      {_checks(["Gana el que deja más dinero allá, después de todo", "¿Llega a tiempo? ¿Se puede recoger cerca o depositar en cuenta?",
                "¿Pagas desde tu cuenta o tarjeta? (en efectivo hay un impuesto del 1% desde 2026)",
                "¿El servicio tiene licencia en tu estado? Búscalo en el sitio del regulador de tu estado"], 28, "Sí")}{NOTAS}''')


def re_quienes() -> str:
    return P("A quién <em>le envío</em>", "Datos para no equivocarte", f'''
      <p>Un nombre mal escrito puede detener un envío. Copia los datos tal como aparecen en la identificación de quien recibe.</p>
      {_tbl([("Nombre completo (como en su ID)", "30%"), ("País y ciudad", "18%"), ("Cómo recibe", "18%"), ("Banco o lugar de pago", "18%"), ("Teléfono", "")], 8, "t34")}
      <div class="box" style="margin-top:12px"><b>Cuidado.</b> Nunca envíes dinero a alguien que no conoces en persona,
      aunque diga que es familiar, que ganaste algo o que es "para arreglar tus papeles". Si te piden un envío urgente,
      cuelga y llama tú a esa persona a un número que ya tenías.</div>{NOTAS}''')


def re_log(part: int) -> str:
    return P("Registro <em>de envíos</em>", f"Hoja {part} de 2", f'''
      {_tbl([("Fecha", "10%"), ("A quién", "17%"), ("Servicio", "14%"), ("Enviaste USD", "11%"), ("Comisión", "9%"),
             ("Tipo de cambio", "10%"), ("Llegó", "11%"), ("Confirmación #", "")], 22, "t30")}
      <p class="note" style="margin-top:6px">Guarda el recibo (una foto sirve) hasta que confirmen que llegó. Si algo sale mal, tienes 180 días para reportarlo.</p>''')


def re_resumen() -> str:
    return P("Resumen <em>del año</em>", "Año: ________", f'''
      <table class="t28"><tr><th style="width:18%">Mes</th><th>Envíos</th><th>Total enviado</th><th>Comisiones</th><th>Total que llegó</th><th>Servicio más usado</th></tr>
      {"".join(f"<tr><td>{m}</td><td></td><td></td><td></td><td></td><td></td></tr>" for m in MESES)}
      <tr class="tot"><td>Año</td><td></td><td></td><td></td><td></td><td></td></tr></table>
      <div class="g3" style="margin-top:12px">{_box("Pagamos en comisiones este año")}{_box("Si hubiéramos usado el más barato")}{_box("Meta para el próximo año")}</div>
      <p class="note" style="margin-top:8px">Mandar una vez al mes en lugar de cada semana suele costar menos en comisiones, si a tu familia le funciona.</p>''')


def re_estafas() -> str:
    flags = [("Te piden un envío urgente", "Un \"familiar\" en problemas, una fianza, un accidente. Cuelga y llama tú a un número que ya tenías."),
             ("Te ofrecen un trámite migratorio", "Nadie puede \"arreglar papeles\" por un envío. Los notarios en EE. UU. no son abogados."),
             ("Ganaste algo, pero tienes que pagar", "Si tienes que pagar para cobrar un premio, no es un premio."),
             ("Te piden recibir y reenviar dinero", "Si alguien te manda dinero para que lo reenvíes, te pueden usar como \"mula\". Es delito."),
             ("Alguien que conociste en línea", "Si nunca lo has visto en persona y te pide dinero, es una estafa casi siempre.")]
    items = "".join(f'<div class="flag"><b>{a}</b>{b}</div>' for a, b in flags)
    return P("Cuidado con <em>las estafas</em>", "Antes de cualquier envío", f'''
      <p class="big">El dinero enviado casi nunca se puede recuperar. Si ves una de estas señales, para y pregunta a alguien de confianza.</p>{items}
      <div class="box" style="margin-top:auto;background:var(--ink);color:var(--cream);border-color:var(--ink)">
        <div class="kick" style="color:var(--gold)">Si ya enviaste</div>
        <div style="margin-top:4px">Llama al servicio de inmediato (si fue en los últimos 30 minutos, puedes cancelar) y
        reporta la estafa en ReportFraud.ftc.gov (también en español).</div></div>''')


def remesas_pages() -> list[str]:
    return [re_start(), re_comparar(), re_quienes(), re_log(1), re_log(2), re_resumen(), re_estafas()]


# ---------------------------------------------------------------- La Lista para Construir tu Crédito (8 páginas)


def cr_start() -> str:
    return P("Empieza <em>aquí</em>", "Construye tu crédito", f'''
      <p class="big">Tu crédito es tu historial de pagos. Sin historial, rentar, comprar un carro o tener un buen seguro
      cuesta más. La buena noticia: se construye con pasos pequeños y aburridos, mes a mes.</p>
      <h3>Lo que más cuenta en tu puntaje</h3>
      <table class="t28"><tr><th style="width:36%">Factor</th><th>Qué significa para ti</th></tr>
        <tr><td><b>Pagar a tiempo</b></td><td>Lo más importante. Un pago con 30 días de atraso te puede bajar mucho.</td></tr>
        <tr><td><b>Cuánto usas</b></td><td>Usa menos del 30% de tu límite, y mejor menos del 10%.</td></tr>
        <tr><td><b>Tiempo</b></td><td>Entre más años de historial, mejor. No cierres tu primera tarjeta.</td></tr>
        <tr><td><b>Solicitudes nuevas</b></td><td>Pide crédito solo cuando lo necesites.</td></tr>
        <tr><td><b>Tipos de crédito</b></td><td>Tarjetas y préstamos juntos ayudan un poco, pero no saques deudas por esto.</td></tr></table>
      <h3>Sin número de Seguro Social</h3>
      <p>Con un ITIN también se puede: varios bancos y cooperativas de crédito abren cuentas y tarjetas aseguradas con ITIN.
      Pregunta directamente antes de solicitar, porque cada lugar tiene sus reglas.</p>
      <div class="box fineprint" style="margin-top:auto">{AVISO}</div>''', kicker="Dinero Simple")


def cr_punto() -> str:
    return P("Tu punto <em>de partida</em>", "Antes del primer paso", f'''
      {_checks(["Tengo una cuenta de banco o de cooperativa a mi nombre",
                "Sé si voy a usar mi Seguro Social o mi ITIN",
                "Pedí mis reportes gratis en AnnualCreditReport.com (los tres burós, cada semana, gratis)",
                "Revisé que no haya cuentas que no reconozco",
                "Sé cuánto puedo pagar cada mes sin problema: $______",
                "Puse mis pagos en automático o con recordatorio",
                "Tengo un colchón chiquito para emergencias, aunque sea de $500"], 32)}
      <div class="g3" style="margin-top:14px">{_box("Equifax", 40)}{_box("Experian", 40)}{_box("TransUnion", 40)}</div>
      <p class="note" style="margin-top:4px">Anota en cada cuadro la fecha en que revisaste el reporte y si encontraste algo raro.</p>{NOTAS}''')


def cr_12() -> str:
    pasos = [("Mes 1", "Abre una tarjeta asegurada o un préstamo para construir crédito (página 8). Lee las comisiones antes."),
             ("Mes 1", "Pon un solo cargo chico que ya pagas (por ejemplo, el teléfono) y el pago automático del saldo completo."),
             ("Mes 2", "Revisa que el pago llegó y que la cuenta aparece en tu reporte."),
             ("Mes 3", "Revisa tus tres reportes. Anota cualquier error (página 6)."),
             ("Mes 4", "Si rentas, pregunta si tu arrendador o una app puede reportar tus pagos de renta."),
             ("Mes 6", "Mira tu puntaje (muchos bancos lo dan gratis). No pidas otra tarjeta solo por curiosidad."),
             ("Mes 9", "Sigue igual: un cargo chico, pagado completo y a tiempo. Lo aburrido es lo que funciona."),
             ("Mes 12", "Pregunta si tu tarjeta asegurada puede pasar a normal y regresarte el depósito."),
             ("Mes 12", "Revisa tus reportes otra vez y llena el registro del año (página 5).")]
    rows = "".join(f'<tr><td class="c"><span class="cb"></span></td><td><b>{m}</b></td><td>{t}</td><td></td></tr>' for m, t in pasos)
    return P("Los primeros <em>12 meses</em>", "Paso a paso", f'''
      <table class="t34"><tr><th style="width:6%"></th><th style="width:12%">Cuándo</th><th>Paso</th><th style="width:14%">Hecho</th></tr>{rows}</table>
      {NOTAS}<div class="box" style="margin-top:10px"><b>La regla que no se rompe:</b> paga el saldo completo cada mes y a tiempo.
      No hace falta dejar saldo ni pagar intereses para construir crédito.</div>''')


def cr_reglas() -> str:
    reglas = [("Siempre a tiempo", "Pago automático por lo menos del mínimo, y paga el resto antes de la fecha límite."),
              ("Menos del 30%", "Con un límite de $500, procura que el saldo al cierre sea menor de $150 (mejor menos de $50)."),
              ("No cierres la primera", "Tu tarjeta más vieja le da años a tu historial. Si no tiene cuota anual, déjala abierta."),
              ("Pocas solicitudes", "Cada solicitud deja una marca. Espera unos seis meses entre una y otra."),
              ("Revisa tus reportes", "Gratis cada semana en AnnualCreditReport.com. Un error se puede disputar sin pagar a nadie.")]
    items = "".join(f'<div class="flag"><b>{i}. {a}</b>{b}</div>' for i, (a, b) in enumerate(reglas, 1))
    return P("Las <em>cinco reglas</em>", "Para pegarlas en el refri", f'''{items}
      <div class="box" style="margin-top:auto;background:var(--ink);color:var(--cream);border-color:var(--ink)">
        <div class="kick" style="color:var(--gold)">Si un mes no puedes pagar</div>
        <div style="margin-top:4px">Paga por lo menos el mínimo y llama al banco antes de la fecha límite. Un pago mínimo
        a tiempo es mucho mejor que un pago atrasado.</div></div>''', kicker="Dinero Simple")


def cr_registro() -> str:
    return P("Registro <em>mensual</em>", "Un renglón por mes", f'''
      <table class="t30"><tr><th style="width:14%">Mes</th><th style="width:18%">Tarjeta</th><th>Límite</th><th>Saldo al cierre</th>
      <th>% de uso</th><th>Pagado completo</th><th>A tiempo</th></tr>
      {"".join(f"<tr><td>{m}</td><td></td><td></td><td></td><td></td><td class='c'><span class='cb'></span></td><td class='c'><span class='cb'></span></td></tr>" for m in MESES)}</table>
      <p class="note" style="margin-top:6px">% de uso = saldo al cierre ÷ límite × 100. Ejemplo: $40 ÷ $500 × 100 = 8%.</p>
      <div class="g3" style="margin-top:auto">{_box("Puntaje al empezar")}{_box("Puntaje a los 6 meses")}{_box("Puntaje a los 12 meses")}</div>''')


def cr_reporte() -> str:
    return P("Revisa <em>tu reporte</em>", "Y corrige los errores", f'''
      {_checks(["Tu nombre, dirección y fechas están bien", "Todas las cuentas son tuyas",
                "Los pagos que hiciste a tiempo no aparecen como atrasados", "No hay deudas que ya pagaste marcadas como abiertas",
                "No hay solicitudes de crédito que tú no hiciste"], 28, "Revisado")}
      <h3>Registro de disputas</h3>
      {_tbl([("Fecha", "12%"), ("Buró", "14%"), ("El error", "34%"), ("Cómo lo envié", "16%"), ("Respuesta", "")], 6, "t30")}
      <p class="note" style="margin-top:6px">Disputar es gratis: en línea en el sitio de cada buró o por correo, con copia de
      tus pruebas. Normalmente tienen unos 30 días para investigar. Si alguien abrió algo a tu nombre, ve a IdentityTheft.gov
      y congela tu crédito (gratis) en los tres burós.</p>{NOTAS}''')


def cr_cuidado() -> str:
    flags = [("Te cobran antes de hacer el trabajo", "Por ley, una empresa de \"reparación de crédito\" no te puede cobrar antes de terminar el servicio."),
             ("Te venden un \"número de crédito nuevo\" (CPN)", "Es una estafa. Usar un número que no es tuyo para pedir crédito puede ser un delito."),
             ("Te prometen borrar todo lo negativo", "Nadie puede borrar información correcta. Los errores los puedes disputar tú gratis."),
             ("Te dicen que no hables con los burós", "Tienes derecho a hablar con ellos y a ver tus reportes cuando quieras.")]
    items = "".join(f'<div class="flag"><b>{a}</b>{b}</div>' for a, b in flags)
    return P("Cuidado con <em>las promesas</em>", "Lo que nadie puede hacer por ti", f'''{items}
      <h3>Ayuda que sí existe</h3>
      <p>Las agencias de asesoría crediticia sin fines de lucro (búscalas en nfcc.org, también en español) te ayudan con un
      plan de deudas por poco o nada. Para quejas, la CFPB: consumerfinance.gov o 855-411-2372.</p>
      {NOTAS}<div class="box fineprint" style="margin-top:10px">{AVISO}</div>''')


def cr_opciones() -> str:
    rows = [("Tarjeta asegurada", "Dejas un depósito (por ejemplo $200) y ese es tu límite.", "Depósito; revisa la cuota anual.", "Que reporte a los tres burós."),
            ("Préstamo para construir crédito", "Pagas un préstamo chico cada mes y al final te dan el dinero.", "Intereses o comisión chicos.", "Que el pago te quede cómodo."),
            ("Usuario autorizado", "Alguien de confianza te agrega a su tarjeta.", "Nada.", "Si esa persona paga tarde, te afecta a ti."),
            ("Reporte de renta", "Tus pagos de renta se reportan a uno o más burós.", "Puede tener costo.", "Pregunta a qué burós reporta."),
            ("Tarjeta de tienda", "Fácil de conseguir, pero el interés suele ser alto.", "Interés alto si dejas saldo.", "Mejor después de la asegurada.")]
    tr = "".join(f"<tr><td class='wrap'><b>{a}</b></td><td class='wrap'>{b}</td><td class='wrap'>{c}</td><td class='wrap'>{d}</td></tr>" for a, b, c, d in rows)
    return P("Opciones <em>para empezar</em>", "Escoge una o dos", f'''
      <table><tr><th style="width:20%">Opción</th><th style="width:34%">Cómo funciona</th><th style="width:20%">Costo</th><th>Cuidado con</th></tr>{tr}</table>
      <h3>La que escogí</h3>
      <div class="g3">{_box("Opción y lugar", 30)}{_box("Fecha en que la abrí", 30)}{_box("Comisiones que leí", 30)}</div>
      <p class="note" style="margin-top:8px">No necesitas todas. Para la mayoría, una tarjeta asegurada usada con un cargo
      chico y pagada completa cada mes es suficiente para empezar.</p>{NOTAS}''')


def credito_pages() -> list[str]:
    return [cr_start(), cr_punto(), cr_12(), cr_reglas(), cr_registro(), cr_reporte(), cr_cuidado(), cr_opciones()]


# ---------------------------------------------------------------- listings

BUENO = ["Es una DESCARGA DIGITAL. No se envía nada. Tus archivos aparecen en tu cuenta de Etsy (Compras y reseñas) justo después de pagar.",
         "PDF en tamaño carta (US Letter) y A4. Imprime en casa o en una imprenta las veces que quieras para uso personal.",
         "Todo está en español.",
         "Solo para uso personal. Por favor, no revendas, compartas ni redistribuyas los archivos.",
         "Contenido educativo, no es asesoría financiera, fiscal ni legal. Pensado para quien vive en Estados Unidos."]
DISCLOSURE = ("Cómo se hizo: diseñado por Dinero Simple. Herramientas de IA ayudaron con el borrador y el diseño; "
              "una persona revisó cada página y los datos con fuentes oficiales.")
CAT = "Paper & Party Supplies > Paper > Calendars & Planners"
CAT_SHEET = "Paper & Party Supplies > Paper > Calendars & Planners (Etsy may suggest Digital templates)"


def _desc(hook: str, get: list[str], how: list[str], extra: list[str] | None = None) -> str:
    g = "\n".join(f"- {x}" for x in get)
    h = "\n".join(f"{i}. {x}" for i, x in enumerate(how, start=1))
    b = "\n".join(f"- {x}" for x in BUENO + (extra or []))
    return (f"{hook}\n\nQUÉ INCLUYE\n{g}\n\nCÓMO FUNCIONA\n{h}\n\nBUENO SABER\n{b}\n- {DISCLOSURE}\n\n"
            "MÁS EN LA TIENDA\nBusca \"Dinero Simple\" en Etsy para los otros kits en español.")


def _gumroad(hook: str, get: list[str], price: float, files: str) -> str:
    g = "\n".join(f"- {x}" for x in get)
    return (f"{hook}\n\nQué incluye:\n{g}\n\nDescarga inmediata: {files}. ${price:g}, un solo pago, los archivos son tuyos.\n\n"
            "Contenido educativo, no es asesoría financiera, fiscal ni legal. Hecho con ayuda de herramientas de IA para el "
            "borrador y el diseño, y revisado por una persona. ¿Una pregunta o un problema con un archivo? Responde al correo de tu compra.")


PF_GET = ["12 páginas: lo que entra en casa, gastos fijos, fondos para lo que siempre llega, tu número de la semana",
          "Presupuesto del mes, las cuatro semanas, calendario de pagos, plan para las deudas y metas de la familia",
          "Una junta familiar de dinero de 20 minutos y la revisión del mes"]
RE_GET = ["7 páginas para imprimir: comparar antes de enviar, a quién le envío, registro de envíos, resumen del año y señales de estafa",
          "Tus derechos al enviar dinero desde EE. UU., explicados en sencillo",
          "Hoja de cálculo (.xlsx para Google Sheets y Excel) que calcula lo que llega, el costo escondido en el tipo de cambio y tus totales por mes y por servicio"]
CR_GET = ["8 páginas: lo que cuenta en tu puntaje, tu punto de partida, los primeros 12 meses paso a paso y las cinco reglas",
          "Registro mensual de uso de tus tarjetas, revisión de tu reporte con registro de disputas",
          "Cuidado con las promesas (CPN y \"reparación de crédito\") y las opciones para empezar, también con ITIN"]

LISTINGS = [
    dict(slug="presupuesto-familiar", name="El Presupuesto Familiar", price=9.00, kind="print", category=CAT,
         title="Presupuesto Familiar en Español Imprimible, Spanish Budget Planner, Gastos, Ahorro y Metas",
         tags=["presupuesto mensual", "spanish budget", "en espanol", "presupuesto familiar", "spanish planner",
               "finanzas personales", "budget printable", "control de gastos", "plan de ahorro", "planificador dinero",
               "family budget", "metas de ahorro", "hispanic gift"],
         attributes={"Occasion": "None", "Holiday": "None", "Paper size": "US Letter, A4", "File type": "PDF",
                     "Primary colour": "Blue", "Secondary colour": "Orange"},
         hook="Un plan de dinero para toda la casa, en español: lo que entra, lo que sale, lo que siempre llega aunque no sea cada mes, y un número semanal para gastar sin culpa."),
    dict(slug="registro-de-envios", name="El Registro de Envíos", price=7.00, kind="print+sheet", category=CAT_SHEET,
         title="Registro de Envios de Dinero en Español, Remittance Tracker Printable y Google Sheets",
         tags=["remesas familiares", "envios de dinero", "remittance tracker", "en espanol", "spanish planner",
               "money transfer", "finanzas personales", "google sheets", "hoja de calculo", "spanish budget",
               "registro de gastos", "dinero para familia", "hispanic gift"],
         attributes={"Occasion": "None", "Holiday": "None", "Paper size": "US Letter, A4", "File type": "PDF, XLSX",
                     "Primary colour": "Blue", "Secondary colour": "Orange"},
         hook="Lo que importa al enviar dinero no es la comisión: es cuánto llega allá. Compara antes de enviar, guarda cada envío y sabe cuánto pagaste en el año."),
    dict(slug="construir-credito", name="La Lista para Construir tu Crédito", price=6.00, kind="print", category=CAT,
         title="Lista para Construir tu Crédito en Español, Credit Building Checklist, Spanish Printable",
         tags=["historial crediticio", "construir credito", "credit building", "en espanol", "spanish planner",
               "puntaje de credito", "credit score", "finanzas personales", "credito con itin", "tarjeta asegurada",
               "spanish budget", "credit tracker", "hispanic gift"],
         attributes={"Occasion": "None", "Holiday": "None", "Paper size": "US Letter, A4", "File type": "PDF",
                     "Primary colour": "Blue", "Secondary colour": "Orange"},
         hook="Construir crédito es aburrido y funciona: pasos pequeños, mes a mes. Esta lista te dice qué hacer en tus primeros 12 meses, también si tienes ITIN."),
    dict(slug="paquete-familia", name="El Paquete de la Familia", price=16.00, kind="bundle", category=CAT,
         title="Paquete de Finanzas Familiares en Español, Presupuesto, Remesas y Crédito, Spanish Budget Bundle",
         tags=["spanish budget", "presupuesto mensual", "en espanol", "remesas familiares", "construir credito",
               "spanish planner", "finanzas personales", "budget bundle", "presupuesto familiar", "plan de ahorro",
               "control de gastos", "planificador dinero", "hispanic gift"],
         attributes={"Occasion": "None", "Holiday": "None", "Paper size": "US Letter, A4", "File type": "PDF, XLSX",
                     "Primary colour": "Blue", "Secondary colour": "Orange"},
         hook="Los tres en una descarga: El Presupuesto Familiar, El Registro de Envíos con su hoja de cálculo y La Lista para Construir tu Crédito, por menos que comprarlos aparte ($22)."),
]

_GET = {"presupuesto-familiar": PF_GET, "registro-de-envios": RE_GET, "construir-credito": CR_GET,
        "paquete-familia": PF_GET[:1] + RE_GET[::2] + CR_GET[:1]}
_HOW = {"print": ["Imprime las páginas que necesitas (carta o A4), o escribe en ellas desde una app de PDF.",
                  "Llénalas una vez, en familia.", "Repite las páginas del mes cada mes."],
        "print+sheet": ["Imprime las páginas o abre la hoja de cálculo en Google Sheets (gratis) o Excel.",
                        "Antes de enviar, compara dos o tres servicios.", "Anota cada envío; los totales se calculan solos."],
        "bundle": ["Descomprime el archivo.", "Empieza por El Presupuesto Familiar.", "Usa el registro en cada envío y la lista de crédito mes a mes."]}
_EXTRA = {"print+sheet": ["La hoja de cálculo es un archivo .xlsx que abre en Google Sheets (súbelo a Google Drive), Excel y Numbers. Las celdas amarillas son las que llenas tú."],
          "bundle": ["La hoja de cálculo es un archivo .xlsx que abre en Google Sheets (súbelo a Google Drive), Excel y Numbers."]}
_FILES = {"print": "PDF en carta y A4", "print+sheet": "PDF en carta y A4, y un archivo .xlsx",
          "bundle": "un .zip con los PDF en carta y A4 y la hoja de cálculo"}
for _it in LISTINGS:
    _it["description"] = _desc(__import__("shop").opener(_it, "es") + " " + _it["hook"], _GET[_it["slug"]], _HOW[_it["kind"]], _EXTRA.get(_it["kind"]))
    _it["gumroad"] = _gumroad(_it["hook"], _GET[_it["slug"]], _it["price"], _FILES[_it["kind"]])
    _it["review"] = "pending native review"
