"""Build "Tu primer año en Estados Unidos: cuaderno de dinero", a printable Spanish workbook for recent arrivals
(the companion product to month 9's "Tu primer año" series). Sold on Gumroad only: Etsy has banned AI-generated
functional guides since Oct 22 2026, and this workbook has instructions written with AI help.

    python3 launch/dinero-simple/primer-ano/build_cuaderno.py          # dist/*.html + GUMROAD.md + review checklist
    python3 launch/dinero-simple/primer-ano/build_cuaderno.py --pdf    # also dist/*.pdf (Chromium via Playwright)

Outputs:
  launch/dinero-simple/primer-ano/GUMROAD.md               the Gumroad listing (price is [PRICE] until Dhruv sets it)
  launch/dinero-simple/REVIEW_CHECKLIST_PRIMER_ANO.md      native-speaker, attorney and fact sign-off (committed)
  dist/Cuaderno-Tu-Primer-Ano.pdf                          the workbook (Letter, print at 100%)

Edit the content in this file (PAGES and the constants), never the PDF. Layout reuses ../mayores/shared.css so all
Dinero Simple printables look like one family. Every name and number in the examples is made up.
"""
from __future__ import annotations

import html
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
DIST = HERE / "dist"
SHARED_CSS = (DS / "mayores" / "shared.css").read_text()
esc = html.escape

TITLE = "Tu primer año en Estados Unidos"
SUBTITLE = "Cuaderno de dinero para quien acaba de llegar: lo que hay que hacer, mes por mes, y dónde anotarlo."
PRICE = "[PRICE]"
VERSION = "noviembre de 2026"
ATTORNEY_LINE = ("Para cualquier pregunta sobre tu situación migratoria, habla con un abogado de inmigración con "
                 "licencia o un representante acreditado por el Departamento de Justicia, nunca con un notario.")
DISCLAIMER = ("Información general, no es asesoría financiera, legal ni de impuestos. Las reglas cambian por estado y "
              "ciudad. Todos los nombres y números de ejemplo son inventados. Redactado con ayuda de herramientas de IA "
              "y revisado por una persona.")

CSS = """
  html,body{font-size:12.6pt;line-height:1.45}
  .page{padding:0.65in 0.7in 0.85in}
  h2{font-size:27pt;margin:0 0 10px} h3{font-size:14.5pt;margin:18px 0 6px} .kicker{font-size:9.5pt} .lede{font-size:13pt}
  .check li{margin-bottom:9px} .check li::before{width:15px;height:15px;top:4px}
  .box{font-size:12pt} .folio{font-size:9pt}
  table{width:100%;border-collapse:collapse;font-size:12pt;margin:8px 0 12px}
  th{background:var(--ink);color:var(--cream);text-align:left;padding:8px 9px;font-size:10.5pt}
  td{border:1px solid var(--line);padding:9px 9px;vertical-align:top} td.b{height:46px}
  .weeks{display:grid;grid-template-columns:repeat(5,1fr);gap:7px;margin:8px 0 12px}
  .weeks div{border:1.6px solid var(--ink);border-radius:8px;height:0.85in;padding:6px 8px;font-size:10.5pt;color:var(--muted)}
  .weeks div b{display:block;color:var(--ink);font-size:12pt}
  .stage{display:grid;grid-template-columns:1.25in 1fr;gap:10px;border-left:4px solid var(--teal);padding:6px 0 6px 12px;margin:0 0 10px}
  .stage b{font-size:11pt}
  .msg{border:1.5px dashed var(--muted);border-radius:10px;padding:10px 14px;font-size:10pt;background:#fff}
  .sum td:first-child{width:62%} .sum tr.t td{font-weight:800;background:var(--tint)}
"""


def page(body: str, n: int | None) -> str:
    folio = f'<div class="folio"><span>Dinero Simple · {esc(TITLE)}</span><span>{n}</span></div>' if n else ""
    return f'<section class="page">{body}{folio}</section>'


def checks(items) -> str:
    return '<ul class="check">' + "".join(f"<li>{esc(x)}</li>" for x in items) + "</ul>"


