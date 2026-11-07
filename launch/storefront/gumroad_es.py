"""Dinero Simple: the whole Gumroad storefront in Spanish (profile + one product page per product).

    python launch/storefront/build_storefront.py      # writes dist/dinero-simple/GUMROAD_ES.md with the rest

Every field is ready to paste into Gumroad: nombre, enlace corto, precio, resumen, descripción, puntos clave, texto
del botón, mensaje de agradecimiento (Gumroad > producto > "Receipt"/"Thank you"), etiquetas y venta cruzada.
Payment and product links are placeholders ([ENLACE: ...]); nothing is uploaded or published.

The five guide kits (Recortar Gastos, Presupuesto de 20 Minutos, Fecha Sin Deudas, Invertir con $100, Paquete) are
written from their LISTING.md files on the Dinero Simple branch (PR #11); the four printables come from
launch/brandshop/dinero_simple.py. NATIVE REVIEW PENDING: a fluent Spanish speaker reads all of it before it goes up.
"""
from __future__ import annotations

REVIEW = ("> **REVISIÓN PENDIENTE (NATIVE REVIEW PENDING).** Nada de esta página se publica hasta que una persona que "
          "hable español con fluidez lo lea completo y firme REVIEW_CHECKLIST_ES.md. Los enlaces entre corchetes son "
          "marcadores: cámbialos por los de tu tienda.")

AVISO = ("Contenido educativo, no es asesoría financiera, fiscal ni legal. Hecho con ayuda de herramientas de IA para el "
         "borrador y el diseño, y revisado por una persona.")

FIRMA = "¿Preguntas? Contesta este correo; lo lee una persona. El equipo de Dinero Simple"

PERFIL = dict(
    nombre="Dinero Simple",
    usuario="dinerosimple",
    bio="Herramientas de dinero en español para latinos en EE. UU.: presupuesto, deudas, crédito, envíos e inversión. No es asesoría financiera.",
    acerca=("Dinero Simple hace guías y plantillas en español para quien vive en Estados Unidos. Nada de 40 categorías "
            "ni apps con suscripción: un número semanal para gastar, un plan con fecha para tus deudas, tu crédito desde "
            "cero (también con ITIN) y cuánto llega de verdad cuando envías dinero a tu familia. Cada guía trae su hoja "
            "de cálculo que hace las cuentas por ti. " + AVISO),
    boton_seguir="Recibe un correo cuando haya un kit nuevo",
    pie="Pagos seguros con Gumroad. Descarga inmediata. ¿Algo no funciona? Escríbenos y lo arreglamos.",
)

SECCIONES = [
    ("Empieza aquí", "Si es tu primera vez: recorta lo que no usas y dale un plan a lo que queda."),
    ("Para la familia", "Para imprimir y llenar en familia: el presupuesto de la casa, los envíos y el crédito."),
    ("Deudas e inversión", "Ponle fecha a tus deudas y después pon a trabajar ese pago."),
    ("Todo junto", "Los cuatro kits en una descarga, por menos."),
]

