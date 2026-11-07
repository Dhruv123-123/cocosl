# "Mandar dinero a casa": the real cost of sending money home (the fee plus the exchange-rate markup), for
# Spanish-first adults and recent arrivals (scouting's creator landscape, research/scouting/dinero-simple-creator-landscape.md
# on PR #2: nobody in Spanish posts this steadily). 6 posts on Tuesdays, Mar 2 - Apr 6, 2027.
#
# Rules: public pricing only, typed in by the viewer or by us on posting day; no provider is named or ranked on screen
# ("Opción A / B / C"); every number is an example; the calculator (/calculadora-de-envios/) does the maths.
# Segment tuples: (heading, on_screen_text, narration, scene). All copy needs a native-speaker review.
from month1_shorts_a import CTA

PILLAR = "apps y herramientas de dinero, comparadas sin rodeos"
CALC = "La calculadora de envíos gratis, en español, está en el enlace de la bio: escribes lo que te muestra cada servicio y te dice cuánto llega."
TAGS = ["remesas", "enviardinero", "tipodecambio", "dinerosimple", "finanzasenespañol"]
NO_ADVICE = "Ejemplo con números redondos. Información general, no es asesoría financiera."
SRC = ["https://www.consumerfinance.gov/es/", "https://remittanceprices.worldbank.org/"]

