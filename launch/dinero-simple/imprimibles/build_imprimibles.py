"""Build three Etsy-safe Spanish printables for Dinero Simple: trackers and logs with labels only, no how-to text
(Etsy bans AI-generated functional guides since Oct 22 2026; planners, trackers and logs stay allowed, see PR #6's
launch/catalog/etsy_rules.py). They complement PR #6's El Presupuesto Familiar and El Registro de Envíos, which
already cover the Spanish budget planner and the remittance log.

    python3 launch/dinero-simple/imprimibles/build_imprimibles.py          # dist/<slug>/*.html + LISTING.md
    python3 launch/dinero-simple/imprimibles/build_imprimibles.py --pdf    # also the PDFs and a cover.png per item

Products:
  registro-de-cuentas   Registro de Cuentas y Pagos (bill tracker, 7 pages, undated so it works any year)
  reto-de-ahorro        Retos de Ahorro (savings trackers: $500 in 25 weeks, 52 weeks, a free-form goal, 6 pages)
  renta-y-reparaciones  Registro de Renta y Reparaciones (rent log, move-in list, repair log, contacts, 6 pages)

Every listing needs a native-speaker read (REVISIÓN NATIVA PENDIENTE) and a price (left as [PRICE]).
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
PRICE = "[PRICE]"
MONTHS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
          "Noviembre", "Diciembre"]
MESES3 = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

CSS = """
  html,body{font-size:12pt;line-height:1.4}
  .page{padding:0.6in 0.6in 0.75in}
  h2{font-size:26pt;margin:0 0 4px} .kicker{font-size:9.5pt} .sub{color:var(--muted);margin:0 0 12px}
  table{width:100%;border-collapse:collapse;font-size:11pt;margin:6px 0 12px}
  th{background:var(--ink);color:var(--cream);text-align:left;padding:7px 7px;font-size:9.5pt}
  td{border:1px solid var(--line);padding:6px 7px;height:44px;vertical-align:top}
  td.l{font-weight:600} .grid td{height:44px;text-align:center;padding:2px} .grid td:first-child{text-align:left}
  .cells{display:grid;gap:6px;margin:8px 0}
  .cells div{border:1.6px solid var(--ink);border-radius:8px;padding:4px 6px;font-size:10pt;font-weight:700;min-height:0.62in}
  .therm{display:grid;grid-template-columns:repeat(10,1fr);gap:5px;margin:10px 0}
  .therm div{border:1.6px solid var(--ink);border-radius:6px;height:0.68in;font-size:8.5pt;padding:2px 4px;color:var(--muted)}
  .big5 div{min-height:1.2in;font-size:12pt}
  .row2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
  .line{border-bottom:1.4px solid var(--ink);height:26px;margin:4px 0}
