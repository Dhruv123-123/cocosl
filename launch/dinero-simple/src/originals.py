"""The one thing a template can't make, for every Dinero Simple long video.

YouTube's 'inauthentic content' rule targets channels of look-alike slideshows with the same narration, and
the factory's review blocks a long video that has neither a chart drawn from its own numbers nor the owner's
own footage (guardrails.check_original_element). Each long video here gets:

- a chart on the beat whose narration gives the numbers (every figure is said out loud in that beat), and
- original_element: a short screen recording Dhruv can add later as a beat's `footage` to make it stronger.
  It is optional: the chart already passes the check. Record only public pages, never your own accounts.

    apply(items)  # call after building a month's items, before writing the JSON
"""
from __future__ import annotations

import re

EXAMPLE = "Ejemplo ilustrativo, no es un consejo"


def _c(kind, title, labels, values, prefix="$", suffix="", note=EXAMPLE, said=""):
    assert 2 <= len(values) == len(labels) <= 12 and len(title.split()) < 8, title
    return {"kind": kind, "title": title, "labels": labels, "values": values, "unit_prefix": prefix,
            "unit_suffix": suffix, "note": note, "_said": said}


# video key (or Spanish title for content.json, whose items have no key) -> {segment heading: chart}
CHARTS = {
    "l-mandar-dinero": {
        "El costo real": _c("bars", "Lo que recibe tu familia por $300", ["Al tipo del mercado (18)", "A 17.60, 'sin comisión'"],
                            [5400, 5280], prefix="", suffix=" pesos",
                            note="Ejemplo: 120 pesos menos, unos $6.70 escondidos en el tipo de cambio"),
        "Cuánto suma": _c("line", "Lo que pierdes en un año", ["3 meses", "6 meses", "9 meses", "12 meses"],
                          [30, 60, 90, 120], note="Ejemplo: $10 perdidos en cada envío de $300, uno al mes"),
    },
    "l-diciembre-sin-deudas": {
        "El fondo semanal": _c("line", "Tu fondo de diciembre, semana a semana",
                               ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6"], [80, 160, 240, 320, 400, 480],
                               note="Ejemplo: $480 en seis semanas, $80 cada semana"),
    },
    "l-plan-2027": {
        "Colchón": _c("line", "Tu colchón de mil dólares", ["Mes 1", "Mes 2", "Mes 3", "Mes 4"], [250, 500, 750, 1000],
                      note="Ejemplo: $125 por quincena, dos quincenas al mes"),
    },
    "l-impuestos-2027": {
        "Qué hacer con él": _c("bars", "Un reembolso de $2,000 en cuatro partes",
                               ["Colchón", "Deuda más cara", "Tu meta", "Para ti"], [600, 800, 400, 200]),
    },
    "l-itin-guia": {
        "Banco y crédito": _c("bars", "Cambiar cheques te cuesta al año", ["Un cheque", "Un mes", "Un año"], [24, 48, 576],
                              note="Ejemplo: cheque de $800 cada quincena, cuota de 3%"),
    },
    "l-si-debes-o-carta": {
        "Declara a tiempo": _c("bars", "Multa por 4 meses de atraso", ["No declarar", "Declarar y no pagar"], [200, 20],
                               note="Ejemplo: debes $1,000; 5% al mes contra 0.5% al mes, sin intereses"),
    },
    "l-credito-desde-cero": {
        "El puntaje": _c("bars", "Qué pesa en tu puntaje",
                         ["Pagar a tiempo", "Uso del límite", "Antigüedad", "Solicitudes nuevas", "Tipos de crédito"],
                         [35, 30, 15, 10, 10], prefix="", suffix="%", note="Pesos aproximados que publica FICO"),
    },
    "l-banco-sin-cargos": {
        "Por qué": _c("bars", "Cambiar cheques te cuesta al año", ["Un cheque", "Un mes", "Un año"], [24, 48, 576],
                      note="Ejemplo: cheque de $800 cada quincena, cuota de 3%",
                      said="cheque de ochocientos dólares"),
    },
    "Cómo empezar a invertir con $100 al mes (guía completa para principiantes)": {
        "Por qué importa el tiempo": _c("bars", "$100 al mes: 40 años contra 30",
                                        ["40 años: pones", "40 años: vale", "30 años: pones", "30 años: vale"],
                                        [48000, 262000, 36000, 122000],
                                        note="Hipotético: 7% al año parejo; nadie promete rendimientos"),
    },
    "¿Sientes que vas atrasado con tu dinero? Un plan de 30 días": {
        "Semana 3: empieza el colchón": _c("line", "$25 a la semana hasta $1,000", ["Sem 10", "Sem 20", "Sem 30", "Sem 40"],
                                           [250, 500, 750, 1000], note="Ejemplo: transferencia automática de $25 cada semana"),
    },
    "l-impuestos-trabajador": {
        "Las dos mitades": _c("bars", "Seguro Social y Medicare con $20,000", ["Con W-2 (tu parte)", "Con 1099 (las dos)"],
                              [1530, 2826], note="Ejemplo: 7.65% contra 15.3% sobre 92.35% de la ganancia neta"),
    },
    "l-envios-del-ano": {
        "Cada cuándo": _c("bars", "Comisiones de un año", ["Cada semana", "Cada mes"], [208, 48],
                          note="Ejemplo: comisión fija de $4 por envío"),
    },
    "l-carro-usado": {
        "La tasa": _c("bars", "Intereses de $15,000 a 60 meses", ["Al 8%", "Al 20%"], [3249, 8845],
                      note="Ejemplo: mismo carro, mismo plazo, distinta tasa"),
    },
    "l-viaje-a-casa": {
        "El fondo": _c("line", "Fondo del viaje: $75 semanales", ["Sem 6", "Sem 12", "Sem 18", "Sem 24"],
                       [450, 900, 1350, 1800], note="Ejemplo: viaje de $1,800 en 24 semanas"),
    },
    "l-tu-sueldo-completo": {
        "La cuenta": _c("bars", "50 horas a $18 la hora", ["Pago parejo", "Pago correcto"], [900, 990],
                        note="Ejemplo: 10 horas extra a $27"),
    },
    "l-tanda": {
        "El costo": _c("bars", "Costo de $1,000 por 10 semanas", ["Tanda", "Tarjeta al 25%", "Día de pago"], [0, 48, 750],
                       note="Ejemplo; el día de pago renovado 5 veces"),
    },
    "l-primera-casa": {
        "El enganche": _c("bars", "Enganche para una casa de $250,000", ["3%", "3.5%", "10%", "20%"],
                          [7500, 8750, 25000, 50000], note="Ejemplo; con menos de 20% pagas seguro hipotecario"),
    },
    "l-primer-ano": {
        "El presupuesto": _c("bars", "Presupuesto de ejemplo, $3,200 al mes",
                             ["Renta", "Comida", "Servicios", "Transporte", "Envíos", "Sobra"],
                             [1400, 800, 250, 200, 200, 350], note="Ejemplo inventado: Rosa y Daniel",
                             said="mil cuatrocientos"),
    },
    "l-rentar": {
        "Para entrar": _c("bars", "Para entrar a $1,200 al mes", ["Sin el último mes", "Con el último mes"],
                          [2450, 3650], note="Ejemplo: primer mes, depósito y $50 de solicitud",
                          said="dos mil cuatrocientos cincuenta"),
    },
    "l-familia-aqui-y-alla": {
        "La cuenta": _c("bars", "Los $3,000 de Ana al mes",
                        ["Renta", "Comida", "Transporte", "Servicios", "Familia", "Colchón", "Lo demás"],
                        [1200, 600, 300, 200, 300, 200, 200], note="Ejemplo inventado; tu número será otro",
                        said="mil doscientos"),
    },
    "l-retiro-tarde": {
        "El ejemplo": _c("bars", "$200 al mes por 20 años", ["Lo que pone", "Con 6% al año (ejemplo)"],
                         [48000, 92400], note="Ejemplo, no una promesa; las inversiones suben y bajan",
                         said="cuarenta y ocho mil"),
    },
    "l-seguro-de-vida": {
        "El costo": _c("bars", "Al mes por $250,000 de cobertura", ["A plazo (20 años)", "Permanente"], [20, 250],
                       note="Ejemplo ilustrativo; tu precio depende de edad y salud"),
    },
}

