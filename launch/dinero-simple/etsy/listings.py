"""Spanish Etsy listing copy for the five Dinero Simple products.

Titles under 15 words (Etsy guidance, Apr 2026; see research/scouting/etsy-seo-playbook.md on PR #2) and <= 140 characters, a first line that says what the item is, exactly 13 tags of <= 20 characters (build_etsy.py checks both). Tags mix Spanish
with the English words US buyers type when they look for Spanish products ("spanish budget"). Every
description says nothing is shipped, that it's educational, and that AI tools helped (Etsy's creativity
standards). No links, codes or prompts to buy off Etsy.
"""
from __future__ import annotations

SHOP = "Dinero Simple"
CAT = "Paper & Party Supplies > Paper > Calendars & Planners (or Books > Guides, whichever Etsy suggests)"

GOOD_TO_KNOW = """BUENO SABER
- Es una DESCARGA DIGITAL. No se envía nada. Tus archivos aparecen en tu cuenta de Etsy (Compras y reseñas) justo después de pagar.
- La guía es un PDF (tamaño carta, se imprime bien en A4). La hoja de cálculo es un archivo .xlsx que abre en Microsoft Excel, Google Sheets (gratis: súbelo a Google Drive y ábrelo) y Apple Numbers.
- Todo está en español. La hoja viene llena con un ejemplo inventado para que veas cómo funciona. Las celdas amarillas son las que llenas tú.
- Solo para uso personal. Por favor, no revendas, compartas ni redistribuyas los archivos.
- Contenido educativo, no es asesoría financiera, fiscal, legal ni de inversión. Pensado para quien vive en Estados Unidos.
- Cómo se hizo: redactado con ayuda de herramientas de IA y verificado por una persona de Dinero Simple. La IA también ayudó con el diseño.
- ¿Una pregunta o algo no funciona? Escríbenos por mensajes de Etsy."""

MORE = f"""MÁS EN LA TIENDA
Busca "{SHOP}" en Etsy para los otros kits en español, o llévate los cuatro en El Paquete Dinero Simple."""


def _desc(what: str, hook: str, get: list[str], how: list[str]) -> str:
    g = "\n".join(f"- {x}" for x in get)
    h = "\n".join(f"{i}. {x}" for i, x in enumerate(how, start=1))
    return f"{what}\n\n{hook}\n\nQUÉ INCLUYE\n{g}\n\nCÓMO FUNCIONA\n{h}\n\n{GOOD_TO_KNOW}\n\n{MORE}"