def table(head, rows: int, first_col=None, widths=None) -> str:
    w = widths or [""] * len(head)
    th = "".join(f'<th style="{f"width:{x}" if x else ""}">{esc(h)}</th>' for h, x in zip(head, w))
    body = ""
    for i in range(rows):
        first = esc(first_col[i]) if first_col and i < len(first_col) else ""
        body += "<tr>" + f'<td class="b">{first}</td>' + "".join("<td></td>" for _ in head[1:]) + "</tr>"
    return f"<table><tr>{th}</tr>{body}</table>"


# --------------------------------------------------------------------------- content
STAGES = [
    ("Mes 1", "Tus papeles a salvo, una cuenta asegurada, un celular sin revisión de crédito y una carpeta para guardarlo todo."),
    ("Meses 2 y 3", "Tu presupuesto real, el precio de verdad (impuesto y propina), los depósitos de la luz y tu colchón de $20 por semana."),
    ("Meses 4 a 6", "Rentar bien: el contrato, las fotos del primer día, cada pago con recibo y las reparaciones por escrito."),
    ("Meses 6 a 12", "Tu historial de crédito, tus impuestos del primer año, ayuda gratis y el plan de tu familia."),
]
MONTH1 = [
    "Guardé los originales (pasaportes, actas, cartas importantes) en una carpeta, en un lugar seco y seguro.",
    "Tomé una foto de cada documento y la guardé en un álbum del celular llamado 'Papeles'.",
    "Abrí una cuenta en un banco o cooperativa asegurada (dice FDIC o NCUA).",
    "Pregunté cuánto cobran al mes y cómo se quita ese cobro.",
    "Pedí que me desactiven el sobregiro.",
    "Activé alertas de cada compra en mi celular.",
    "Tengo un plan de celular prepagado (sin revisión de crédito ni depósito).",
    "Empecé mi carpeta del año: talones de pago, recibos de renta, facturas.",
    "Puse una transferencia automática de $20 por semana a mi colchón.",
    "Guardé en mi celular el número de una organización de ayuda legal o un abogado con licencia.",
]
DOCS = ["Pasaporte", "Acta de nacimiento", "Matrícula consular / identificación", "Actas de los niños",
        "Cartas o papeles migratorios", "Tarjeta de Seguro Social o carta del ITIN", "Contrato de renta",
        "Títulos o diplomas", "Cartilla de vacunas"]
ACCOUNT_BRING = ["Identificación con foto (muchos aceptan pasaporte o matrícula consular)",
                 "Comprobante de domicilio (contrato de renta o una factura con tu nombre)",
                 "Número de Seguro Social o ITIN, si tienes (algunas cuentas se abren sin ninguno)",
                 "Un primer depósito, si lo piden"]
ACCOUNT_ASK = ["¿Qué identificación aceptan?", "¿Cuánto cobran al mes?", "¿Cómo se quita ese cobro?",
               "¿Cobran por sobregiro? ¿Me lo pueden desactivar?", "¿Hay cajeros sin cobro cerca de mí?",
               "¿La cuenta está asegurada por la FDIC o la NCUA?"]
BUDGET = ["Renta", "Comida del súper", "Luz, gas y agua", "Celular e internet", "Transporte", "Lo que mando a mi familia",
          "Mi colchón (ahorro)", "Pagos de deudas", "Salud y medicinas", "Ropa y cosas de la casa", "Gustos y salidas"]
LEASE = ["Leí todo el contrato antes de firmar.", "Sé cuánto pago para entrar, todo junto.",
         "Sé cuánto dura y cuánto cobran si me salgo antes.", "Sé qué servicios pago yo: luz, agua, gas, basura, internet.",
         "Sé cuánto es el recargo por pagar tarde, y desde qué día.", "Sé quién arregla qué y cómo se pide una reparación.",
         "Vi el departamento por dentro y confirmé que quien me lo renta es el dueño o la administración.",
         "No pagué con app de pago, tarjeta de regalo ni transferencia a un desconocido.",
         "Me llevé una copia firmada por los dos."]