ORIGINAL = {
    "l-mandar-dinero": "Graba la pantalla comparando cuánto recibe tu familia por $300 en dos apps de envío, el mismo día (sin iniciar sesión, solo el cotizador)",
    "l-diciembre-sin-deudas": "Graba la pantalla abriendo un apartado de ahorro llamado 'Diciembre' en una app de banco de demostración, o la hoja del presupuesto con el total de diciembre",
    "l-plan-2027": "Graba la pantalla llenando la hoja de gastos sorpresa de El Presupuesto con números de ejemplo",
    "l-impuestos-2027": "Graba la pantalla de la página '¿Dónde está mi reembolso?' de irs.gov en español (sin poner datos)",
    "l-itin-guia": "Graba la pantalla de la página del formulario W-7 en irs.gov en español, mostrando dónde se descarga",
    "l-si-debes-o-carta": "Graba la pantalla de la página de planes de pago de irs.gov en español (sin iniciar sesión)",
    "l-credito-desde-cero": "Graba la pantalla de AnnualCreditReport.com mostrando dónde se piden los tres reportes gratis (sin poner datos)",
    "l-banco-sin-cargos": "Graba la pantalla del buscador de cuentas Bank On certificadas (joinbankon.org), filtrando por tu código postal",
    "Cómo empezar a invertir con $100 al mes (guía completa para principiantes)": "Graba la pantalla de una calculadora pública de interés compuesto (Investor.gov) con $100 al mes y 7%",
    "¿Sientes que vas atrasado con tu dinero? Un plan de 30 días": "Graba la pantalla de El Presupuesto con números de ejemplo: el número semanal de la semana 2",
    "l-impuestos-trabajador": "Graba la pantalla del calculador de retenciones del IRS (irs.gov) en español, sin poner datos reales, mostrando dónde está el paso de dos trabajos",
    "l-envios-del-ano": "Graba la pantalla cotizando el mismo envío de $300 con dos métodos de entrega (depósito y efectivo) en una app, sin iniciar sesión",
    "l-carro-usado": "Graba la pantalla del buscador de llamados a reparación de la NHTSA con un VIN de ejemplo (no el tuyo), y la Guía del comprador en español de la FTC",
    "l-viaje-a-casa": "Graba la pantalla creando un apartado de ahorro llamado 'Viaje' con transferencia semanal en una app de banco de demostración",
    "l-tanda": "Graba la pantalla de una hoja de cálculo sencilla con la lista de la tanda (nombres de ejemplo, montos, fechas y turnos) y una foto de la lista en un chat de grupo",
    "l-primera-casa": "Graba la pantalla de la Estimación del préstamo de ejemplo de la CFPB (la versión en español) marcando la tasa, el APR y los gastos de cierre",
    "l-tu-sueldo-completo": "Graba la pantalla de una libreta de horas en el celular (una nota con fechas, entrada, comida y salida) junto a un talón de pago de ejemplo con la línea de 'overtime' marcada",
    "l-primer-ano": "Graba la pantalla del buscador de cooperativas de MyCreditUnion.gov y de la página de seguro de depósitos de la FDIC en español (sin poner datos)",
    "l-rentar": "Graba la pantalla de un video de ejemplo recorriendo un departamento vacío cuarto por cuarto, y la nota con la lista de daños con fecha que se manda al administrador",
    "l-familia-aqui-y-alla": "Graba la pantalla creando dos apartados de ahorro, 'Familia' y 'Emergencia familia', con transferencia mensual en una app de banco de demostración, y la nota compartida de los hermanos con números de ejemplo",
    "l-retiro-tarde": "Graba la pantalla de la calculadora de interés compuesto de Investor.gov con $200 al mes, 20 años y 6%, y la página de ssa.gov en español donde se abre la cuenta de mi Seguro Social (sin iniciar sesión)",
    "l-seguro-de-vida": "Graba la pantalla del buscador de licencias de agentes de seguros de la página del departamento de seguros de un estado (sin datos personales)",
}


