"""Build "Estafas: guía para papás y abuelos" (letra grande), the Spanish seniors scam guide.

    python3 launch/dinero-simple/mayores/build_mayores.py           # dist/*.html
    python3 launch/dinero-simple/mayores/build_mayores.py --pdf     # also dist/*.pdf (Chromium via Playwright)

Outputs:
  launch/dinero-simple/REVIEW_CHECKLIST_MAYORES.md   native-speaker and attorney sign-off (committed)
  dist/Guia-Estafas-Papas-y-Abuelos.pdf   large-print booklet with the fridge checklist and wallet cards
  dist/Lista-del-Refrigerador.pdf         1 page for the fridge
  dist/Tarjetas-de-Bolsillo.pdf           8 cut-out cards, fronts and backs (print double-sided, flip on long edge)

Layout and CSS come from PR #9's English seniors pack (shared.css is a copy) so both editions look like one family.
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
sys.path.insert(0, str(HERE))
import contenido as C  # noqa: E402

DIST = HERE / "dist"
SHARED_CSS = (HERE / "shared.css").read_text()
esc = html.escape

LARGE = """
  html,body{font-size:16pt;line-height:1.42}
  .page{padding:0.65in 0.75in 0.85in}
  h2{font-size:30pt;margin-bottom:12px} h3{font-size:19pt;margin:18px 0 6px}
  .kicker{font-size:12pt} .lede{font-size:17pt;color:var(--ink)}
  li{margin-bottom:10px} .folio{font-size:11pt}
  .rule{display:flex;gap:16px;margin:0 0 16px}.rule b.n{flex:0 0 46px;height:46px;border-radius:50%;background:var(--amber);
    display:flex;align-items:center;justify-content:center;font-size:20pt;font-weight:800}
  .call{border:2.5px solid var(--ink);border-radius:14px;padding:10px 16px;margin:0 0 12px;break-inside:avoid}
  .call h3{margin:0 0 4px;font-size:17pt}.call .say{font-style:italic;margin:0 0 4px}.call .do{font-weight:700;margin:0}
  table{font-size:15pt} td,th{padding:9px 8px} td.blank{height:44px}
  .fridge{font-size:17pt;padding:20px 28px}.fridge h2{font-size:32pt}.fridge li{margin-bottom:9px}
  .cover h1{font-size:50pt}.cover .sub{font-size:19pt}.cover ul{font-size:16pt}.cover .foot{font-size:11pt}
  .cards{display:grid;grid-template-columns:3.5in 3.5in;grid-auto-rows:2in;gap:0.35in 0.3in;justify-content:center;margin-top:0.2in}
  .card{border:1.5px dashed var(--muted);border-radius:12px;padding:0.14in 0.18in;font-size:10.5pt;line-height:1.28;overflow:hidden}
  .card b.t{display:block;font-size:13pt;margin-bottom:4px}.card ol{padding-left:18px;margin:0}.card li{margin:0 0 2px}
  .wallet{padding-top:0.4in;padding-bottom:0.3in}.wallet .cards{margin-top:0.1in}
  .card .ln{border-bottom:1px solid var(--ink);height:0.24in;margin-top:2px}