# One dict per Gumroad product. Names match the catalog (launch/catalog/build_catalog.py) exactly.
PRODUCTOS = [
    dict(nombre="El Kit para Recortar Gastos", enlace="recortar-gastos", precio=5,
         titulo="El Kit para Recortar Gastos: encuentra y cancela cada suscripción en una hora",
         resumen="Encuentra cada cobro que se repite en 10 minutos, cancela lo que no usas y baja las cuentas que te quedas con guiones palabra por palabra.",
         gancho="¿Cuánto pagas al mes en cosas que ya ni usas? Casi nadie lo sabe, porque la mitad de los cobros no salen con su nombre en el estado de cuenta.",
         incluye=["**La guía (PDF):** dónde buscar cada cobro que se repite, una decisión por cobro y siete guiones palabra por palabra",
                  "**La hoja de cálculo (.xlsx):** tu lista de cobros con tu ahorro al año, al mes y a la semana; funciona en Google Sheets, Excel y Numbers"],
         puntos=["Encuentra las suscripciones de Apple, Google, PayPal y Amazon que no salen en tu estado de cuenta.",
                 "Una decisión por cobro: me quedo, cancelar, bajar de plan o negociar.",
                 "Siete guiones palabra por palabra, incluido qué decir cuando te dicen que no.",
                 "Te toma como una hora. Repítelo cada seis meses."],
         boton="Quiero recortar gastos",
         gracias=["Descarga el zip y abre la guía. Las páginas 3 a 5 toman unos 15 minutos.",
                  "Abre la hoja, mira el ejemplo, borra las celdas amarillas y empieza tu lista.",
                  "Aparta una hora esta semana en tu calendario: \"Recortar gastos\"."],
         etiquetas=["suscripciones", "cancelar suscripciones", "ahorrar dinero", "presupuesto", "finanzas personales",
                    "negociar cuentas", "hoja de cálculo", "Google Sheets", "en español"],
         archivos="un .zip con la guía en PDF y la hoja de cálculo .xlsx"),
    dict(nombre="El Presupuesto de 20 Minutos", enlace="presupuesto-20-minutos", precio=12,
         titulo="El Presupuesto de 20 Minutos: un sistema semanal para tu dinero + hoja de cálculo",
         resumen="Un presupuesto que armas una noche y manejas en 20 minutos a la semana. Guía de 14 páginas + hoja de cálculo con plan para salir de deudas.",
         gancho=("Casi todos los presupuestos fallan porque te piden 50 decisiones chiquitas al día. Este te pide una "
                 "decisión al mes y una revisión de 20 minutos a la semana. Tu sueldo neto se divide en cuatro líneas: "
                 "gastos fijos, fondos para lo irregular, metas que se pagan primero y un solo número semanal para gastar."),
         incluye=["**La guía (PDF, 14 páginas):** el método en 6 pasos, un ejemplo completo con números (persona ficticia), cómo ponerlo en automático con tu banco, la rutina semanal, avalancha contra bola de nieve, qué hacer si tus ingresos cambian, en pareja o si ayudas a tu familia",
                  "**La hoja de cálculo (.xlsx):** Configuración, Plan mensual, Revisión semanal, Fondos de previsión, Pago de deudas y Calendario de pagos. Las celdas amarillas son tuyas; lo demás se calcula solo"],
         puntos=["Lo armas una noche; después son 20 minutos a la semana.",
                 "Un solo número semanal en lugar de una docena de categorías.",
                 "Fondos para los gastos \"sorpresa\" que no son sorpresa: el carro, regalos, renovaciones.",
                 "Tu fecha sin deudas, con avalancha y bola de nieve lado a lado.",
                 "Funciona con cualquier banco. Sin app y sin suscripción."],
         boton="Quiero mi presupuesto",
         gracias=["Descarga los archivos y lee el método y los 6 pasos al principio de la guía (unos 10 minutos).",
                  "Abre la hoja, mira el ejemplo de Daniela y cambia las celdas amarillas por tus números.",
                  "Pon una alarma semanal de 20 minutos: \"Revisión de dinero\"."],
         etiquetas=["presupuesto", "finanzas personales", "plantilla de presupuesto", "hoja de cálculo",
                    "salir de deudas", "ahorro", "Google Sheets", "en español"],
         archivos="la guía en PDF y la hoja de cálculo .xlsx"),
    dict(nombre="Tu Fecha Sin Deudas", enlace="fecha-sin-deudas", precio=17,
         titulo="Tu Fecha Sin Deudas: el planificador que le pone fecha al día en que ya no debes nada",
         resumen="Ponle fecha real al día en que ya no debes nada. Hasta 10 deudas, avalancha o bola de nieve, y calculadoras para saber si una transferencia de saldo o un préstamo de consolidación de verdad te conviene.",
         gancho="\"Algún día\" no es un plan. Escribe tus deudas una vez y la hoja te dice el mes y el año en que terminas, y cuánto vale cada pago extra.",
         incluye=["**La guía (PDF):** cómo elegir el orden, qué hacer con los mínimos que ni cubren el interés y una página honesta para cuando el plan no alcanza",
                  "**La hoja de cálculo (.xlsx):** hasta 10 deudas, avalancha, bola de nieve o tu propio orden, y las calculadoras de transferencia de saldo y consolidación"],
         puntos=["Tu fecha sin deudas exacta, mes y año.",
                 "Avalancha, bola de nieve o tu orden, con un clic.",
                 "Te dice si una transferencia de saldo o un préstamo de consolidación de verdad te ahorra dinero.",
                 "Marca en rojo los mínimos que ni cubren el interés.",
                 "Una página honesta para cuando el plan no alcanza, con opciones y focos rojos."],
         boton="Quiero mi fecha",
         gracias=["Descarga el zip y abre la guía. El Paso 1 toma unos 20 minutos.",
                  "Abre la hoja, mira el ejemplo de Andrea, borra las celdas amarillas y escribe tus deudas.",
                  "Pon tu fecha sin deudas donde la veas todos los días."],
         etiquetas=["salir de deudas", "plan de pagos", "avalancha", "bola de nieve", "tarjetas de crédito",
                    "finanzas personales", "hoja de cálculo", "Google Sheets", "en español"],
         archivos="un .zip con la guía en PDF y la hoja de cálculo .xlsx"),
    dict(nombre="Empieza a Invertir con $100 al Mes", enlace="invertir-con-100", precio=19,
         titulo="Empieza a Invertir con $100 al Mes: la guía en español para tu primera cuenta de inversión",
         resumen="Qué cuenta abrir primero, qué comprar, cuánto cuesta y cómo ponerlo en automático. En español claro, sin recomendar acciones y sin promesas. Guía de 12 páginas + 5 calculadoras.",
         gancho="Invertir no empieza con saber qué acción comprar. Empieza con saber a dónde va tu primer dólar, y el siguiente. Esta guía te da el orden, en español y sin palabras raras.",
         incluye=["**La guía (PDF, 12 páginas):** el orden de tus primeros dólares, Roth o Traditional en una pregunta, fondos de fecha objetivo e índice explicados, y tu plan de una página",
                  "**Cinco calculadoras (.xlsx):** el match de tu 401(k), cuánto cuesta una comisión de 1% en 30 años y más, en Google Sheets, Excel o Numbers"],
         puntos=["El orden exacto: a dónde va tu primer dólar y el siguiente.",
                 "Roth o Traditional en una sola pregunta.",
                 "Qué comprar: fondos de fecha objetivo e índice, explicados sin palabras raras.",
                 "Cuánto te cuesta una comisión de 1% en 30 años.",
                 "No recomendamos acciones ni prometemos rendimientos: invertir tiene riesgo y el valor puede bajar."],
         boton="Quiero empezar",
         gracias=["Descarga el zip y lee los capítulos 1 y 2 (unos 20 minutos).",
                  "Abre las calculadoras y prueba la pestaña Match 401k con tu sueldo.",
                  "Llena tu plan de una página (página 11) y aparta 30 minutos para abrir tu cuenta."],
         etiquetas=["invertir", "Roth IRA", "401k", "fondos índice", "retiro", "finanzas personales",
                    "calculadora", "Google Sheets", "en español"],
         archivos="un .zip con la guía en PDF y las calculadoras .xlsx"),
    dict(nombre="El Paquete Dinero Simple", enlace="paquete-dinero-simple", precio=29,
         titulo="El Paquete Dinero Simple: 4 kits en español para tu presupuesto, tus deudas y tu primera inversión",
         resumen="Los cuatro kits de Dinero Simple en una sola descarga: Recortar Gastos, El Presupuesto de 20 Minutos, Tu Fecha Sin Deudas y Empieza a Invertir con $100 al Mes. $29 (por separado, $53).",
         gancho="Los cuatro pasos en orden: recorta lo que no usas, dale un plan a lo que queda, ponle fecha a tus deudas y después invierte ese pago.",
         incluye=["**4 guías en PDF y 4 hojas de cálculo (.xlsx)**, las mismas que se venden por separado",
                  "**Empieza aquí (PDF, 3 páginas):** el mapa del paquete, para saber por dónde empezar"],
         puntos=["$29 por los cuatro; por separado son $53 ($5 + $12 + $17 + $19).",
                 "Un orden claro: recortar, presupuesto, deudas, inversión.",
                 "¿Ya compraste uno? Contesta tu recibo y te mandamos un código por la diferencia."],
         boton="Quiero los cuatro",
         gracias=["Abre primero Empieza-Aqui-Mapa-del-Paquete.pdf: en tres páginas te dice por dónde empezar.",
                  "Empieza por El Kit para Recortar Gastos esta semana; el resto va en orden."],
         etiquetas=["finanzas personales", "presupuesto", "salir de deudas", "invertir", "plantillas",
                    "hojas de cálculo", "Google Sheets", "en español", "paquete"],
         archivos="un .zip con las 4 guías, las 4 hojas de cálculo y el mapa del paquete"),
    dict(nombre="El Presupuesto Familiar", enlace="presupuesto-familiar", precio=9,
         titulo="El Presupuesto Familiar: un plan de dinero para toda la casa, para imprimir",
         resumen="12 páginas para imprimir y llenar en familia: lo que entra, lo que sale, lo que siempre llega y un número semanal para gastar sin culpa.",
         gancho="Un plan de dinero para toda la casa, en español: lo que entra, lo que sale, lo que siempre llega aunque no sea cada mes, y un número semanal para gastar sin culpa.",
         incluye=["**12 páginas para imprimir (PDF, carta y A4):** lo que entra en casa, gastos fijos, fondos para lo que siempre llega y tu número de la semana",
                  "Presupuesto del mes, las cuatro semanas, calendario de pagos, plan para las deudas y metas de la familia",
                  "Una junta familiar de dinero de 20 minutos y la revisión del mes"],
         puntos=["Hecho para llenarse en familia, en papel o en una app de PDF.",
                 "Incluye lo que ayudas a la familia de allá como un gasto planeado.",
                 "Una junta familiar de dinero de 20 minutos, una vez al mes."],
         boton="Quiero el presupuesto familiar",
         gracias=["Descarga el PDF en carta (o A4) e imprime las páginas 1 a 4.",
                  "Llénalas en familia; toma como una hora la primera vez.",
                  "Imprime las páginas del mes cada mes y haz la junta de 20 minutos."],
         etiquetas=["presupuesto familiar", "presupuesto", "imprimible", "finanzas personales", "ahorro",
                    "control de gastos", "metas de ahorro", "en español"],
         archivos="PDF en carta y A4"),
    dict(nombre="El Registro de Envíos", enlace="registro-de-envios", precio=7,
         titulo="El Registro de Envíos: compara antes de enviar y sabe cuánto llega",
         resumen="Lo que importa al enviar dinero es cuánto llega allá. Compara servicios, guarda cada envío y ve cuánto pagaste en el año. Para imprimir + hoja de cálculo.",
         gancho="Lo que importa al enviar dinero no es la comisión: es cuánto llega allá. Compara antes de enviar, guarda cada envío y sabe cuánto pagaste en el año.",
         incluye=["**7 páginas para imprimir (PDF, carta y A4):** comparar antes de enviar, a quién le envío, registro de envíos, resumen del año y señales de estafa",
                  "Tus derechos al enviar dinero desde EE. UU., explicados en sencillo",
                  "**Hoja de cálculo (.xlsx):** calcula lo que llega, el costo escondido en el tipo de cambio y tus totales por mes y por servicio"],
         puntos=["Ve el costo escondido en el tipo de cambio, no solo la comisión.",
                 "Estima el impuesto federal del 1% cuando pagas en efectivo, giro o cheque de caja.",
                 "Totales por mes y por servicio, solos.",
                 "No recomendamos ningún servicio: tú comparas con tus propias cotizaciones."],
         boton="Quiero el registro",
         gracias=["Sube la hoja de cálculo a Google Drive (o ábrela en Excel) y lee la pestaña Empieza.",
                  "Antes de tu próximo envío, llena Comparar con dos o tres cotizaciones para el mismo monto.",
                  "Después de enviar, anota el envío en Envíos y borra las filas de ejemplo."],
         etiquetas=["remesas", "envíos de dinero", "remittance tracker", "hoja de cálculo", "Google Sheets",
                    "finanzas personales", "familia", "en español"],
         archivos="PDF en carta y A4, y un archivo .xlsx"),
    dict(nombre="La Lista para Construir tu Crédito", enlace="construir-credito", precio=6,
         titulo="La Lista para Construir tu Crédito: tus primeros 12 meses, también con ITIN",
         resumen="Construir crédito es aburrido y funciona. Qué hacer en tus primeros 12 meses, mes a mes, también si tienes ITIN. 8 páginas para imprimir.",
         gancho="Construir crédito es aburrido y funciona: pasos pequeños, mes a mes. Esta lista te dice qué hacer en tus primeros 12 meses, también si tienes ITIN.",
         incluye=["**8 páginas para imprimir (PDF, carta y A4):** lo que cuenta en tu puntaje, tu punto de partida, los primeros 12 meses paso a paso y las cinco reglas",
                  "Registro mensual de uso de tus tarjetas y revisión de tu reporte, con registro de disputas",
                  "Cuidado con las promesas (CPN y \"reparación de crédito\") y las opciones para empezar, también con ITIN"],
         puntos=["Un paso por mes durante 12 meses.",
                 "Opciones para empezar con ITIN.",
                 "Cómo reconocer las promesas falsas de \"reparación de crédito\" y los CPN.",
                 "Nadie puede prometerte un puntaje; esta lista te dice qué hábitos cuentan."],
         boton="Quiero la lista",
         gracias=["Imprime las páginas 1 a 3 y escribe tu punto de partida.",
                  "Pide tu reporte gratis en AnnualCreditReport.com y revísalo con la página de revisión.",
                  "Marca el paso del mes cada mes y anota el uso de tus tarjetas."],
         etiquetas=["crédito", "construir crédito", "puntaje de crédito", "ITIN", "tarjeta asegurada",
                    "finanzas personales", "imprimible", "en español"],
         archivos="PDF en carta y A4"),
    dict(nombre="El Paquete de la Familia", enlace="paquete-de-la-familia", precio=16,
         titulo="El Paquete de la Familia: presupuesto, envíos y crédito en una descarga",
         resumen="Los tres para imprimir en una descarga: El Presupuesto Familiar, El Registro de Envíos con su hoja de cálculo y La Lista para Construir tu Crédito. $16 (por separado, $22).",
         gancho="Los tres en una descarga: El Presupuesto Familiar, El Registro de Envíos con su hoja de cálculo y La Lista para Construir tu Crédito, por menos que comprarlos aparte ($22).",
         incluye=["**El Presupuesto Familiar** (12 páginas)", "**El Registro de Envíos** (7 páginas + hoja de cálculo .xlsx)",
                  "**La Lista para Construir tu Crédito** (8 páginas)"],
         puntos=["$16 por los tres; por separado son $22 ($9 + $7 + $6).",
                 "Todo en carta y A4, para imprimir o llenar en una app de PDF.",
                 "No es lo mismo que El Paquete Dinero Simple: este reúne los tres imprimibles para la familia."],
         boton="Quiero el paquete",
         gracias=["Descomprime el archivo y empieza por El Presupuesto Familiar.",
                  "Usa El Registro de Envíos en cada envío.",
                  "Marca un paso de La Lista para Construir tu Crédito cada mes."],
         etiquetas=["presupuesto familiar", "remesas", "crédito", "imprimible", "finanzas personales",
                    "hoja de cálculo", "paquete", "en español"],
         archivos="un .zip con los PDF en carta y A4 y la hoja de cálculo"),
    # PR #8 (apps thread, launch/dashboard-pro/): copy taken from its LISTING.md, same native review.
    dict(nombre="Tablero de dinero Pro", enlace="tablero-de-dinero-pro", precio=12,
         titulo="Tablero de dinero Pro: presupuesto en Google Sheets con lo que descargas de tu banco",
         resumen="Pega tus movimientos del banco y ve 12 meses de lo que entra, lo que gastas y lo que te sobra, cada categoría contra su presupuesto y tus fondos de ahorro, con gráficas.",
         gancho="Tu banco ya tiene todos tus números. Esto los pone en una sola página: toma lo que descargas de tu banco (o el archivo del Tablero de dinero gratis) y lo convierte en un tablero que sí vas a revisar cada mes.",
         incluye=["**Tablero:** elige un mes y ve lo que entra, lo que gastas, lo que ahorras y lo que te sobra, con tres gráficas",
                  "**Presupuesto vs real, Tendencias de 12 meses y Fondos de ahorro**, más la pestaña Movimientos para pegar y listo"],
         puntos=["Funciona con lo que descargas de tu banco: pegas y listo.",
                 "Las transferencias y pagos de tarjeta no cuentan como gasto, para no contar nada dos veces.",
                 "Hecha para Google Sheets (gratis); el .xlsx también funciona en Excel y Numbers."],
         boton="Quiero mi tablero",
         gracias=["Abre el PDF Empieza aquí.", "Haz clic en el enlace y elige Hacer una copia: la hoja queda en tu Google Drive.",
                  "Pega tus movimientos y pon tu presupuesto en las celdas amarillas."],
         etiquetas=["presupuesto", "hoja de cálculo", "Google Sheets", "finanzas personales", "fondos de ahorro",
                    "control de gastos", "presupuesto mensual", "en español"],
         archivos="un .zip con el PDF Empieza aquí y la hoja .xlsx"),
]


