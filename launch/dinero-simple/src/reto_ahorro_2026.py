# Dinero Simple "Reto de diciembre: $10 al día" (Nov 30 - Dec 28, 2026): a savings challenge the viewer does *with*
# us, after PR #2's scouting (research/scouting/finance-formats-nov-2026.md): the savings-challenge hook had about 6x
# the reach of other hook types on finance TikTok. 7 posts: day 1, a tracker, a check-in each Sunday and a finale.
#
# Rules from that research, applied here:
#  1. The numbers are a worked example, never a promise ("si apartas $10 al día, son $280"), never "vas a ahorrar".
#  2. No fake personal progress: we're faceless, so no invented "yo ahorré $X". Only the plan's arithmetic.
#  3. Each check-in stands alone (a new viewer can start that day) and points back to day 1.
#  4. Counted inside the cadence cap: at most 2 posts a day per platform with month 1 and the holiday pack.
# Smaller versions ($5 and $2 a day) are offered in every post, so nobody is left out.
# Segment tuples: (heading, on_screen_text, narration, scene). All copy needs a native-speaker review.
from month1_shorts_a import CTA
from month2_shorts import IMPUESTOS as PRESUPUESTO_P

RETO = "#RetoDeDiciembre: $10 al día del 30 de noviembre al 27 de diciembre. ¿No te alcanza? Hazlo con $5 o con $2: lo que cuenta es el hábito."
DIA1 = "¿Llegas tarde? Empieza hoy: el reto sirve desde cualquier día. El primer video está fijado en el perfil."
TAGS = ["retodeahorro", "retodediciembre", "ahorro", "presupuesto", "dinerosimple"]