"""


def page(body: str, n: int | None) -> str:
    folio = f'<div class="folio"><span>{esc(C.TITLE)} · letra grande</span><span>{n}</span></div>' if n else ""
    return f'<section class="page">{body}{folio}</section>'


def wpage(body: str) -> str:
    return f'<section class="page wallet">{body}</section>'


def doc(title: str, pages: list[str]) -> str:
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{esc(title)}</title>'
            f"<style>{SHARED_CSS}{LARGE}</style></head><body>{''.join(pages)}</body></html>")


def calls_html(calls) -> str:
    return "".join(f'<div class="call"><h3>{esc(t)}</h3><p class="say">{esc(s)}</p><p class="do">{esc(d)}</p></div>'
                   for t, s, d, _ in calls)


def fridge_page(n: int | None) -> str:
    items = "".join(f"<li>{esc(x)}</li>" for x in C.FRIDGE)
    rows = "".join("<tr><td class='blank'></td><td></td></tr>" for _ in range(3))
    return page(f"""<div class="fridge"><div class="kicker">Para tener junto al teléfono</div>
      <h2>Antes de pagar, tocar o compartir algo</h2><ol>{items}</ol>
      <table><tr><th>Primero llamo a</th><th style="width:45%">Teléfono</th></tr>{rows}</table>
      <p style="font-size:14pt;margin:0">Reportar una estafa: <strong>1-877-382-4357</strong> · Fraude a mayores: <strong>1-833-372-8311</strong></p></div>""", n)


def wallet_pages() -> list[str]:
    front = ("<div class='card'><b class='t'>ALTO. ¿Es una estafa?</b><ol>"
             "<li>¿Prisa? ¿Secreto? ¿Pago raro? <b>Pare.</b></li>"
             "<li>Nunca tarjetas de regalo, giros, cripto ni efectivo.</li>"
             "<li>Nunca doy un código ni la clave de un envío.</li>"
             "<li>Cuelgo. Llamo yo a un número que busco yo.</li></ol></div>")
    back = ("<div class='card'><b class='t'>Antes de pagar, llamo a:</b>"
            "<div>Nombre</div><div class='ln'></div><div style='margin-top:4px'>Teléfono</div><div class='ln'></div>"
            "<div style='margin-top:6px'>Reportar una estafa: <b>1-877-382-4357</b></div>"
            "<div>Fraude a mayores: <b>1-833-372-8311</b></div></div>")
    note = ("<p style='font-size:12pt;color:var(--muted);margin:0'>Recorte por las líneas punteadas. Imprima por los dos "
            "lados (volteando por el lado largo), o pegue el frente con la parte de atrás.</p>")
    return [wpage(f"<div class='kicker'>Tarjetas de bolsillo · frente</div>{note}<div class='cards'>{front * 8}</div>"),
            wpage(f"<div class='kicker'>Tarjetas de bolsillo · reverso</div>{note}<div class='cards'>{back * 8}</div>")]


def booklet() -> list[str]:
    cover = f"""<section class="page cover"><div class="badge"></div>
      <div class="kicker" style="color:var(--amber)">Dinero Simple · letra grande</div>
      <h1>Estafas: <span>guía para papás y abuelos</span></h1>
      <p class="sub">{esc(C.SUBTITLE)}</p>
      <ul><li>5 reglas de oro que paran casi todas las estafas</li><li>Las llamadas a las que hay que colgar</li>
      <li>La clave de sus envíos de dinero y el fraude del notario</li><li>Lista para el refrigerador y tarjetas de bolsillo</li></ul>
      <div class="foot">Información general, no es asesoría legal ni financiera. {esc(C.ATTORNEY_LINE)} Teléfonos revisados en
      {esc(C.VERSION)}. Todas las llamadas, mensajes y nombres de ejemplo son inventados. © Dinero Simple. Para uso personal y familiar.</div></section>"""
    rules = "".join(f'<div class="rule"><b class="n">{i}</b><div><strong>{esc(a)}</strong><br>{esc(b)}</div></div>'
                    for i, (a, b) in enumerate(C.GOLDEN_RULES, 1))
    p2 = page(f"""<div class="kicker">Empiece aquí</div><h2>Las 5 reglas de oro</h2>
      <p class="lede">Los estafadores son profesionales. Gente lista y cuidadosa cae todos los días. Estas cinco reglas
      ganan a casi todos los trucos.</p>{rules}""", 2)
    p3 = page(f"""<div class="kicker">Llamadas</div><h2>Llamadas para colgar</h2>{calls_html(C.CALLS[:3])}""", 3)
    p4 = page(f"""<div class="kicker">Llamadas</div><h2>Más llamadas para colgar</h2>{calls_html(C.CALLS[3:])}""", 4)
    texts = "".join(f'<div class="call"><p class="say">{esc(s)}</p><p class="do">{esc(d)}</p></div>' for s, d in C.TEXTS)
    p5 = page(f"""<div class="kicker">Mensajes y correos</div><h2>No toque el enlace</h2>
      <p class="lede">Los mensajes falsos parecen venir del correo, del banco o de la autopista. Si tiene dudas, vaya usted
      a la empresa.</p>{texts}<p><strong>Gratis:</strong> reenvíe los mensajes de estafa al <strong>7726</strong> y luego bórrelos.</p>""", 5)
    remesas = "".join(f"<li>{esc(x)}</li>" for x in C.REMESAS)
    notario = "".join(f"<li>{esc(x)}</li>" for x in C.NOTARIO)
    p6a = page(f"""<div class="kicker">Envíos de dinero</div><h2>La clave de su envío</h2>
      <p class="lede">Mandar dinero a la familia es un cariño. Los estafadores lo saben.</p><ul>{remesas}</ul>""", 6)
    p6b = page(f"""<div class="kicker">Inmigración</div><h2>El notario no es abogado</h2><ul>{notario}</ul>
      <div class="box warn">{esc(C.ATTORNEY_LINE)}</div>""", 7)
    online = "".join(f"<li>{esc(x)}</li>" for x in C.ONLINE)
    p7 = page(f"""<div class="kicker">Amigos por internet y la computadora</div><h2>Cuando un amigo nuevo necesita dinero</h2>
      <p class="lede">Los estafadores del amor pasan semanas siendo amables antes de pedir algo. Cuidado con alguien:</p><ul>{online}</ul>
      <div class="box warn"><strong>La regla:</strong> nunca mande dinero, tarjetas de regalo ni criptomonedas a alguien que
      solo conoce por internet. Aunque se sienta muy real.</div>
      <h3>La ventana que asusta</h3>
      <p>“¡ALERTA! Su computadora tiene un virus. Llame ya a soporte técnico.” No llame. Cierre el navegador. Si no se cierra,
      apague la computadora y vuelva a prenderla. Las alertas de verdad nunca le dan un teléfono para llamar, y nadie que
      le llamó debe entrar a su computadora.</p>""", 8)
    lines = "".join(f"<li>{esc(x)}</li>" for x in C.HANG_UP_LINES)
    p8 = page(f"""<div class="kicker">Qué decir</div><h2>Sus frases para colgar</h2>
      <p class="lede">No tiene que ser amable con un desconocido que le llama. Escoja una frase y dígala en voz alta unas
      cuantas veces ahora.</p><ol style="font-size:19pt">{lines}</ol>
      <div class="box tip"><strong>Escojan una palabra secreta en familia.</strong> Pónganse de acuerdo en una palabra que
      un estafador nunca podría adivinar. Si alguien llama “en problemas”, pídale la palabra.<br><br>Nuestra palabra:
      <span class="fill"></span></div>""", 9)
    nums = "".join(f"<tr><td>{esc(a)}</td><td><strong>{esc(b)}</strong></td></tr>" for a, b in C.OFFICIAL_NUMBERS)
    p9 = page(f"""<div class="kicker">Números de confianza</div><h2>Teléfonos oficiales</h2>
      <p class="lede">Estos son números reales, con atención en español. Los estafadores a veces copian nombres oficiales,
      así que marque usted mismo.</p>
      <table><tr><th>Quién</th><th style="width:46%">Cómo comunicarse</th></tr>{nums}</table>
      <p style="font-size:12pt;color:var(--muted)">Revisados en {esc(C.VERSION)}. Si un número no funciona, búsquelo en la
      página oficial que termina en .gov.</p>""", 10)
    rows = "".join("<tr><td class='blank'></td><td></td></tr>" for _ in range(5))
    p10 = page(f"""<div class="kicker">Llene esta página</div><h2>Mis números importantes</h2>
      <p class="lede">Cópielos de sus tarjetas y facturas, no de una llamada ni de un mensaje.</p>
      <table><tr><th>Quién</th><th style="width:46%">Número</th></tr>
      <tr><td>Mi banco (detrás de mi tarjeta)</td><td></td></tr><tr><td>Mi tarjeta de crédito</td><td></td></tr>
      <tr><td>Mi doctor / farmacia</td><td></td></tr><tr><td>Mi compañía de envíos de dinero</td><td></td></tr>
      <tr><td><strong>Si tengo dudas, primero llamo a</strong></td><td></td></tr>{rows}</table>""", 11)
    steps = "".join(f'<div class="rule"><b class="n">{i}</b><div><strong>{esc(a)}</strong> {esc(b)}</div></div>'
                    for i, (a, b) in enumerate(C.IF_IT_HAPPENS, 1))
    p11 = page(f"""<div class="kicker">Si le pasa</div><h2>La primera hora</h2>
      <p class="lede">Actuar rápido le da la mejor oportunidad de recuperar el dinero.</p>{steps}""", 12)
    return [cover, p2, p3, p4, p5, p6a, p6b, p7, p8, p9, p10, p11, fridge_page(13)] + wallet_pages()


def review_doc() -> str:
    calls = [f"- [ ] {t}" + (" · **ATTORNEY REVIEW**" if a else "") for t, _, _, a in C.CALLS]
    return "\n".join([
        f"# Review checklist: {C.TITLE}", "",
        "Nothing from `launch/dinero-simple/mayores/` is printed, shared or listed until every box is ticked. "
        "Edit `contenido.py`, never the PDFs, then run `python3 launch/dinero-simple/mayores/build_mayores.py --pdf`.", "",
        "## Sign-off",
        "- [ ] **Native-speaker review** of every page (machine-written Spanish). Check that \"usted\" reads warm, not stiff, "
        "for Mexican, Central American and Caribbean grandparents, and that words like giro, clave, envío and peaje are the ones they use.",
        "- [ ] **ATTORNEY REVIEW:** a licensed immigration attorney or DOJ-accredited representative reads the items below, "
        "the week the guide goes out.",
        "- [ ] **Read it aloud with one abuelo or abuela** before the first print. If they stumble on a sentence, shorten it.",
        "- [ ] **Print test** at 100% on Letter paper: wallet cards line up front to back.", "",
        "## ATTORNEY REVIEW items", *[f"- [ ] {x}" for x in C.ATTORNEY_ITEMS], "",
        "## Facts to check",
        "- [ ] Each official line still answers in Spanish: FTC 1-877-382-4357 (and ReporteFraude.ftc.gov), Elder Fraud "
        "Hotline 1-833-372-8311, Social Security 1-800-772-1213, Medicare 1-800-633-4227, Do Not Call 1-888-382-1222.",
        "- [ ] 7726 still accepts forwarded texts from the big US carriers.",
        "- [ ] The EOIR list of recognized organizations and accredited representatives is still at justice.gov/eoir.",
        "- [ ] No real company, bank or remittance brand is named anywhere.", "",
        "## Calls page", *calls, "",
    ]) + "\n"


def to_pdf(src: Path, out: Path) -> None:
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();"
          "await p.goto('file://" + str(src) + "');await p.pdf({path:'" + str(out) + "',"
          "format:'Letter',printBackground:true,preferCSSPageSize:true});await b.close();})();")
    subprocess.run(["node", "-e", js], check=True, env={**os.environ, "NODE_PATH": "/opt/node22/lib/node_modules"})


def main() -> None:
    (DS / "REVIEW_CHECKLIST_MAYORES.md").write_text(review_doc())
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir()
    docs = {"Guia-Estafas-Papas-y-Abuelos": doc(C.TITLE, booklet()),
            "Lista-del-Refrigerador": doc("Lista del refrigerador", [fridge_page(None)]),
            "Tarjetas-de-Bolsillo": doc("Tarjetas de bolsillo", wallet_pages())}
    for name, text in docs.items():
        src = DIST / f"{name}.html"
        src.write_text(text)
        if "--pdf" in sys.argv:
            to_pdf(src, DIST / f"{name}.pdf")
    for p in sorted(DIST.iterdir()):
        print(f"{p.name:38s} {p.stat().st_size // 1024:>6} KB")


if __name__ == "__main__":
    main()
