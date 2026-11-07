"""Paid 2-hour test for a native Spanish reviewer, taken from the lean launch set, with planted problems.

    python3 launch/dinero-simple/reviewer/build_test.py          # dist/Prueba-Pagada-Revision.html + ANSWER_KEY.md
    python3 launch/dinero-simple/reviewer/build_test.py --pdf    # also the PDF to send

The test is real copy from the lean set (4 welcome emails, the Kit's product page, 2 Shorts), about 1,900 words:
1.5-2 hours for a careful native edit with notes. Twelve problems are planted in this copy only (the source files
are untouched): Spain-only words, calques of English, a register slip, agreement and spelling errors, stiff
phrasing, and one changed number the reviewer should flag, not fix. ANSWER_KEY.md lists them. **Never send the
key**; score the returned test with RUBRIC.md.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
sys.path.insert(0, str(DS / "review"))
import build_packets as bp  # noqa: E402

DIST = HERE / "dist"
FEE = "$45"            # flat fee for the test (about 2 hours at $20-25/hour)
HOURS = "1.5-2"

# The pieces, by their lean-packet title prefix, in the order the reviewer sees them.
PIECES = [
    "Correos de bienvenida · día 0",
    "Correos de bienvenida · día 1",
    "Correos de bienvenida · día 3",
    "Correos de bienvenida · día 7",
    "Sitio web · producto · el-kit-para-recortar-gastos",
    "Semana 1 · lun · short · El truco de las dos cuentas",
    "Semana 3 · mié · short · ¿Pagaste completo",
]

# (piece prefix, original text, planted text, kind, what a good reviewer does)
SEEDS = [
    ("Correos de bienvenida · día 0", "Una persona lee cada respuesta.",
     "Una persona lee cada respuesta, eventualmente.", "false friend",
     "'eventualmente' means 'possibly', not 'eventually': drop it or say 'tarde o temprano'"),
    ("Correos de bienvenida · día 1", "Revisa dos meses de tu cuenta",
     "Revisad dos meses de vuestra cuenta", "Spain Spanish (vosotros)", "back to 'Revisa ... tu cuenta' (tú, US Latino)"),
    ("Correos de bienvenida · día 1", "la tienda de apps de tu celular",
     "la tienda de apps de tu móvil", "Spain Spanish", "'móvil' → 'celular'"),
    ("Correos de bienvenida · día 1", "Son 26 pagos al año",
     "Son 24 pagos al año", "changed fact (flag, don't fix)",
     "every two weeks is 26 paychecks; the reviewer should FLAG the number, not silently rewrite it"),
    ("Correos de bienvenida · día 3", "Cuestan cero",
     "Son libres", "calque of 'free'", "'libre' isn't 'free of charge': 'Son gratis' / 'Cuestan cero'"),
    ("Correos de bienvenida · día 7", "Llegaste al final de la semana.",
     "Usted llegó al final de la semana.", "register slip (usted)", "the brand uses tú: 'Llegaste ...'"),
    ("Sitio web · producto · el-kit-para-recortar-gastos", "Nadie puede prometer eso.",
     "Nadie puede prometer eso, no hace sentido.", "calque ('make sense')",
     "'no tiene sentido', or just drop the added clause"),
    ("Sitio web · producto · el-kit-para-recortar-gastos", "Descarga inmediata.",
     "Descarga instantánea es disponible.", "ser/estar + calque", "'Descarga inmediata.' / 'Está disponible al instante.'"),
    ("Semana 1 · lun · short · El truco de las dos cuentas", "Abre una segunda cuenta de cheques sin comisiones.",
     "Abre una segunda cuenta corriente sin comisiones.", "Spain Spanish", "'cuenta corriente' → 'cuenta de cheques'"),
    ("Semana 1 · lun · short · El truco de las dos cuentas",
     "Voz: Si revisas tu saldo antes de comprar el almuerzo, tus cuentas están mal organizadas.",
     "Voz: Si revisas tu saldo antes de comprar el almuerzo, tus cuentas se encuentran en un estado de mala organización.",
     "stiff / robotic", "plain spoken Spanish: 'tus cuentas están mal organizadas'"),
    ("Semana 3 · mié · short · ¿Pagaste completo", "la fecha límite de pago",
     "el fecha límite de pago", "gender agreement", "'la fecha'"),
    ("Semana 3 · mié · short · ¿Pagaste completo", "Te explico por qué.",
     "Te explico por que.", "spelling (accent)", "'por qué'"),
]

INSTRUCTIONS_ES = f"""Esta es una prueba pagada ({FEE}, tarifa fija). Es texto real de una marca de finanzas personales en español
para latinos en Estados Unidos (registro de tú, español latinoamericano neutro con un toque mexicano-americano).
Tiempo esperado: {HOURS} horas.