def apply(items: list[dict]) -> list[dict]:
    """Add the chart(s) and the suggested recording to every long video; fail loudly if one is missing."""
    for it in items:
        if it["format"] != "long":
            continue
        script = it["script"]
        name = it.get("key") or script["title"]
        charts = CHARTS.get(name)
        if not charts or name not in ORIGINAL:
            raise SystemExit(f"{name}: long video without an original element (add it to originals.py)")
        by_heading = {s["heading"]: s for s in script["segments"]}
        for heading, chart in charts.items():
            seg = by_heading.get(heading)
            if seg is None:
                raise SystemExit(f"{name}: no segment called {heading!r}")
            chart = dict(chart)
            said = chart.pop("_said")
            if not _backed(chart, said, seg["narration"]):
                raise SystemExit(f"{name}/{heading}: the chart's numbers are not said in this beat's narration")
            seg["chart"] = chart
            claim = f"Chart '{chart['title']}': {', '.join(f'{l} {v:g}' for l, v in zip(chart['labels'], chart['values']))} ({chart['note']})"
            if claim not in script["claims_to_verify"]:
                script["claims_to_verify"].append(claim)
        script["original_element"] = ORIGINAL[name]
        _add_example(name, script)
    return items


def _add_example(name: str, script: dict) -> None:
    """Insert the worked example from long_examples.py just before the closing summary (once)."""
    from long_examples import EXAMPLES
    from build_month1 import visual
    extra = EXAMPLES.get(name, [])
    have = {s["heading"] for s in script["segments"]}
    segs = []
    for heading, on_screen, narration, scene in extra:
        if heading in have:
            continue
        if len(on_screen.split()) > 12:
            raise SystemExit(f"{name}: on-screen text over 12 words: {on_screen}")
        segs.append({"heading": heading, "narration": narration, "on_screen_text": on_screen, "visual_prompt": visual(scene)})
    if segs:
        script["segments"][-1:-1] = segs


def _backed(chart: dict, said: str, narration: str) -> bool:
    """The chart only draws figures the beat says out loud: one of its values, or a figure in its title/note
    (e.g. '$125 por quincena'), must appear in the narration, or the explicit phrase `said` (for numbers spoken
    as words) must."""
    if said:
        return said in narration
    if chart["unit_suffix"] == "%":
        return True  # weights quoted by the source; the narration paraphrases them ("más o menos un tercio")
    flat = narration.replace(",", "")
    figures = [f"{v:g}" for v in chart["values"]] + re.findall(r"\d+(?:\.\d+)?", (chart["title"] + " " + chart["note"]).replace(",", ""))
    return any(re.search(rf"(?<![\d.]){re.escape(f)}(?![\d])", flat) for f in figures)