"""


def page(title: str, kicker: str, body: str, product: str, n: int) -> str:
    return (f'<section class="page"><div class="kicker">{esc(kicker)}</div><h2>{esc(title)}</h2>{body}'
            f'<div class="folio"><span>Dinero Simple · {esc(product)}</span><span>{n}</span></div></section>')


def cover(name: str, sub: str, bullets: list[str]) -> str:
    lis = "".join(f"<li>{esc(b)}</li>" for b in bullets)
    return f"""<section class="page cover"><div class="badge"></div>
      <div class="kicker" style="color:var(--amber)">Dinero Simple · para imprimir</div>
      <h1>{esc(name.split(' ', 1)[0])} <span>{esc(name.split(' ', 1)[1])}</span></h1>
      <p class="sub" style="color:#c9d2dc">{esc(sub)}</p><ul>{lis}</ul>
      <div class="foot">Para uso personal. Tamaño carta (8.5 × 11 in); imprime al 100%. © Dinero Simple.</div></section>"""


def blank_table(head: list[str], rows: int, first: list[str] | None = None, widths: list[str] | None = None,
                cls: str = "") -> str:
    w = widths or [""] * len(head)
    th = "".join(f'<th style="{f"width:{x}" if x else ""}">{esc(h)}</th>' for h, x in zip(head, w))
    body = ""
    for i in range(rows):
        f = esc(first[i]) if first and i < len(first) else ""
        body += f'<tr><td class="l">{f}</td>' + "<td></td>" * (len(head) - 1) + "</tr>"
    return f'<table class="{cls}"><tr>{th}</tr>{body}</table>'


# ------------------------------------------------------------------ Registro de Cuentas y Pagos
def cuentas() -> list[str]:
    P = "Registro de Cuentas y Pagos"
    grid_head = ["Cuenta"] + MESES3
    p = [cover(P, "Todas tus cuentas en un solo lugar: qué se paga, cuándo y si ya quedó.",
               ["Resumen del año: 12 meses de un vistazo", "Página del mes (imprime una cada mes)",
                "Suscripciones", "Deudas y saldos", "Teléfonos y cuentas en línea"])]
    p.append(page("Mi año de un vistazo", "Resumen del año", '<p class="sub">Año: ______ · Marca cada cuenta cuando quede pagada.</p>'
                  + blank_table(grid_head, 18, None, ["22%"] + ["6.5%"] * 12, "grid"), P, 2))
    p.append(page("Cuentas del mes", "Página del mes", '<p class="sub">Mes: ______________ · Ingreso del mes: $ __________</p>'
                  + blank_table(["Cuenta", "Vence el día", "Monto", "¿Automático?", "Pagado el", "✓"], 14, None,
                                ["28%", "13%", "15%", "15%", "17%", "12%"])
                  + '<div class="row2"><div><strong>Total de cuentas:</strong> $ __________</div>'
                    '<div><strong>Me queda:</strong> $ __________</div></div>', P, 3))
    p.append(page("Cuentas del mes", "Página del mes (copia extra)", '<p class="sub">Mes: ______________ · Ingreso del mes: $ __________</p>'
                  + blank_table(["Cuenta", "Vence el día", "Monto", "¿Automático?", "Pagado el", "✓"], 14, None,
                                ["28%", "13%", "15%", "15%", "17%", "12%"])
                  + '<div class="row2"><div><strong>Total de cuentas:</strong> $ __________</div>'
                    '<div><strong>Me queda:</strong> $ __________</div></div>', P, 4))
    p.append(page("Mis suscripciones", "Lo que se cobra solo", blank_table(
        ["Servicio", "Cobra el día", "Al mes", "Al año", "¿La uso?", "¿Cancelar?"], 16, None,
        ["28%", "13%", "13%", "13%", "16%", "17%"]) + '<p><strong>Total al mes:</strong> $ ________ &nbsp; '
        '<strong>Total al año:</strong> $ ________</p>', P, 5))
    p.append(page("Mis deudas", "Saldos", blank_table(
        ["Deuda", "Tasa (APR)", "Pago mínimo", "Vence el día"] + MESES3[:4], 8, None,
        ["22%", "11%", "12%", "11%", "11%", "11%", "11%", "11%"]) + blank_table(
        ["Deuda"] + MESES3[4:], 8, None, ["22%"] + ["9.75%"] * 8), P, 6))
    p.append(page("Teléfonos y cuentas en línea", "Para tener a la mano", blank_table(
        ["Compañía", "Número de cuenta (últimos 4)", "Teléfono", "Página web", "Usuario"], 16, None,
        ["24%", "18%", "18%", "22%", "18%"]) + '<p style="font-size:9.5pt;color:var(--muted)">No escribas contraseñas completas en papel.</p>', P, 7))
    return p


# ------------------------------------------------------------------ Retos de Ahorro
def ahorro() -> list[str]:
    P = "Retos de Ahorro"
    p = [cover(P, "Tres hojas para ver crecer tu ahorro, semana por semana.",
               ["$500 en 25 semanas ($20 por semana)", "52 semanas: de $1 a $52 (total $1,378)",
                "Tu propia meta: un termómetro de 100 casillas", "Fondos con nombre: viaje, regalos, emergencias"])]
    weeks = "".join(f"<div>Semana {i}<br><span style='font-weight:400'>$20 ☐</span></div>" for i in range(1, 26))
    p.append(page("$500 en 25 semanas", "Reto 1", '<p class="sub">Empecé el: __________ · Meta: $500</p>'
                  f'<div class="cells big5" style="grid-template-columns:repeat(5,1fr)">{weeks}</div>'
                  '<p><strong>Llevo:</strong> $ ________ &nbsp; <strong>Terminé el:</strong> __________</p>', P, 2))
    w52 = "".join(f"<div>{i}<br><span style='font-weight:400'>${i} ☐</span></div>" for i in range(1, 53))
    p.append(page("52 semanas", "Reto 2", '<p class="sub">Empecé el: __________ · Total al final: $1,378 · '
                  'Puedes ir en cualquier orden.</p>'
                  f'<div class="cells" style="grid-template-columns:repeat(8,1fr)">{w52}</div>', P, 3))
    therm = "".join(f"<div>{i}</div>" for i in range(1, 101))
    p.append(page("Mi meta", "Reto 3", '<p class="sub">Mi meta: ______________________ · Total: $ ________ · '
                  'Cada casilla = $ ________</p>'
                  f'<div class="therm">{therm}</div><p><strong>Empecé el:</strong> __________ &nbsp; '
                  '<strong>Lo logré el:</strong> __________</p>', P, 4))
    funds = "".join(f'<div><h3 style="margin:6px 0">Fondo: ____________ · Meta: $ ______</h3>'
                    + blank_table(["Fecha", "Puse", "Saqué", "Saldo"], 6, None, ["25%", "25%", "25%", "25%"]) + "</div>"
                    for _ in range(2))
    p.append(page("Mis fondos con nombre", "Fondos", f'<div class="row2">{funds}{funds}</div>', P, 5))
    p.append(page("Mi ahorro del año", "Resumen", blank_table(
        ["Mes", "Ahorré", "Total acumulado", "Nota"], 12, MONTHS, ["22%", "20%", "25%", "33%"]), P, 6))
    return p


# ------------------------------------------------------------------ Registro de Renta y Reparaciones
ROOMS = ["Entrada y sala", "Cocina", "Baño", "Recámara 1", "Recámara 2", "Ventanas y puertas", "Pisos y alfombra",
         "Aparatos", "Calefacción y aire", "Otro"]


def renta() -> list[str]:
    P = "Registro de Renta y Reparaciones"
    p = [cover(P, "Tus pagos, el estado del departamento y cada reparación, por escrito y con fecha.",
               ["Datos del contrato y contactos", "Pagos de renta: 12 meses con recibo", "Estado del departamento al entrar y al salir",
                "Registro de reparaciones", "Registro de avisos y mensajes"])]
    p.append(page("Mi contrato y mis contactos", "Datos", blank_table(
        ["Dato", "Lo mío"], 13, ["Dirección", "Dueño o administración", "Teléfono", "Correo", "Portal de pagos",
                                 "Renta al mes", "Vence el día", "Recargo por pagar tarde", "Depósito", "Inicio del contrato",
                                 "Fin del contrato", "Aviso para salir (días)", "Mantenimiento de emergencia"],
        ["40%", "60%"]), P, 2))
    p.append(page("Mis pagos de renta", "Pagos", '<p class="sub">Año: ______</p>' + blank_table(
        ["Mes", "Fecha de pago", "Monto", "Cómo pagué", "Recibo / confirmación", "Recargo"], 12, MONTHS,
        ["16%", "16%", "14%", "18%", "24%", "12%"]), P, 3))
    p.append(page("Estado del departamento", "Al entrar y al salir", '<p class="sub">Fecha de entrada: __________ · '
                  'Fecha de salida: __________</p>' + blank_table(
        ["Cuarto", "Al entrar", "Foto ✓", "Al salir", "Foto ✓"], len(ROOMS), ROOMS, ["20%", "32%", "8%", "32%", "8%"])
                  + '<div class="row2"><div>Firma del inquilino<div class="line"></div></div>'
                    '<div>Firma del dueño<div class="line"></div></div></div>', P, 4))
    p.append(page("Mis reparaciones", "Reparaciones", blank_table(
        ["Fecha", "Qué está mal", "Avisé por", "Respuesta", "Arreglado el"], 13, None, ["13%", "33%", "16%", "24%", "14%"]), P, 5))
    p.append(page("Avisos y mensajes", "Registro", blank_table(
        ["Fecha", "De / para", "Tema", "Cómo (correo, mensaje, carta)", "Guardado en"], 15, None,
        ["13%", "20%", "29%", "20%", "18%"]), P, 6))
    return p


PRODUCTS = [
    dict(slug="registro-de-cuentas", name="Registro de Cuentas y Pagos", pages=cuentas,
         title="Registro de Cuentas y Pagos en Español, Bill Tracker Imprimible para Todo el Año",
         what="Un registro imprimible en español para anotar tus cuentas y pagos del mes, tus suscripciones y tus deudas.",
         tags=["bill tracker", "registro de cuentas", "spanish printable", "en español", "control de gastos",
               "bill payment log", "monthly bills", "suscripciones", "deudas", "planner español", "finanzas personales",
               "pago de cuentas", "printable pdf"]),
    dict(slug="reto-de-ahorro", name="Retos de Ahorro", pages=ahorro,
         title="Retos de Ahorro en Español, 52 Semanas y $500, Savings Tracker Imprimible",
         what="Tres hojas imprimibles en español para ver crecer tu ahorro: $500 en 25 semanas, 52 semanas y tu propia meta.",
         tags=["savings challenge", "reto de ahorro", "52 semanas", "spanish printable", "en español", "ahorro",
               "savings tracker", "sinking funds", "fondo de ahorro", "planner español", "money challenge",
               "ahorrar dinero", "printable pdf"]),
    dict(slug="renta-y-reparaciones", name="Registro de Renta y Reparaciones", pages=renta,
         title="Registro de Renta y Reparaciones en Español, Rent Tracker para Inquilinos Imprimible",
         what="Un registro imprimible en español para inquilinos: pagos de renta, estado del departamento, reparaciones y avisos.",
         tags=["rent tracker", "registro de renta", "inquilinos", "spanish printable", "en español", "rent log",
               "move in checklist", "repair log", "renter planner", "departamento", "landlord log", "vivienda",
               "printable pdf"]),
]


def doc(title: str, pages: list[str]) -> str:
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{esc(title)}</title>'
            f"<style>{SHARED_CSS}{CSS}</style></head><body>{''.join(pages)}</body></html>")


def listing(it: dict, n_pages: int) -> str:
    tags = "\n".join(f"{i}. {t}" for i, t in enumerate(it["tags"], 1))
    return f"""# Etsy listing: {it['name']}