LISTINGS: list[dict] = [
    dict(slug="recorte-de-gastos", name="El Kit para Recortar Gastos", price=5.00, category=CAT,
         what="Este Kit para Recortar Gastos es una descarga digital en español: una guía en PDF de 9 páginas y una hoja de cálculo para Excel y Google Sheets.",
         title="Kit para Recortar Gastos en Español, Lista de Suscripciones y Guiones para Bajar Cuentas",
         tags=["spanish budget", "en español", "recortar gastos", "ahorrar dinero", "cancelar suscripcion",
               "presupuesto mensual", "finanzas personales", "hoja de calculo", "google sheets", "excel template",
               "spanish planner", "bill negotiation", "money saving"],
         pitch="Encuentra cada cobro que se repite y baja las cuentas que te quedas.",
         chips=["Descarga inmediata", "Guía PDF", "Excel + Google Sheets", "En español"],
         inside_title="9 páginas de guía + hoja de control",
         get=["Guía en PDF de 9 páginas: los cinco lugares donde se esconden los cobros, la regla de las cuatro decisiones, cómo cancelar para que no vuelva y 7 guiones palabra por palabra",
              "Hoja de cálculo (.xlsx): revisión con costo anual, registro de llamadas con recordatorio antes de que acabe una promoción, y tu ahorro total al año",
              "Hoja para imprimir"],
         how=["Revisa los cinco lugares donde se esconden los cobros.", "Decide una sola cosa por cobro: quedarte, cancelar, bajar de plan o negociar.",
              "Usa los guiones con las cuentas que te quedas.", "Manda lo que ahorres a tu ahorro o a tu deuda."],
         hook="Las suscripciones no se sienten caras a $9.99 al mes. Se sienten caras a $120 al año, por seis. Este kit en español te ayuda a encontrar cada cobro que se repite en unos 10 minutos, cancelar lo que no usas y bajar las cuentas que te quedas.",
         hero=[1, 3, 6], grid=[1, 2, 3, 4, 5, 6, 7, 8]),
    dict(slug="presupuesto-20-minutos", name="El Presupuesto de 20 Minutos", price=12.00, category=CAT,
         what="Esta plantilla de presupuesto semanal es una descarga digital en español: una guía en PDF de 14 páginas y una hoja de cálculo para Excel y Google Sheets.",
         title="Plantilla de Presupuesto Semanal en Español, Excel y Google Sheets, Guía de 14 Páginas",
         tags=["spanish budget", "presupuesto familiar", "en español", "plantilla excel", "google sheets",
               "finanzas personales", "budget template", "spanish planner", "plan de ahorro", "control de gastos",
               "budget spreadsheet", "planificador semanal", "presupuesto semanal"],
         pitch="Un número semanal para gastar y un plan automático para todo lo demás.",
         chips=["Descarga inmediata", "Guía de 14 páginas", "Excel + Google Sheets", "En español"],
         inside_title="14 páginas de guía + plantilla",
         get=["Guía en PDF de 14 páginas: tu número semanal, la revisión de 20 minutos, fondos de ahorro para gastos que llegan cada año y un plan para tus deudas",
              "Plantilla de presupuesto (.xlsx) en español con revisión semanal, fondos de previsión y plan de deudas",
              "Ejemplos con números para que veas cómo se usa"],
         how=["Anota lo que entra y tus gastos fijos.", "La hoja te da tu número semanal para gastar.",
              "Una vez por semana, 20 minutos: revisas y ajustas.", "Pon en automático tus fondos y tus pagos."],
         hook="Un presupuesto en español que no te pide anotar cada café. Pones en automático tus cuentas, tu ahorro y tus metas, y te queda un solo número semanal para gastar. Una revisión de 20 minutos a la semana y listo.",
         hero=[1, 4, 7], grid=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
    dict(slug="fecha-sin-deudas", name="Tu Fecha Sin Deudas", price=17.00, category=CAT,
         what="Este planificador para pagar deudas es una descarga digital en español: una guía en PDF de 10 páginas y una hoja de cálculo para Excel y Google Sheets.",
         title="Planificador para Pagar Deudas en Español, Método Bola de Nieve, Excel y Google Sheets",
         tags=["debt payoff", "pagar deudas", "en español", "bola de nieve", "metodo avalancha",
               "spanish budget", "debt tracker", "salir de deudas", "google sheets", "excel template",
               "finanzas personales", "debt snowball", "spanish planner"],
         pitch="Pon todas tus deudas en una hoja y ve el mes exacto en que terminas.",
         chips=["Descarga inmediata", "Guía PDF", "Excel + Google Sheets", "En español"],
         inside_title="10 páginas de guía + planificador",
         get=["Guía en PDF de 10 páginas: tu lista de deudas, cómo elegir método, dónde encontrar tu pago extra, cómo bajar tus tasas y qué hacer si el plan no alcanza",
              "Planificador (.xlsx) en español: compara avalancha y bola de nieve con tus números, calcula tu fecha sin deudas y el interés total, y trae calculadoras de transferencia de saldo y consolidación",
              "Hoja de avance para imprimir y un calendario de pagos"],
         how=["Anota cada deuda: saldo, tasa y pago mínimo.", "Elige avalancha o bola de nieve. La hoja te muestra los dos.",
              "Paga el mínimo en todas y el extra a una sola.", "Cada mes, actualiza los saldos y mira cómo se acerca tu fecha."],
         hook="¿Cuándo terminas de pagar tus deudas? Este planificador en español pone todas tus deudas en un solo lugar, compara el método avalancha y el de bola de nieve con tus números, y te dice el mes exacto en que quedas libre.",
         hero=[1, 4, 6], grid=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
    dict(slug="invertir-con-100", name="Empieza a Invertir con $100 al Mes", price=19.00, category=CAT,
         what="Esta guía de inversión para principiantes es una descarga digital en español: una guía en PDF de 12 páginas y calculadoras para Excel y Google Sheets.",
         title="Guía de Inversión para Principiantes en Español, Calculadoras en Excel y Google Sheets",
         tags=["invertir dinero", "en español", "spanish finance", "roth ira", "401k",
               "fondos indice", "investing guide", "guia principiantes", "calculadora interes", "google sheets",
               "excel template", "finanzas personales", "retirement planning"],
         pitch="El orden para empezar a invertir y calculadoras para ver tus números.",
         chips=["Descarga inmediata", "Guía de 12 páginas", "5 calculadoras", "En español"],
         inside_title="12 páginas de guía + calculadoras",
         get=["Guía en PDF de 12 páginas: el orden para empezar (match, colchón, deudas caras, Roth IRA, fondo índice), cómo abrir tu cuenta y qué hacer cuando el mercado baja",
              "Calculadoras (.xlsx) en español: crecimiento, comisiones, match del 401(k), Roth o Traditional y aportaciones",
              "Lista de pasos en la hoja para marcar mientras avanzas"],
         how=["Sigue el orden de la guía.", "Pon tus números en las calculadoras.",
              "Abre tu cuenta y pon tu aportación en automático.", "Revisa una vez al año, no cada día."],
         hook="No necesitas mucho dinero para empezar a invertir. Necesitas el orden correcto y ponerlo en automático. Esta guía en español te lleva paso a paso, con calculadoras para ver cuánto puede crecer tu dinero y cuánto te cuestan las comisiones. Ejemplos hipotéticos, nadie te promete rendimientos.",
         hero=[1, 3, 5], grid=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
    dict(slug="paquete", name="El Paquete Dinero Simple", price=29.00, category=CAT,
         what="Este paquete de finanzas personales es una descarga digital en español: los cuatro kits de Dinero Simple (guías en PDF y hojas de cálculo) y un mapa de inicio.",
         bundle_of=["recorte-de-gastos", "presupuesto-20-minutos", "fecha-sin-deudas", "invertir-con-100"],
         title="Paquete de Finanzas Personales en Español: Presupuesto, Deudas, Ahorro e Inversión",
         tags=["spanish budget", "en español", "presupuesto mensual", "pagar deudas", "invertir dinero",
               "finanzas personales", "budget bundle", "spanish planner", "google sheets", "excel template",
               "plan de ahorro", "money bundle", "regalo practico"],
         pitch="Los cuatro kits en español: gastos, presupuesto, deudas e inversión.",
         chips=["Descarga inmediata", "4 guías + 4 hojas", "Excel + Google Sheets", "En español"],
         inside_title="Los 4 kits que recibes",
         get=["El Kit para Recortar Gastos: guía + hoja de control",
              "El Presupuesto de 20 Minutos: guía + plantilla",
              "Tu Fecha Sin Deudas: guía + planificador",
              "Empieza a Invertir con $100 al Mes: guía + calculadoras",
              "Mapa de inicio en PDF con un plan de 30 días"],
         how=["Abre el mapa de inicio.", "Semana 1: recorta gastos.", "Semana 2: arma tu presupuesto.",
              "Semanas 3 y 4: tu plan de deudas y tu primer paso para invertir."],
         hook="Los cuatro kits de Dinero Simple en un solo paquete, todos en español: recortar gastos, un presupuesto semanal, un plan para salir de deudas y una guía para empezar a invertir. Comprados por separado cuestan $53.",
         hero=[], grid=[]),
]

for _it in LISTINGS:
    _it["description"] = _desc(_it["what"], _it["hook"], _it["get"], _it["how"])
BY_SLUG = {it["slug"]: it for it in LISTINGS}