ROOMS = ["Entrada y sala", "Cocina", "Baño", "Recámara 1", "Recámara 2", "Ventanas y puertas", "Pisos y alfombra",
         "Aparatos (estufa, refri)", "Calefacción y aire"]
CREDIT = ["Mes 6: pedí mis reportes gratis en AnnualCreditReport.com (si tengo Seguro Social).",
          "Pregunté en mi cooperativa o banco por una tarjeta asegurada o un préstamo para construir crédito (algunas aceptan ITIN).",
          "Uso la tarjeta solo para un gasto chico, como el celular.",
          "La pago completa cada mes, en automático.",
          "Uso menos del 30% de mi límite.",
          "Nunca compré un 'número nuevo' (CPN): es una estafa."]
FOLDER = ["Talones de pago (todo el año)", "Estados de cuenta del banco", "Contrato de renta y recibos de cada pago",
          "Facturas de luz, gas, agua e internet", "Formularios de impuestos (W-2, 1099) que lleguen en enero",
          "Cartas del depósito de servicios y cuándo lo devuelven", "Fotos y lista de daños del departamento",
          "Mensajes de reparaciones y respuestas"]
TAXES = ["Si trabajé, probablemente tengo que declarar impuestos la primavera siguiente, aunque sea mi primer año.",
         "Si no tengo Seguro Social, el ITIN se pide con el formulario W-7, normalmente junto con la declaración.",
         "Busqué ayuda gratis: el programa VITA prepara declaraciones sin costo para muchas familias.",
         "Nadie que me cobre por 'arreglar mis papeles' con los impuestos puede cambiar mi situación migratoria."]
HELP = ["Biblioteca pública más cercana", "Cooperativa o banco", "Mi consulado", "Organización comunitaria",
        "Clínica comunitaria (cobra según mi ingreso)", "Ayuda legal gratis o grupo de inquilinos",
        "Abogado de inmigración con licencia u organización acreditada", "Ayuda gratis con impuestos (VITA)"]