**Etsy-safe:** a tracker/log with labels only, no instructions (Etsy's Oct 22 2026 AI-guide rule; PR #6's
`launch/catalog/etsy_rules.py` allows planners, trackers and logs). **REVISIÓN NATIVA PENDIENTE:** a fluent Spanish
speaker reads the PDF and this listing first. Price is {PRICE} until Dhruv sets it (PR #6 prices its Spanish planner
$9 and its remittance log $7).

- **Title:** {it['title']}
- **Price:** {PRICE}
- **Type:** digital download · **File:** `{it['file']}` ({n_pages} pages, US Letter)
- **Thumbnail:** `cover.png`

## Tags (13)
{tags}

## Description

{it['what']}

Qué incluye ({n_pages} páginas):
{chr(10).join('- ' + b for b in it['bullets'])}

- Tamaño carta (8.5 × 11 in). Imprime al 100% en casa o en una tienda de copias.
- Sin fechas: sirve para cualquier año.
- Archivo digital: no se envía nada por correo.

Diseño hecho con ayuda de herramientas digitales, incluida IA, y revisado por una persona de Dinero Simple. Para uso
personal. No es asesoría financiera ni legal.
"""


def to_pdf(src: Path, out: Path, png: Path) -> None:
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:816,height:1056},deviceScaleFactor:1.5});"
          "await p.goto('file://" + str(src) + "');await p.pdf({path:'" + str(out) + "',format:'Letter',printBackground:true,"
          "preferCSSPageSize:true});await p.emulateMedia({media:'print'});const el=await p.$('.page');"
          "await el.screenshot({path:'" + str(png) + "'});await b.close();})();")
    subprocess.run(["node", "-e", js], check=True, env={**os.environ, "NODE_PATH": "/opt/node22/lib/node_modules"})


def main() -> None:
    shutil.rmtree(DIST, ignore_errors=True)
    for it in PRODUCTS:
        d = DIST / it["slug"]
        d.mkdir(parents=True)
        pages = it["pages"]()
        it["file"] = f"{it['name'].replace(' ', '-')}.pdf"
        it["bullets"] = [x for x in __import__("re").findall(r"<li>(.*?)</li>", pages[0])]
        it["bullets"] = [html.unescape(x) for x in it["bullets"]]
        src = d / f"{it['slug']}.html"
        src.write_text(doc(it["name"], pages))
        (d / "LISTING.md").write_text(listing(it, len(pages)))
        if "--pdf" in sys.argv:
            to_pdf(src, d / it["file"], d / "cover.png")
        print(f"{it['slug']:22s} {len(pages)} pages")


if __name__ == "__main__":
    main()