ITEMS = [
dict(
    key="e-dos-costos", format="short", pillar=PILLAR,
    angle="Series opener: every transfer has two costs, the fee you see and the exchange-rate markup you don't. Worked example: $300, a $3.99 fee and a rate 2% under the market rate cost about $10 in total, not $3.99.",
    title="Tu envío tiene dos costos, y uno está escondido",
    hook="Cuando mandas dinero a casa pagas dos veces, y solo una sale en letras grandes.",
    thumbnail_text="El costo escondido",
    segments=[
        ("Gancho", "Pagas dos veces cada envío", "Cuando mandas dinero a casa pagas dos veces, y solo una sale en letras grandes.", "a phone showing a transfer screen with a small fee line"),
        ("Costo 1", "1. La comisión: la que sí ves", "El primer costo es la comisión. Esa la ves: por ejemplo, tres noventa y nueve.", "a receipt with the fee circled"),
        ("Costo 2", "2. El tipo de cambio: el que no ves", "El segundo está en el tipo de cambio. Si el mercado está a veinte y a ti te dan diecinueve sesenta, esa diferencia también la pagas tú.", "two exchange rates side by side, one lower"),
        ("La cuenta", "$300: $3.99 + unos $6 en el cambio", "Con trescientos dólares, ese dos por ciento menos son unos seis dólares. En total pagas casi diez, no tres noventa y nueve.", "a simple sum on a notepad"),
        ("Qué hacer", "Compara cuánto llega, no la comisión", "Por eso no compares la comisión. Compara cuánto llega allá, con la misma cantidad y el mismo día.", "two receipts with the received amount highlighted"),
        ("Cierre", "Cada martes: una parte de la serie", "Cada martes te enseño una parte. Guarda este video para tu próximo envío.", "a calendar with Tuesdays marked"),
    ],
    caption="Cada envío tiene dos costos:\n1. La comisión (la ves).\n2. El margen en el tipo de cambio (no lo ves).\nEjemplo: $300 con $3.99 de comisión y un tipo de cambio 2% por debajo del mercado = unos $10 en total.\nCompara cuánto llega allá, no solo la comisión.\n\n" + CALC + "\n" + NO_ADVICE + "\n\n" + CTA,
    hashtags=TAGS,
    description="Serie Mandar dinero a casa, parte 1: la comisión y el tipo de cambio.",
    sources=SRC,
    claims=["Example arithmetic: 2% of $300 = $6; $3.99 + $6 = $9.99",
            "Providers must show the fee, exchange rate and amount received before you pay (CFPB Remittance Transfer Rule)"],
),
dict(
    key="ec-cuanto-llega", format="carousel", pillar=PILLAR,
    angle="Save-this carousel: how to work out what really arrives in 4 steps (market rate, the rate you're offered, the fee, the amount received) with one worked example, then the calculator does it for you.",
    title="Cuánto llega de verdad: la cuenta en 4 pasos",
    hook="Guárdala para tu próximo envío.",
    thumbnail_text="¿Cuánto llega?",
    segments=[
        ("Portada", "¿Cuánto llega de verdad? 4 pasos", "Guárdala para tu próximo envío.", "a phone and a calculator on a table"),
        ("Paso 1", "Busca el tipo de cambio del mercado de hoy", "Paso uno: busca el tipo de cambio del mercado de hoy. Es el punto de comparación.", "a search result showing a market rate"),
        ("Paso 2", "Anota el tipo de cambio que te ofrecen", "Paso dos: anota el que te ofrece el servicio, antes de pagar.", "a transfer screen with the offered rate circled"),
        ("Paso 3", "Suma la comisión", "Paso tres: suma la comisión, y cualquier cargo por pagar con tarjeta.", "a receipt with fee lines"),
        ("Paso 4", "Mira la línea 'monto a recibir'", "Paso cuatro: mira la línea que dice cuánto recibe tu familia. Esa es la que importa.", "the amount-received line highlighted"),
        ("Ejemplo", "$300 · mercado 20.00 · te dan 19.60 · $3.99", "Ejemplo: trescientos dólares, mercado a veinte, te dan diecinueve sesenta y pagas tres noventa y nueve. Llegan 5,880 en vez de 6,000.", "a worked example card"),
        ("Más fácil", "La calculadora lo hace por ti", "La calculadora gratis lo hace por ti y compara hasta cinco opciones.", "the calculator on a phone screen"),
    ],
    caption="Cuánto llega de verdad, en 4 pasos:\n1. Tipo de cambio del mercado hoy.\n2. Tipo de cambio que te ofrecen.\n3. Comisión (y cargos por tarjeta).\n4. La línea 'monto a recibir'.\nEjemplo: $300, mercado 20.00, te dan 19.60, comisión $3.99: llegan 5,880 en vez de 6,000.\n\n" + CALC + "\n" + NO_ADVICE + "\n\n" + CTA,
    hashtags=TAGS,
    description="Cómo saber cuánto llega de verdad cuando mandas dinero.",
    sources=SRC,
    claims=["Example arithmetic: 300 x 20.00 = 6,000; 300 x 19.60 = 5,880 (the fee is paid on top of the $300)",
            "The pre-payment disclosure must show the amount to be received (CFPB Remittance Transfer Rule)"],
),
dict(
    key="e-impuesto-1", format="short", pillar=PILLAR,
    angle="The 1% federal tax on remittances paid in cash, money order or cashier's check (from Jan 1, 2026); transfers paid from a US bank account or with a US-issued debit or credit card are not taxed. Example: $300 in cash adds $3.",
    title="El impuesto de 1% a los envíos en efectivo",
    hook="Desde enero de 2026, mandar dinero pagando en efectivo cuesta uno por ciento más.",
    thumbnail_text="1% si pagas en efectivo",
    segments=[
        ("Gancho", "Envíos en efectivo: 1% más desde 2026", "Desde enero de 2026, mandar dinero pagando en efectivo cuesta uno por ciento más.", "cash on a counter next to a transfer receipt"),
        ("Qué es", "Un impuesto federal nuevo", "Es un impuesto federal nuevo sobre los envíos al extranjero.", "a simple 'nuevo' label on a receipt"),
        ("Cuándo aplica", "Efectivo, giro postal o cheque de caja", "Aplica si pagas el envío en efectivo, con giro postal o con cheque de caja.", "cash, a money order and a cashier's check"),
        ("Cuándo no", "No: desde tu cuenta o con tarjeta de EE. UU.", "No aplica si lo pagas desde tu cuenta de banco en Estados Unidos o con una tarjeta de débito o crédito de aquí.", "a bank app and a debit card"),
        ("La cuenta", "$300 en efectivo = $3 más", "Con trescientos en efectivo son tres dólares más, cada vez.", "a small sum on a notepad"),
        ("Ojo", "Pagar con tarjeta de crédito puede costar más", "Ojo: con tarjeta de crédito algunos servicios cobran un cargo extra. Revisa el total antes de pagar.", "a warning sign over a credit card"),
    ],
    caption="Impuesto federal de 1% a los envíos de dinero al extranjero (desde el 1 de enero de 2026):\n• Aplica si pagas en efectivo, giro postal o cheque de caja.\n• No aplica si pagas desde una cuenta de banco de EE. UU. o con tarjeta de débito o crédito de EE. UU.\nEjemplo: $300 en efectivo = $3 más.\nCon tarjeta de crédito, revisa si hay un cargo extra.\n\n" + CALC + "\nInformación general, no es asesoría fiscal.\n\n" + CTA,
    hashtags=TAGS,
    description="El impuesto de 1% a los envíos pagados en efectivo, explicado.",
    sources=["https://www.irs.gov/es", "https://www.consumerfinance.gov/es/"],
    claims=["1% excise tax on remittance transfers paid in cash, money order, cashier's check or similar physical instrument, for transfers made after Dec 31, 2025 (One Big Beautiful Bill Act, IRC sec. 4475)",
            "Exempt when funded from an account at a US financial institution or with a US-issued debit or credit card",
            "Check for any IRS guidance issued since November 2026"],
),
dict(
    key="e-mismo-dia", format="short", pillar=PILLAR,
    angle="How to compare fairly: same amount, same day, same delivery method (bank deposit vs cash pickup), and look at the amount received; rates move daily and some services price pickup differently. No provider is named.",
    title="Para comparar envíos: mismo día, misma cantidad",
    hook="Si comparas envíos en días distintos, la comparación no sirve.",
    thumbnail_text="Compara bien",
    segments=[
        ("Gancho", "Comparar en días distintos no sirve", "Si comparas envíos en días distintos, la comparación no sirve.", "two calendars with different dates crossed out"),
        ("Regla 1", "Mismo día, misma hora", "El tipo de cambio se mueve todos los días. Compara el mismo día.", "a rate ticker moving"),
        ("Regla 2", "Misma cantidad", "Usa la misma cantidad. A veces la comisión cambia según cuánto mandas.", "the same $300 typed in three apps"),
        ("Regla 3", "Mismo método: depósito o recoger en efectivo", "Y el mismo método: depósito a cuenta o recoger en efectivo pueden tener precios distintos.", "a bank icon and a cash pickup icon"),
        ("Qué ver", "Solo una línea: cuánto recibe tu familia", "Luego mira una sola línea: cuánto recibe tu familia. Gana la que deja más allá.", "three receipts, amount received highlighted"),
        ("Cierre", "Anótalo en la calculadora", "Anótalo en la calculadora gratis y guárdalo para el mes que viene.", "the calculator on a phone"),
    ],
    caption="Para comparar envíos de verdad:\n1. El mismo día.\n2. La misma cantidad.\n3. El mismo método (depósito o efectivo).\n4. Mira solo cuánto recibe tu familia.\n\n" + CALC + "\n" + NO_ADVICE + "\n\n" + CTA,
    hashtags=TAGS,
    description="Cómo comparar servicios de envío de dinero de forma justa.",
    sources=SRC,
    claims=["Exchange rates offered change daily; fees can vary by amount, funding method and delivery method"],
),
dict(
    key="e-tus-derechos", format="short", pillar=PILLAR,
    angle="Your rights under the CFPB Remittance Transfer Rule: a disclosure before you pay, a receipt, generally 30 minutes to cancel for a full refund, and 180 days to report an error; complaints go to the CFPB (in Spanish).",
    title="Mandaste dinero y algo salió mal: tus derechos",
    hook="Si mandas dinero desde Estados Unidos, la ley te da derechos. Casi nadie los conoce.",
    thumbnail_text="Tus derechos al enviar",
    segments=[
        ("Gancho", "Tus derechos al mandar dinero", "Si mandas dinero desde Estados Unidos, la ley te da derechos. Casi nadie los conoce.", "a receipt with a shield icon"),
        ("Antes de pagar", "Te deben mostrar cuánto llega", "Antes de pagar, te deben mostrar la comisión, el tipo de cambio y cuánto llega.", "a disclosure screen"),
        ("30 minutos", "En general: 30 minutos para cancelar", "En general tienes treinta minutos para cancelar y recibir todo tu dinero, si todavía no lo recogieron.", "a 30-minute timer"),
        ("Errores", "180 días para reportar un error", "Si llegó menos o no llegó, tienes ciento ochenta días para reportar el error al servicio.", "a calendar counting days"),
        ("Si no responden", "Queja gratis al CFPB, en español", "Si no te lo resuelven, pon una queja gratis ante el CFPB. Atienden en español.", "a phone showing a complaint form"),
        ("Cierre", "Guarda tu recibo siempre", "Y guarda siempre tu recibo. Es tu prueba.", "a receipt going into a wallet"),
    ],
    caption="Tus derechos cuando mandas dinero desde EE. UU.:\n• Antes de pagar: la comisión, el tipo de cambio y cuánto llega.\n• En general, 30 minutos para cancelar con reembolso completo (si no lo han recogido).\n• 180 días para reportar un error.\n• Si no te lo resuelven: queja gratis en consumerfinance.gov/es o al 855-411-2372.\nGuarda tu recibo.\n\nInformación general, no es asesoría legal.\n\n" + CTA,
    hashtags=TAGS,
    description="Tus derechos cuando mandas dinero: cancelar, errores y quejas.",
    sources=["https://www.consumerfinance.gov/es/"],
    claims=["CFPB Remittance Transfer Rule (Reg. E subpart B): pre-payment disclosure, receipt, 30-minute cancellation right (generally), 180 days to report an error",
            "CFPB phone 855-411-2372 offers Spanish; complaints at consumerfinance.gov/es"],
),
dict(
    key="ec-cuanto-llega-mes", format="carousel", pillar=PILLAR,
    angle="The monthly 'cuánto llega' template: the same $300 sent the same day through three anonymised options (Opción A, B, C), typed from public prices on posting day; shows fee, rate and amount received, never ranks or names providers.",
    title="¿Cuánto llega este mes? Mismo envío, 3 opciones",
    hook="Mandamos el mismo envío por tres opciones. Mira cuánto llega.",
    thumbnail_text="¿Cuánto llega este mes?",
    segments=[
        ("Portada", "Este mes: $300, el mismo día, 3 opciones", "Mismo envío, mismo día, tres opciones. Mira cuánto llega.", "three phones side by side"),
        ("Opción A", "Opción A: comisión · cambio · llega [LLENAR]", "Opción A: comisión, tipo de cambio y cuánto llega.", "receipt card A"),
        ("Opción B", "Opción B: comisión · cambio · llega [LLENAR]", "Opción B, igual.", "receipt card B"),
        ("Opción C", "Opción C: comisión · cambio · llega [LLENAR]", "Opción C, igual.", "receipt card C"),
        ("La diferencia", "Diferencia entre la que más y menos deja [LLENAR]", "La diferencia entre la que más deja y la que menos.", "a bar showing the gap"),
        ("Tu turno", "Tus precios cambian: hazlo tú hoy", "Los precios cambian cada día y según tu país. Haz tu propia cuenta antes de mandar.", "the calculator on a phone"),
    ],
    caption="¿Cuánto llega este mes? El mismo envío de $300, el mismo día, por tres opciones (precios públicos tomados el [FECHA] a las [HORA], hacia [PAÍS], depósito a cuenta):\nOpción A: [LLENAR]\nOpción B: [LLENAR]\nOpción C: [LLENAR]\nLos precios cambian cada día. Haz tu propia cuenta antes de mandar.\n\n" + CALC + "\n" + NO_ADVICE + "\n\n" + CTA,
    hashtags=TAGS,
    description="Plantilla mensual: el mismo envío por tres opciones, cuánto llega.",
    sources=SRC,
    claims=["OPERATOR: fill every [LLENAR], [FECHA], [HORA] and [PAÍS] from each provider's public quote page on posting day; screenshot each quote and keep it",
            "Options stay anonymised (A/B/C) on screen and in the caption: no provider is named or ranked",
            "Re-post monthly with the same amount, corridor and delivery method"],
),
]