def pages() -> list[str]:
    cover = f"""<section class="page cover"><div class="badge"></div>
      <div class="kicker" style="color:var(--amber)">Dinero Simple · cuaderno para imprimir</div>
      <h1>Tu primer año <span>en Estados Unidos</span></h1>
      <p class="sub">{esc(SUBTITLE)}</p>
      <ul><li>Tu año en cuatro etapas, con una lista para cada una</li><li>Tu presupuesto, tu colchón y el precio de verdad</li>
      <li>Rentar sin que te roben: contrato, fotos, pagos y reparaciones</li><li>Tu crédito, tus impuestos, ayuda gratis y el plan de tu familia</li></ul>
      <div class="foot">{esc(DISCLAIMER)} {esc(ATTORNEY_LINE)} Revisado en {esc(VERSION)}. © Dinero Simple. Para uso personal y familiar.</div></section>"""
    stages = "".join(f'<div class="stage"><b>{esc(a)}</b><div>{esc(b)}</div></div>' for a, b in STAGES)
    p2 = page(f"""<div class="kicker">Empieza aquí</div><h2>Cómo usar este cuaderno</h2>
      <p class="lede">Imprímelo, ponlo en una carpeta y llénalo con lápiz. No tienes que hacer todo el primer mes: el año
      tiene cuatro etapas, y cada página te dice qué toca.</p>{stages}
      <div class="box tip"><strong>Una regla para todo el año:</strong> si alguien te cobra por adelantado para abrir una
      cuenta, conseguirte crédito o arreglar un trámite, desconfía. Lo básico se hace gratis.</div>
      <div class="box warn">{esc(ATTORNEY_LINE)}</div>""", 2)
    p3 = page(f"""<div class="kicker">Mes 1</div><h2>Tu primer mes: la lista</h2>
      <p class="lede">Marca cada cosa cuando la termines. Si algo no aplica para ti, táchalo.</p>{checks(MONTH1)}
      <h3>Fecha en que llegué</h3><p><span class="fill"></span></p>""", 3)
    p4 = page(f"""<div class="kicker">Mes 1</div><h2>Mis papeles</h2>
      <p class="lede">Dónde está cada original, si ya tiene foto y cuándo vence. No le entregues tus originales a nadie que
      te prometa trámites rápidos: una copia casi siempre basta.</p>
      {table(["Documento", "¿Dónde está el original?", "¿Foto? (sí/no)", "Vence"], len(DOCS) + 3, DOCS, ["34%", "34%", "14%", "18%"])}""", 4)
    p5 = page(f"""<div class="kicker">Mes 1</div><h2>Abrir mi cuenta</h2>
      <h3>Lo que llevo</h3>{checks(ACCOUNT_BRING)}
      <h3>Compara dos lugares antes de escoger</h3>
      {table(["Pregunta", "Lugar 1: ______________", "Lugar 2: ______________"], len(ACCOUNT_ASK), ACCOUNT_ASK, ["40%", "30%", "30%"])}
      <div class="box tip">Una cuenta asegurada protege tu dinero hasta $250,000 por depositante, por institución y por tipo de
      cuenta. El dinero en casa no te protege de un robo ni deja registro de lo que ganas.</div>""", 5)
    p6 = page(f"""<div class="kicker">Mes 1</div><h2>Si me roban la tarjeta</h2>
      <p class="lede">Lo que pierdes depende del tipo de tarjeta y de qué tan rápido avisas.</p>
      <table><tr><th>Tarjeta</th><th>Si avisas…</th><th>Lo máximo que pierdes</th></tr>
      <tr><td>Crédito</td><td>Cuando sea</td><td>$50 (muchas cobran $0)</td></tr>
      <tr><td>Débito</td><td>En 2 días hábiles</td><td>$50</td></tr>
      <tr><td>Débito</td><td>Hasta 60 días después de tu estado de cuenta</td><td>Hasta $500</td></tr>
      <tr><td>Débito</td><td>Después de 60 días</td><td>Puede ser más</td></tr></table>
      <h3>Mis números (cópialos de la tarjeta, no de un mensaje)</h3>
      {table(["Tarjeta o cuenta", "Teléfono para reportar", "Últimos 4 números"], 4, None, ["40%", "35%", "25%"])}
      <div class="box warn"><strong>Las apps de pago entre personas son como efectivo.</strong> Úsalas solo con familia y
      amigos que conoces en persona. Para comprar, mejor tarjeta de crédito: puedes disputar el cargo.</div>""", 6)
    rows = "".join(f'<tr><td>{esc(x)}</td><td></td><td></td></tr>' for x in BUDGET)
    p7 = page(f"""<div class="kicker">Meses 2 y 3</div><h2>Mi presupuesto del mes</h2>
      <p class="lede">Escribe lo que planeas y, al final del mes, lo que de verdad gastaste. Haz una copia para cada mes.</p>
      <p>Mes: <span class="fill" style="min-width:1.6in"></span> &nbsp; Me llega al mes (neto): <span class="fill" style="min-width:1.6in"></span></p>
      <table class="sum"><tr><th>Gasto</th><th>Planeo</th><th>Gasté</th></tr>{rows}
      <tr class="t"><td>Total</td><td></td><td></td></tr><tr class="t"><td>Me llega menos el total = me sobra</td><td></td><td></td></tr></table>
      <div class="box tip"><strong>Ejemplo inventado:</strong> Rosa y Daniel reciben $3,200 al mes. Renta $1,400, comida $800,
      servicios $250, transporte $200 y lo que mandan a casa $200 suman $2,850. Les sobran $350, y de ahí sale su colchón.</div>""", 7)
    p8 = page(f"""<div class="kicker">Meses 2 y 3</div><h2>El precio de verdad</h2>
      <p class="lede">Aquí el precio de la etiqueta casi nunca es lo que pagas.</p>
      <table><tr><th>Lo que se suma</th><th>Lo mío</th></tr>
      <tr><td>Impuesto de ventas de mi ciudad (búscalo: "impuesto de ventas" + tu ciudad)</td><td>______ %</td></tr>
      <tr><td>Propina en restaurante con mesero (se espera 15% a 20%; revisa si ya dice "service charge")</td><td>______ %</td></tr>
      <tr><td>Cargos de envío y servicio en apps de comida</td><td>$ ______</td></tr>
      <tr><td>Suscripciones que se renuevan solas (revisa tu estado de cuenta)</td><td>$ ______ al mes</td></tr></table>
      <h3>Haz la cuenta antes de salir</h3>
      <table><tr><th>Ejemplo</th><th>Tu cuenta</th></tr>
      <tr><td>Comida: $40.00</td><td>Comida: $ ______</td></tr>
      <tr><td>+ Impuesto 8%: $3.20</td><td>+ Impuesto ___%: $ ______</td></tr>
      <tr><td>+ Propina 18% (sobre $40): $7.20</td><td>+ Propina ___%: $ ______</td></tr>
      <tr><td><strong>Total: unos $50</strong></td><td><strong>Total: $ ______</strong></td></tr></table>""", 8)
    p9 = page(f"""<div class="kicker">Meses 2 y 3</div><h2>Servicios y depósitos</h2>
      <p class="lede">Sin historial de crédito, la luz, el gas o el internet te pueden pedir un depósito. Pregunta si aceptan
      una carta de buen pago de tu compañía anterior, si lo bajan con pago automático y cuándo lo devuelven. Pídelo por escrito.</p>
      {table(["Compañía", "Depósito", "¿Lo bajaron? ¿Cómo?", "Lo devuelven el", "¿Por escrito?"], 7, ["Luz", "Gas", "Agua", "Internet", "Celular"], ["20%", "14%", "30%", "20%", "16%"])}
      <div class="box tip">Si no te alcanza para pagar una factura, llama antes de la fecha y pregunta por planes de pago y
      programas de ayuda. Cada programa tiene sus propios requisitos.</div>""", 9)
    weeks = "".join(f"<div><b>Semana {i}</b>$20 · ☐</div>" for i in range(1, 26))
    p10 = page(f"""<div class="kicker">Meses 2 a 6</div><h2>Mi colchón: de $0 a $500</h2>
      <p class="lede">Veinte dólares por semana, veinticinco semanas, quinientos dólares. Pon una transferencia automática el
      día de pago a un apartado con nombre, y marca cada semana.</p><div class="weeks">{weeks}</div>
      <table><tr><th>Escalón</th><th>Meta</th><th>Lo logré el</th></tr>
      <tr><td>1. Mi primer colchón</td><td>$500</td><td></td></tr><tr><td>2. Un mes de renta</td><td>$ ______</td><td></td></tr>
      <tr><td>3. Tres meses de lo básico</td><td>$ ______</td><td></td></tr></table>
      <p style="font-size:9.5pt;color:var(--muted)">Solo para emergencias de verdad: salud, trabajo, el carro para ir a trabajar.</p>""", 10)
    p11 = page(f"""<div class="kicker">Meses 4 a 6</div><h2>Antes de firmar la renta</h2>{checks(LEASE)}
      <h3>Mi total para entrar</h3>
      <table class="sum"><tr><th>Concepto</th><th>Ejemplo ($1,200 al mes)</th><th>El mío</th></tr>
      <tr><td>Primer mes</td><td>$1,200</td><td></td></tr><tr><td>Depósito</td><td>$1,200</td><td></td></tr>
      <tr><td>Cargo de solicitud</td><td>$50</td><td></td></tr><tr><td>Último mes (si lo piden)</td><td>$1,200</td><td></td></tr>
      <tr class="t"><td>Total</td><td>$2,450 o $3,650</td><td></td></tr></table>
      <p style="font-size:9.5pt;color:var(--muted)">Una guía común: que la renta no pase del 30% de lo que ganas antes de impuestos. Es una referencia, no una ley.</p>""", 11)
    p12 = page(f"""<div class="kicker">El primer día en tu casa nueva</div><h2>Lista de daños al entrar</h2>
      <p class="lede">Antes de meter tus cosas, toma fotos y video de cada cuarto. Anota lo que ya está dañado, mándalo por
      correo al dueño o la administración ese mismo día y guarda la respuesta. Esta lista vale tanto como tu depósito.</p>
      <p>Dirección: <span class="fill" style="min-width:3.3in"></span> &nbsp; Fecha: <span class="fill" style="min-width:1.1in"></span></p>
      {table(["Cuarto", "Lo que ya está dañado", "¿Foto?", "Al salir"], len(ROOMS), ROOMS, ["24%", "50%", "10%", "16%"])}
      <p>Firma del inquilino: <span class="fill" style="min-width:1.9in"></span> &nbsp; Firma del dueño: <span class="fill" style="min-width:1.9in"></span></p>""", 12)
    months = ["Mes 1", "Mes 2", "Mes 3", "Mes 4", "Mes 5", "Mes 6", "Mes 7", "Mes 8", "Mes 9", "Mes 10", "Mes 11", "Mes 12"]
    p13 = page(f"""<div class="kicker">Todo el año</div><h2>Mis pagos de renta</h2>
      <p class="lede">Paga de una forma que deje rastro y guarda cada recibo. Si pagas en efectivo, pide siempre un recibo
      firmado con la fecha, el monto y la dirección. Estos recibos también son tu historial para tu próxima renta.</p>
      {table(["Mes", "Fecha en que pagué", "Monto", "Cómo pagué", "¿Recibo?"], 12, months, ["14%", "22%", "16%", "30%", "18%"])}""", 13)
    p14 = page(f"""<div class="kicker">Todo el año</div><h2>Mis reparaciones</h2>
      <p class="lede">Pídelas siempre por escrito, con fotos y la fecha, y guarda cada respuesta. No dejes de pagar la renta
      sin antes preguntar las reglas de tu estado a ayuda legal o a un grupo de inquilinos.</p>
      {table(["Fecha", "Qué está mal", "Cómo lo pedí", "Respuesta y fecha", "¿Arreglado?"], 6, None, ["13%", "30%", "17%", "25%", "15%"])}
      <h3>Mensaje modelo (cópialo y cámbialo)</h3>
      <div class="msg">Hola, [nombre]. Soy [tu nombre], del departamento [número] en [dirección]. Desde el [fecha], [qué está
      mal, por ejemplo: no hay agua caliente]. Le mando fotos. ¿Me puede decir qué día vienen a arreglarlo? Gracias.</div>""", 14)
    p15 = page(f"""<div class="kicker">Meses 6 a 12</div><h2>Empieza tu historial de crédito</h2>{checks(CREDIT)}
      {table(["Mes", "Saldo de la tarjeta", "¿La pagué completa?", "¿A tiempo?"], 7, ["Mes 6", "Mes 7", "Mes 8", "Mes 9", "Mes 10", "Mes 11", "Mes 12"], ["16%", "30%", "28%", "26%"])}
      <div class="box warn">{esc(ATTORNEY_LINE)}</div>""", 15)
    p16 = page(f"""<div class="kicker">Todo el año</div><h2>La carpeta de tu primer año</h2>
      <p class="lede">Prueba tus ingresos y tu domicilio. Te la van a pedir para rentar, pedir crédito y hacer tus impuestos.
      El original en la carpeta; una foto en el celular.</p>{checks(FOLDER)}
      <h3>Tus impuestos del primer año</h3>{checks(TAXES)}""", 16)
    p17 = page(f"""<div class="kicker">Para tener a la mano</div><h2>Ayuda gratis cerca de mí</h2>
      <p class="lede">No tienes que pagarle a nadie para lo básico. Busca estos lugares y anota cómo llegar.</p>
      {table(["Lugar", "Nombre y dirección", "Teléfono"], len(HELP), HELP, ["36%", "40%", "24%"])}
      <div class="box warn">Aquí un "notary public" no es abogado: solo confirma quién firma. {esc(ATTORNEY_LINE)}</div>""", 17)
    p18 = page(f"""<div class="kicker">Para hacer en familia</div><h2>El plan de mi familia</h2>
      <p class="lede">Si un día no pudieras llegar a casa, esto es lo que tu familia necesita saber. Llénenlo juntos y guárdenlo
      con tus papeles.</p>
      <table><tr><th>Pregunta</th><th>Respuesta</th></tr>
      <tr><td class="b">¿Quién puede recoger a los niños? (y ¿la escuela lo tiene anotado?)</td><td></td></tr>
      <tr><td class="b">¿Dónde están los originales y las copias de los papeles?</td><td></td></tr>
      <tr><td class="b">¿Quién puede pagar la renta si yo no puedo, y cómo llega al dinero?</td><td></td></tr>
      <tr><td class="b">Contacto de emergencia 1 (nombre y teléfono)</td><td></td></tr>
      <tr><td class="b">Contacto de emergencia 2 (nombre y teléfono)</td><td></td></tr>
      <tr><td class="b">Abogado de inmigración con licencia u organización acreditada</td><td></td></tr>
      <tr><td class="b">Mi consulado</td><td></td></tr></table>
      <div class="box tip">Los papeles legales, como un poder o una autorización para que alguien cuide a tus hijos, prepáralos
      con un abogado con licencia en tu estado, nunca con un notario.</div>""", 18)
    p19 = page(f"""<div class="kicker">Lo lograste</div><h2>Tu año, en una página</h2>
      {table(["Meta", "¿Listo?", "Fecha"], 8, ["Papeles a salvo y con foto", "Cuenta asegurada sin cobro mensual", "Presupuesto del mes, cada mes",
       "Colchón de $500", "Contrato leído, fotos del primer día y recibos", "Historial de crédito empezado", "Impuestos del primer año",
       "Plan de mi familia lleno"], ["60%", "15%", "25%"])}
      <div class="box dark"><div class="kicker">Lo que sigue</div><p>El segundo año es para un mes de renta en tu colchón, subir
      tu crédito y empezar tu retiro, aunque sea con poco. Cada semana, un paso concreto con tu dinero en Dinero Simple.</p></div>
      <p style="font-size:9pt;color:var(--muted)">{esc(DISCLAIMER)}</p>""", 19)
    return [cover, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19]