def _cross(nombre: str, cross: dict) -> str:
    rec, why, _where, code = cross[nombre]
    code = code.replace(" (new)", "")
    off = f" Por tu compra tienes $5 de descuento con el código **{code}**." if code else ""
    return f"¿Y después? **{rec}**: {why[0].lower() + why[1:]}{off} [ENLACE: {rec}]"


def descripcion(p: dict) -> str:
    inc = "\n".join(f"- {x}" for x in p["incluye"])
    return (f"{p['gancho']}\n\n**Qué incluye**\n\n{inc}\n\nDescarga inmediata: {p['archivos']}. ${p['precio']}, un solo "
            f"pago, los archivos son tuyos.\n\n*{AVISO}*")


def gracias(p: dict, cross: dict) -> str:
    steps = "\n".join(f"> {i}. {s}" for i, s in enumerate(p["gracias"], 1))
    return f"> ¡Gracias por comprar {p['nombre']}!\n{steps}\n>\n> {_cross(p['nombre'], cross)}\n> {FIRMA}"


def markdown(secciones: list[tuple[str, list[str]]], cross: dict) -> str:
    """secciones: the brand's (section, [products]) list from build_storefront.BRANDS, so the order stays in one place."""
    by = {p["nombre"]: p for p in PRODUCTOS}
    desc = dict(SECCIONES)
    out = ["# Dinero Simple: tienda de Gumroad en español", "", REVIEW, "",
           "Todo lo que se escribe en Gumroad, en español y listo para pegar. Las imágenes del perfil (avatar.png, "
           "cover.png) y la guía en inglés están en STOREFRONT.md, en esta misma carpeta. No se ha subido nada.", "",
           "## Perfil (Settings > Profile)", "",
           f"- **Nombre:** {PERFIL['nombre']}", f"- **Usuario:** {PERFIL['usuario']} (gumroad.com/{PERFIL['usuario']})",
           f"- **Bio:** {PERFIL['bio']}", f"- **Texto del botón para seguir:** {PERFIL['boton_seguir']}",
           f"- **Nota al pie:** {PERFIL['pie']}", "", "**Acerca de:**", "", f"> {PERFIL['acerca']}", "",
           "## Secciones del perfil, en orden", ""]
    for name, prods in secciones:
        out.append(f"**{name}.** {desc[name]}")
        out += [f"{i}. {n} (${by[n]['precio']})" for i, n in enumerate(prods, 1)] + [""]
    out += ["## Ventas cruzadas en el checkout (Checkout > Upsells)", "",
            "| Si compran | Ofrece | Texto de la oferta | Código |", "|---|---|---|---|"]
    for p in PRODUCTOS:
        rec, why, _w, code = cross[p["nombre"]]
        out.append(f"| {p['nombre']} | {rec} | {why} | {code.replace(' (new)', ' (nuevo)') or '—'} |")
    out += ["", "Los códigos marcados (nuevo) todavía no existen: créalos en Gumroad > Checkout > Discounts antes de usarlos.", ""]
    for p in PRODUCTOS:
        out += [f"## {p['nombre']} (${p['precio']})", "",
                f"- **Nombre en Gumroad:** {p['titulo']}", f"- **Enlace corto:** gumroad.com/l/{p['enlace']}",
                f"- **Precio:** ${p['precio']} (sin \"paga lo que quieras\" hasta tener datos)",
                f"- **Texto del botón:** {p['boton']}", f"- **Resumen (tarjeta del perfil):** {p['resumen']}",
                f"- **Etiquetas:** {', '.join(p['etiquetas'])}", "", "**Descripción:**", "", descripcion(p), "",
                "**Puntos clave (Additional details):**", ""] + [f"- {x}" for x in p["puntos"]] + [
                "", "**Mensaje de agradecimiento (Content > mensaje después de la compra):**", "", gracias(p, cross), ""]
    return "\n".join(out)