1. Anota la hora en que empiezas y la hora en que terminas (abajo). Nos ayuda a calcular el resto del trabajo.
2. Corrige el texto para que suene como lo escribiría una persona latina que vive en EE. UU. Usa "sugerencias"
   o control de cambios, o escribe en la columna de comentarios.
3. Junto a cada cambio, una línea de por qué: error, suena traducido, no se entiende, registro equivocado.
4. No cambies cifras, fechas ni datos. Si algo parece incorrecto, márcalo con FLAG y explica por qué.
5. Al final, anota cualquier palabra que este público no usaría.
6. Lo que está entre llaves, como {{signoff}} o {{product_name}}, se llena solo: déjalo igual."""


def pieces() -> list[dict]:
    lean = bp.gather_lean()
    out = []
    for prefix in PIECES:
        e = next(x for x in lean.entries if x["title"].startswith(prefix))
        text = e["text"]
        for p, orig, planted, *_ in SEEDS:
            if p == prefix:
                assert text.count(orig) == 1, f"{prefix}: '{orig}' must occur exactly once"
                text = text.replace(orig, planted)
        out.append({"title": e["title"], "text": text})
    return out


def words(ps: list[dict]) -> int:
    return sum(len(p["text"].split()) for p in ps)


def test_html(ps: list[dict]) -> str:
    rows, n = [], 0
    for i, p in enumerate(ps, 1):
        rows.append(f'<tr class="entry"><td class="n">P-{i}</td><td colspan="2">{bp.esc(p["title"])}</td></tr>')
        for j, c in enumerate(bp.chunks(p["text"]), 1):
            n += 1
            rows.append(f'<tr><td class="n">P-{i}.{j}</td><td class="t">{bp.esc(c)}</td>'
                        f'<td class="c"><span class="ok"></span>OK &nbsp; <span class="ok"></span>Cambiar:</td></tr>')
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Prueba pagada de revisión</title>
<style>{bp.CSS}</style></head><body><section class="cover"><div class="meta">Dinero Simple · prueba pagada</div>
<h1>Prueba pagada de revisión de español</h1><div class="box" style="white-space:pre-wrap">{bp.esc(INSTRUCTIONS_ES)}</div>
<p><strong>Tamaño:</strong> {len(ps)} piezas, {words(ps):,} palabras.</p>
<p>Nombre: ____________________ &nbsp; Empecé: ________ &nbsp; Terminé: ________</p>
<p class="meta">English: this is a paid test ({FEE} flat). Edit the Spanish so it reads as written by a US Latino native
speaker (tú register). One-line reason per change. Don't change numbers or facts: FLAG them. Note your start and end
time. Leave {{placeholders}} as they are.</p></section>
<h2>Texto</h2><table><tr><th style="width:0.62in">#</th><th>Texto en español</th><th style="width:2.5in">Comentarios</th></tr>
{''.join(rows)}</table><h2>Palabras que este público no usaría</h2><p>______________________________________________</p>
</body></html>"""


def answer_key(ps: list[dict]) -> str:
    rows = "\n".join(f"| {i} | {p.split(' · ')[-1][:40]} | {kind} | “{planted}” | “{orig}” | {fix} |"
                     for i, (p, orig, planted, kind, fix) in enumerate(SEEDS, 1))
    return f"""# Answer key: paid review test (DON'T SEND)

Built by `build_test.py`. The test copy is {words(ps):,} words from the lean launch set, {HOURS} hours of careful
work. These {len(SEEDS)} problems were planted in the test copy only; the source files are correct. Score the
returned test with `RUBRIC.md`.

| # | Piece | Kind | Planted | Original | A good reviewer |
|---|---|---|---|---|---|
{rows}

Seed 4 (the 24 paychecks) tests rule 4 of the instructions: the right move is a FLAG, not a silent fix.
"""


def main() -> None:
    ps = pieces()
    DIST.mkdir(exist_ok=True)
    (DIST / "Prueba-Pagada-Revision.html").write_text(test_html(ps))
    (HERE / "ANSWER_KEY.md").write_text(answer_key(ps))
    if "--pdf" in sys.argv:
        bp.to_pdf(DIST / "Prueba-Pagada-Revision.html", DIST / "Prueba-Pagada-Revision.pdf")
    print(f"test: {len(ps)} pieces, {words(ps):,} words, {len(SEEDS)} planted problems")


if __name__ == "__main__":
    main()