def doc(title: str, body: list[str]) -> str:
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{esc(title)}</title>'
            f"<style>{SHARED_CSS}{CSS}</style></head><body>{''.join(body)}</body></html>")


def gumroad() -> str:
    return f"""# Gumroad listing: {TITLE} (cuaderno de dinero)

**Gumroad only.** Etsy has banned AI-generated functional guides since Oct 22 2026, and this workbook's instructions
were drafted with AI help, so it does not go on Etsy. **REVISIÓN NATIVA PENDIENTE:** a fluent Spanish speaker signs off
`REVIEW_CHECKLIST_PRIMER_ANO.md` before it goes on sale.

- **Name:** Tu primer año en Estados Unidos: cuaderno de dinero para imprimir
- **Price:** {PRICE} (Dhruv sets it; the product ladder runs $5 to $29)
- **File:** `Cuaderno-Tu-Primer-Ano.pdf` (19 pages, Letter, print at 100%)
- **URL slug:** `tu-primer-ano`
- **Tags:** recién llegados, inmigrantes, presupuesto, rentar, crédito, español

## Description

Un cuaderno para imprimir y llenar con lápiz, para tu primer año de dinero en Estados Unidos. Te dice qué hacer mes por
mes y te da dónde anotarlo: tus papeles, tu cuenta, tu presupuesto, tu colchón, la renta, tu crédito, tus impuestos y
el plan de tu familia.

**Qué incluye (19 páginas):**
- Tu año en cuatro etapas, con una lista para el primer mes
- Mis papeles: dónde está cada original y cuándo vence
- Abrir tu cuenta: qué llevar y una tabla para comparar dos lugares
- Si te roban la tarjeta: los plazos de débito y de crédito
- Tu presupuesto del mes, el precio de verdad (impuesto y propina) y los depósitos de servicios
- Tu colchón de $0 a $500: 25 semanas para marcar
- Antes de firmar la renta, la lista de daños del primer día, tus pagos y tus reparaciones (con un mensaje modelo)
- Tu historial de crédito, la carpeta del año y tus impuestos del primer año
- Ayuda gratis cerca de ti y el plan de tu familia

**Para quién:** quien acaba de llegar, o quien lleva un tiempo aquí y quiere poner su dinero en orden desde el principio.
Sirve con número de Seguro Social o sin él.

**Qué no es:** no es asesoría financiera, legal, de impuestos ni migratoria. Para cualquier pregunta sobre tu situación
migratoria, habla con un abogado de inmigración con licencia o un representante acreditado, nunca con un notario.

**Cómo se hizo:** redactado con ayuda de herramientas de IA y revisado por una persona de Dinero Simple. Todos los
nombres y números de ejemplo son inventados.

**Garantía:** si no es para ti, escríbenos dentro de 14 días y te devolvemos todo.
"""