ITEMS = [
dict(
    key="r-dia-1", format="short", pillar=PRESUPUESTO_P,
    angle="Day 1 of a 28-day challenge done with the viewer: set aside $10 a day from Nov 30 to Dec 27 into a separate, named savings spot; that is $280 by Dec 27 (example arithmetic), with $5 and $2 versions.",
    title="Reto de diciembre: $10 al día, ¿te animas?",
    hook="Te reto: diez dólares al día, de hoy al 27 de diciembre. Hagámoslo juntos.",
    thumbnail_text="Reto: $10 al día",
    segments=[
        ("Gancho", "Reto: $10 al día hasta el 27 de diciembre", "Te reto: diez dólares al día, de hoy al 27 de diciembre. Hagámoslo juntos.", "M holding up a calendar with Nov 30 circled"),
        ("La cuenta", "28 días × $10 = $280", "Son 28 días. Si apartas diez dólares cada día, el 27 de diciembre tienes 280. Es un ejemplo de la cuenta, no una promesa.", "a jar with 28 small marks"),
        ("Dónde", "Apártalo en una cuenta con nombre: 'Reto'", "Hoy abre un apartado o una cuenta de ahorro y ponle de nombre 'Reto'. Lo que tiene nombre se toca menos.", "a phone with a savings pocket named 'Reto'"),
        ("Cómo", "Transfiere cada noche, o $70 cada domingo", "Transfiere cada noche, o setenta cada domingo si te pagan por semana.", "a weekly calendar with Sundays marked"),
        ("Sin excusas", "¿No te alcanza? $5 o $2 al día", "¿Diez es mucho? Hazlo con cinco o con dos. Lo que cuenta es el hábito.", "three jars: $10, $5, $2"),
        ("Cierre", "Cada domingo te digo cómo vamos", "Cada domingo subo cómo vamos y de dónde sacar los diez. Guarda este video.", "M giving a thumbs up"),
    ],
    caption="Reto de diciembre: $10 al día del 30 de noviembre al 27 de diciembre.\n• 28 días × $10 = $280 (ejemplo de la cuenta, no una promesa).\n• Apártalo en una cuenta o un apartado con nombre: 'Reto'.\n• Transfiere cada noche, o $70 cada domingo.\n• ¿No te alcanza? Con $5 son $140; con $2, $56.\nCada domingo subo cómo vamos y de dónde sacar los $10.\n\n" + CTA,
    hashtags=TAGS,
    description="Día 1 del Reto de diciembre: $10 al día, hasta el 27 de diciembre.",
    sources=["https://www.consumerfinance.gov/es/"],
    claims=["Example arithmetic: 28 x $10 = $280; 28 x $5 = $140; 28 x $2 = $56; 7 x $10 = $70",
            "Nov 30 to Dec 27, 2026 inclusive is 28 days"],
),
dict(
    key="rc-tabla-del-reto", format="carousel", pillar=PRESUPUESTO_P,
    angle="A tracker to save and send: 28 squares of $10 by week with running totals ($70, $140, $210, $280), the $5 and $2 versions, and three rules (separate named account, transfer the same day, never use a card).",
    title="Tu tabla del reto: 28 casillas",
    hook="Guárdala y tacha una casilla cada día.",
    thumbnail_text="Tabla del reto",
    segments=[
        ("Portada", "Reto de diciembre: tu tabla de 28 casillas", "Guárdala y tacha una casilla cada día.", "M holding a printed grid with 28 squares"),
        ("Semana 1", "Nov 30 – dic 6: 7 casillas = $70", "Al terminar la semana 1 llevas 70.", "a row of 7 squares, all ticked"),
        ("Semana 2", "Dic 7 – 13: 7 casillas = $140", "Al terminar la semana 2 llevas 140.", "two rows of squares"),
        ("Semana 3", "Dic 14 – 20: 7 casillas = $210", "Al terminar la semana 3 llevas 210.", "three rows of squares"),
        ("Semana 4", "Dic 21 – 27: 7 casillas = $280", "Al terminar la semana 4 llevas 280.", "four rows of squares with a star"),
        ("Otras versiones", "$5 al día = $140 · $2 al día = $56", "¿Diez es mucho? Con cinco son 140; con dos, 56.", "three jars side by side"),
        ("3 reglas", "Cuenta aparte · el mismo día · nunca con tarjeta", "Tres reglas: una cuenta aparte con nombre, transfiere el mismo día y nunca lo 'ahorres' pagando con tarjeta.", "a short checklist"),
        ("Cierre", "Mándasela a quien lo hace contigo", "Mándasela a quien lo hace contigo: en pareja o en familia se cumple más.", "two phones sharing a picture"),
    ],
    caption="Tu tabla del Reto de diciembre (ejemplo con $10 al día):\nSemana 1 (nov 30 – dic 6): $70\nSemana 2 (dic 7 – 13): $140\nSemana 3 (dic 14 – 20): $210\nSemana 4 (dic 21 – 27): $280\nCon $5 al día: $140. Con $2: $56.\nReglas: cuenta aparte con nombre, transfiere el mismo día, nunca con tarjeta de crédito.\nGuárdala y mándasela a quien lo hace contigo.\n\n" + DIA1 + "\n\n" + CTA,
    hashtags=TAGS,
    description="La tabla de 28 casillas del Reto de diciembre.",
    sources=[],
    claims=["Week totals: 7, 14, 21, 28 x $10 = $70, $140, $210, $280; check the week date ranges against the 2026 calendar"],
),
dict(
    key="r-semana-1", format="short", pillar=PRESUPUESTO_P,
    angle="Week 1 check-in (Dec 6): $70 by now in the example; where to find $10 a day this week, the small daily leaks (coffee, delivery fees, the snack at the gas station), with a new-viewer on-ramp.",
    title="Reto semana 1: de dónde sacar $10 al día",
    hook="Semana uno del reto: si vas al día, ya llevas setenta. Si no, aquí sacas los diez.",
    thumbnail_text="Semana 1: $70",
    segments=[
        ("Gancho", "Semana 1: si vas al día, ya llevas $70", "Semana uno del reto: si vas al día, ya llevas setenta. Si no, aquí sacas los diez.", "a calendar with 7 squares ticked"),
        ("Fuga 1", "El café o el refresco de la gasolinera", "Uno: el café o el refresco de la gasolinera. Llévalo de casa tres días y ya son casi diez.", "a thermos next to a gas-station cup"),
        ("Fuga 2", "El cargo de entrega de la app", "Dos: la comida a domicilio. El cargo de entrega más la propina pueden ser diez por pedido.", "a phone with a delivery app and a fee"),
        ("Fuga 3", "La compra 'ya que estoy aquí'", "Tres: la compra de 'ya que estoy aquí'. Ve con lista y sal con lo de la lista.", "a short shopping list"),
        ("Regla", "Lo que no gastas, transfiérelo hoy", "Lo que no gastas, transfiérelo hoy al apartado del reto. Si no lo mueves, se gasta solo.", "an arrow from wallet to savings"),
        ("Cierre", "¿Llegas tarde? Empieza hoy", "¿Llegas tarde? Empieza hoy. El día uno está fijado en el perfil.", "M pointing at a pinned video"),
    ],
    caption="Reto de diciembre, semana 1: si vas al día, ya llevas $70 (ejemplo con $10 al día).\nDe dónde sacar los $10 esta semana:\n1. El café o el refresco de la gasolinera.\n2. El cargo de entrega y la propina de la app.\n3. La compra de 'ya que estoy aquí'.\nLo que no gastas, transfiérelo hoy al apartado del reto.\n\n" + DIA1 + "\n\n" + RETO + "\n\n" + CTA,
    hashtags=TAGS,
    description="Semana 1 del Reto de diciembre: de dónde sacar $10 al día.",
    sources=[],
    claims=["Example arithmetic: 7 x $10 = $70", "Delivery fee plus tip 'can be' about $10 an order (illustrative, varies)"],
),
dict(
    key="r-semana-2", format="mid", pillar=PRESUPUESTO_P,
    angle="Week 2 check-in (Dec 13): $140 in the example; this week the $10 a day comes from one 10-minute phone call that lowers a bill (phone, internet, car insurance), with a script in Spanish; the monthly savings fund the challenge and keep going after it.",
    title="Reto semana 2: una llamada que paga el reto",
    hook="Semana dos del reto. Esta semana los diez dólares salen de una sola llamada de diez minutos.",
    thumbnail_text="Semana 2: $140",
    segments=[
        ("Gancho", "Semana 2: si vas al día, ya llevas $140", "Semana dos del reto. Si vas al día, ya llevas ciento cuarenta. Esta semana los diez dólares salen de una sola llamada de diez minutos.", "a calendar with 14 squares ticked"),
        ("La idea", "Baja una cuenta y el reto se paga solo", "La idea es esta: si bajas una cuenta fija, ese dinero se aparta solo cada mes, también después del reto.", "a bill with a lower number"),
        ("Cuál", "Celular, internet o seguro del carro", "Escoge una: el celular, el internet o el seguro del carro. Son las que más cambian si preguntas.", "three bills on a table"),
        ("Antes", "Ten a la mano tu factura y una oferta", "Antes de llamar, ten a la mano tu factura y el precio de un plan parecido en otra compañía. Muchas atienden en español: marca la opción de español.", "a bill next to a phone"),
        ("El guion", "'Estoy pensando en cambiarme'", "Di esto: estoy revisando mis gastos y estoy pensando en cambiarme. ¿Qué planes más baratos o descuentos tienen para mí?", "a phone with a speech bubble"),
        ("Si dicen no", "Pide hablar con retención de clientes", "Si te dicen que no, pide amable que te pasen con el área de retención de clientes. Ahí suelen tener las ofertas.", "a phone being transferred"),
        ("Ejemplo", "Ejemplo: $20 menos al mes", "Ejemplo: si te bajan veinte dólares al mes, son doscientos cuarenta al año. Es un ejemplo, no una promesa; a veces no bajan nada.", "a small chart going down"),
        ("Revisa", "Lee qué cambia antes de aceptar", "Antes de aceptar, pregunta si el precio es por tiempo limitado y si cambia algo del servicio o te piden un contrato.", "a magnifying glass over fine print"),
        ("Aparta", "Lo que bajó, transfiérelo al reto", "Lo que bajó, transfiérelo al apartado del reto el mismo día. Si no, se pierde en el mes.", "an arrow into a savings pocket"),
        ("Cierre", "¿Llegas tarde? Empieza hoy", "¿Llegas tarde al reto? Empieza hoy con diez, cinco o dos al día. El día uno está fijado en el perfil.", "M pointing at a pinned video"),
    ],
    caption="Reto de diciembre, semana 2: si vas al día, ya llevas $140 (ejemplo con $10 al día).\nEsta semana los $10 salen de una llamada de 10 minutos al celular, internet o seguro del carro:\n'Estoy revisando mis gastos y estoy pensando en cambiarme. ¿Qué planes más baratos o descuentos tienen para mí?'\nSi dicen que no, pide el área de retención. Antes de aceptar, pregunta si el precio es temporal o trae contrato.\nEjemplo: $20 menos al mes son $240 al año (no es una promesa).\n\n" + DIA1 + "\n\n" + RETO + "\n\n" + CTA,
    hashtags=TAGS,
    description="Semana 2 del Reto de diciembre: una llamada para bajar una cuenta.",
    sources=["https://www.consumerfinance.gov/es/"],
    claims=["Example arithmetic: 14 x $10 = $140; $20 x 12 = $240", "Many carriers offer Spanish-language support (say 'many', don't name one)"],
),
dict(
    key="r-semana-3", format="image", pillar=PRESUPUESTO_P,
    angle="Week 3 check-in (Dec 20) as one image to screenshot: $210 in the example, and the week's rule: the challenge money is not the gift money; buy gifts from the December number, not from the 'Reto' account.",
    title="Reto semana 3: $210 que no son para regalos",
    hook="Semana 3: no lo toques para regalos.",
    thumbnail_text="Semana 3: $210",
    segments=[
        ("Imagen", "Semana 3: $210. El dinero del reto no es para regalos.", "", "M guarding a jar labelled 'Reto' next to a pile of gifts"),
    ],
    caption="Reto de diciembre, semana 3: si vas al día, ya llevas $210 (ejemplo con $10 al día).\nLa regla de esta semana: el dinero del reto no es para regalos. Los regalos salen de tu número de diciembre, no del apartado 'Reto'.\nSi ya lo tocaste, no pasa nada: sigue desde hoy.\n\n" + DIA1 + "\n\n" + RETO + "\n\n" + CTA,
    hashtags=TAGS,
    description="Semana 3 del Reto de diciembre: no lo toques para regalos.",
    sources=[],
    claims=["Example arithmetic: 21 x $10 = $210"],
),
dict(
    key="r-semana-4", format="short", pillar=PRESUPUESTO_P,
    angle="Last check-in (Dec 27): $280 in the example; whatever the number is, it counts; don't spend it in the after-Christmas sales; leave it put until the finale tomorrow, and the $5/$2 totals.",
    title="Reto día 28: lo lograste (con lo que sea)",
    hook="Día 28 del reto. Si fuiste al día con diez, hoy tienes doscientos ochenta. Y si no, también cuenta.",
    thumbnail_text="Día 28: $280",
    segments=[
        ("Gancho", "Día 28: si fuiste al día, $280", "Día 28 del reto. Si fuiste al día con diez, hoy tienes doscientos ochenta. Y si no, también cuenta.", "a full calendar with a star on the 27th"),
        ("Otras versiones", "Con $5: $140 · con $2: $56", "Con cinco al día son ciento cuarenta, y con dos, cincuenta y seis. Más que el 30 de noviembre.", "three jars of different sizes"),
        ("Si fallaste días", "Lo que juntaste vale igual", "¿Fallaste días? Lo que juntaste vale igual. El hábito ya lo empezaste.", "a calendar with a few empty squares"),
        ("Cuidado", "No lo gastes en las rebajas de esta semana", "Esta semana todo está en rebaja. No lo gastes ahí: el reto no era para eso.", "a sale sign and a closed wallet"),
        ("Cierre", "Mañana: qué hacer con lo que juntaste", "Déjalo quieto. Mañana te digo qué hacer con él.", "M closing a jar with a lid"),
    ],
    caption="Reto de diciembre, día 28: si fuiste al día con $10, hoy tienes $280 (ejemplo de la cuenta). Con $5, $140; con $2, $56.\n¿Fallaste días? Lo que juntaste vale igual.\nNo lo gastes en las rebajas de esta semana. Déjalo quieto: mañana te digo qué hacer con él.\n\n" + CTA,
    hashtags=TAGS,
    description="Último día del Reto de diciembre.",
    sources=[],
    claims=["Example arithmetic: 28 x $10 = $280; 28 x $5 = $140; 28 x $2 = $56"],
),
dict(
    key="rc-que-hacer-con-el-reto", format="carousel", pillar=PRESUPUESTO_P,
    angle="Finale (Dec 28): three good homes for the challenge money in order (the January card bill if there's a balance, the first $1,000 emergency fund, a sinking fund for the next remittance or the trip home), plus keeping a smaller automatic transfer going in January.",
    title="Juntaste tu reto: ¿y ahora qué?",
    hook="Ya juntaste el reto. Así le das un buen destino, en este orden.",
    thumbnail_text="¿Y ahora qué?",
    segments=[
        ("Portada", "Juntaste tu reto: ¿y ahora qué?", "Así le das un buen destino, en este orden.", "M holding a full jar labelled 'Reto'"),
        ("1", "1. ¿Debes en la tarjeta? Paga ahí primero", "Si te quedó saldo en la tarjeta después de diciembre, ese interés cuesta más de lo que gana cualquier ahorro.", "a card statement with a balance"),
        ("2", "2. Si no, empieza tu fondo de emergencia", "Si no debes, es el inicio de tu fondo de emergencia: la primera meta es mil dólares.", "a jar labelled 'Colchón $1,000'"),
        ("3", "3. O el próximo envío a casa", "¿Ya tienes colchón? Apártalo para el próximo envío o el viaje a casa, sin tarjeta.", "a jar labelled 'Envío'"),
        ("Enero", "Sigue en enero, aunque sea con menos", "Sigue en enero con una transferencia automática más chica, por ejemplo veinte por semana.", "a calendar with January Sundays marked"),
        ("Ejemplo", "Ejemplo: $20 por semana = $1,040 al año", "Veinte por semana son mil cuarenta al año. Es un ejemplo, no una promesa.", "a small line chart going up"),
        ("Cierre", "Mándaselo a quien hizo el reto contigo", "Mándaselo a quien hizo el reto contigo, y nos vemos en enero.", "two phones sharing a picture"),
    ],
    caption="Juntaste tu Reto de diciembre. Así le das un buen destino, en orden:\n1. ¿Te quedó saldo en la tarjeta? Paga ahí primero.\n2. Si no, empieza tu fondo de emergencia (primera meta: $1,000).\n3. ¿Ya tienes colchón? Apártalo para el próximo envío o el viaje a casa.\nY sigue en enero con una transferencia automática más chica: $20 por semana son $1,040 al año (ejemplo, no promesa).\n\n" + CTA,
    hashtags=TAGS,
    description="Qué hacer con lo que juntaste en el Reto de diciembre.",
    sources=["https://www.consumerfinance.gov/es/"],
    claims=["Example arithmetic: $20 x 52 = $1,040", "Typical credit card APRs exceed savings yields (CFPB/Fed data); keep it general"],
),
]