def review_doc() -> str:
    return "\n".join([
        f"# Review checklist: {TITLE} (cuaderno, Gumroad)", "",
        "Nothing from `launch/dinero-simple/primer-ano/` goes on sale until every box is ticked. Edit `build_cuaderno.py`, "
        "never the PDF, then run `python3 launch/dinero-simple/primer-ano/build_cuaderno.py --pdf`.", "",
        "## Sign-off",
        "- [ ] **Native-speaker review** of every page and of `GUMROAD.md` (machine-written Spanish, tú register).",
        "- [ ] **ATTORNEY REVIEW:** a licensed immigration attorney or DOJ-accredited representative reads pages 2, 4, 15, 16, 17 "
        "and 18 (documents, ITIN, notario, family plan) the week it goes on sale.",
        "- [ ] **Tenant-law check:** pages 11 to 14 stay general (\"en muchos estados\"); nothing promises a state rule.",
        "- [ ] **Print test** at 100% on Letter paper: every table fits, nothing runs off the page.",
        "- [ ] **Price** set in place of [PRICE] (GUMROAD.md and the Gumroad product).",
        "- [ ] **Not listed on Etsy** (AI-generated functional guides are banned there since Oct 22 2026).", "",
        "## Facts to check",
        "- [ ] FDIC/NCUA insurance: up to $250,000 per depositor, per insured institution, per ownership category.",
        "- [ ] Card liability: credit $50 cap; debit $50 within 2 business days, up to $500 within 60 days of the statement, possibly more after (Reg E).",
        "- [ ] Example arithmetic: $40 + 8% ($3.20) + 18% ($7.20) = $50.40; 25 × $20 = $500; $1,200 + $1,200 + $50 = $2,450 (+ $1,200 = $3,650); "
        "$1,400 + $800 + $250 + $200 + $200 = $2,850, $3,200 − $2,850 = $350.",
        "- [ ] 30% of gross income as a rent guideline is described as a reference, not a law.",
        "- [ ] The ITIN is applied for with Form W-7, normally with a federal return; VITA offers free tax help to eligible filers.",
        "- [ ] Some secured cards and credit-builder loans accept an ITIN (varies); CPNs are a scam (FTC).",
        "- [ ] No bank, app, landlord, remittance company or lender is named anywhere.", "",
    ]) + "\n"


def to_pdf(src: Path, out: Path) -> None:
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();"
          "await p.goto('file://" + str(src) + "');await p.pdf({path:'" + str(out) + "',"
          "format:'Letter',printBackground:true,preferCSSPageSize:true});await b.close();})();")
    subprocess.run(["node", "-e", js], check=True, env={**os.environ, "NODE_PATH": "/opt/node22/lib/node_modules"})


def main() -> None:
    (DS / "REVIEW_CHECKLIST_PRIMER_ANO.md").write_text(review_doc())
    (HERE / "GUMROAD.md").write_text(gumroad())
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir()
    src = DIST / "Cuaderno-Tu-Primer-Ano.html"
    src.write_text(doc(TITLE, pages()))
    if "--pdf" in sys.argv:
        to_pdf(src, DIST / "Cuaderno-Tu-Primer-Ano.pdf")
    for p in sorted(DIST.iterdir()):
        print(f"{p.name:34s} {p.stat().st_size // 1024:>6} KB")


if __name__ == "__main__":
    main()
