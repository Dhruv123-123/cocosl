"""Contenido de "Estafas: guía para papás y abuelos", the Spanish large-print version of Scam Decoded for Seniors.

Adapted from PR #9's seniors pack (launch/scam-decoded/product/seniors-pack/seniors_content.py), not a word-for-word
translation: it adds the scams that hit Spanish-speaking families hardest (the fake notario, the relative "detained" at
the border, virtual kidnapping, the remittance code) and uses "usted", which most abuelos expect.

Machine-written Spanish: a native speaker reviews everything before it is printed or shared (REVIEW_CHECKLIST_MAYORES.md).
The notario and immigration items carry ATTORNEY REVIEW. All example calls, texts and names are made up. Official numbers
were checked in November 2026; re-check them, and that each line really offers Spanish, before every new version.
"""

TITLE = "Estafas: guía para papás y abuelos"
SUBTITLE = "La guía en letra grande para reconocer estafas por teléfono, mensaje, correo y computadora"
VERSION = "noviembre de 2026"
ATTORNEY_LINE = ("Para cualquier trámite de inmigración, vaya solo con un abogado de inmigración con licencia o con un "
                 "representante acreditado por el Departamento de Justicia (DOJ). Un notario no es abogado.")

GOLDEN_RULES = [
    ("No confíe en el nombre que aparece en la pantalla.", "Los estafadores pueden hacer que salga cualquier nombre o número."),
    ("Cuelgue y llame usted.", "Use un número que usted mismo busque: el de su tarjeta, su factura o la página oficial."),
    ("Nunca pague con prisa.", "Los bancos y las agencias de verdad le dan tiempo. Los estafadores nunca."),
    ("Nunca pague con tarjetas de regalo, giros, criptomonedas o efectivo por mensajero.",
     "Solo los estafadores piden eso."),
    ("Nunca comparta un código.", "Si alguien le pide el código que le acaba de llegar por mensaje, es una estafa."),
]

# (title, what they say, what to do, attorney?)
CALLS = [
    ("El nieto en problemas",
     "“Abuela, soy yo. Estoy detenido. Por favor no le diga a mi mamá.”",
     "Cuelgue y llame a su nieto, o a sus papás, al número que usted ya tiene. Las voces se pueden imitar con IA.", False),
    ("El familiar detenido en la frontera",
     "“Su sobrino está detenido. Mande la fianza hoy o lo deportan.”",
     "Cuelgue. Llame a su familia al número de siempre. Nadie cobra una fianza por teléfono ni con tarjetas de regalo.", True),
    ("El secuestro virtual",
     "“Tenemos a su hija. No cuelgue y no llame a nadie, o le hacemos daño.”",
     "Casi siempre es mentira. Desde otro teléfono, llame a su hija o pida a alguien que la llame. Luego llame al 911.", False),
    ("El gobierno",
     "“Habla el Seguro Social. Su número fue suspendido.”",
     "El Seguro Social, el IRS, Medicare e Inmigración no llaman para amenazarle ni para exigir un pago. Cuelgue.", True),
    ("El “departamento de fraude” de su banco",
     "“Paramos un cargo sospechoso. Léame el código que le acabamos de mandar.”",
     "Su banco nunca le pedirá ese código. Cuelgue y llame al número que está detrás de su tarjeta.", False),
    ("Usted ganó un premio",
     "“¡Ganó 2.5 millones de dólares! Solo pague primero los impuestos.”",
     "Los premios de verdad no se pagan. Si tiene que pagar, no ganó nada.", False),
]

TEXTS = [
    ("“Su paquete no se pudo entregar. Pague $1.99 para reprogramar.”",
     "Revise la app o la página oficial de la empresa de paquetería."),
    ("“Tiene un peaje sin pagar. Pague ahora para evitar una multa.”", "Busque usted su cuenta de peaje. No toque el enlace."),
    ("“Hola, ¿es usted Doña Carmen? ¡Perdón, número equivocado!”",
     "No conteste. Una plática amistosa que sigue muchas veces termina en una estafa de inversión."),
    ("“Para cobrar su envío de dinero, mándenos el número de clave.”",
     "Nunca dé la clave o el número de su envío a nadie más que a la persona que lo va a recoger."),
]

# The remittance page: money sent home is a favourite target.
REMESAS = [
    "La clave (el número del envío) es como efectivo. Quien la tiene, cobra el dinero.",
    "Solo se la da a la persona que va a recoger el dinero, y por un número que usted ya conoce.",
    "Si alguien “de la compañía” le pide la clave por teléfono o mensaje, cuelgue. La compañía ya la tiene.",
    "Nunca mande dinero a alguien que solo conoce por internet, aunque diga que es familia.",
    "¿Ya la dio? Llame enseguida a la compañía de envíos al número de su recibo y pida que detengan el pago.",
]

NOTARIO = [
    "En muchos países un notario es casi abogado. En Estados Unidos, un notario público solo sella firmas.",
    "Un notario o “consultor” no puede darle consejo de inmigración ni llenar sus papeles de inmigración.",
    "Desconfíe de quien le promete papeles rápidos, le pide pagar en efectivo o le quita sus documentos originales.",
    "Nunca firme papeles en blanco ni en un idioma que no entiende.",
    "Busque ayuda solo con un abogado de inmigración con licencia o con un representante acreditado por el DOJ. "
    "En justice.gov/eoir hay una lista de organizaciones reconocidas.",
]

ONLINE = [
    "Alguien que solo conoce por internet y que pronto le dice que le ama",
    "Que nunca puede verle en persona ni en videollamada",
    "Que luego necesita dinero para un boleto, un hospital, la aduana o una inversión “segura”",
]

HANG_UP_LINES = [
    "“No hago negocios por teléfono. Yo le llamo al número que tengo.”",
    "“Primero lo voy a hablar con mi familia.”",
    "“Mándemelo por escrito.”",
    "“No, gracias.” (Y cuelgue. No le debe una despedida.)",
]

# Spanish service on each line was checked in November 2026: re-check before every version.
OFFICIAL_NUMBERS = [
    ("Reportar una estafa a la FTC (en español)", "ReporteFraude.ftc.gov o 1-877-382-4357"),
    ("Línea Nacional contra el Fraude a Personas Mayores (Departamento de Justicia)", "1-833-372-8311 (1-833-FRAUD-11)"),
    ("Seguro Social", "1-800-772-1213"),
    ("Medicare", "1-800-633-4227 (1-800-MEDICARE)"),
    ("Dejar de recibir llamadas de ventas: Registro No Llame", "1-888-382-1222 o DoNotCall.gov"),
    ("Reenviar mensajes de estafa, gratis", "7726"),
    ("Si alguien está en peligro", "911"),
]

IF_IT_HAPPENS = [
    ("Pare.", "No mande más dinero, aunque le digan que así recupera el primer pago."),
    ("Llame a su banco", "al número de su tarjeta. Pida que detengan o reviertan el pago."),
    ("¿Tarjetas de regalo o un envío?", "Llame a la compañía al número de la tarjeta o del recibo, y guarde la tarjeta y el recibo."),
    ("Cuénteselo a alguien de confianza.", "Los estafadores cuentan con que usted lo guarde en secreto. No es su culpa: son criminales profesionales."),
    ("Repórtelo", "en ReporteFraude.ftc.gov o llame a la Línea contra el Fraude a Personas Mayores: 1-833-372-8311."),
    ("Cuidado con la segunda estafa.", "Quien le llame ofreciendo “recuperar” su dinero a cambio de un pago es otro estafador."),
]

FRIDGE = [
    "El nombre en la pantalla puede mentir.",
    "Nunca pago con tarjetas de regalo, giros, criptomonedas o efectivo.",
    "Nunca doy un código que me llegó por mensaje, ni la clave de un envío.",
    "Nunca dejo que alguien que me llamó entre a mi computadora.",
    "Prisa + secreto + pago raro = ESTAFA.",
    "Cuelgo y llamo yo, a un número que busco yo.",
    "Papeles de inmigración: solo con abogado o representante acreditado. Nunca con un notario.",
    "¿Tengo dudas? Primero llamo a alguien de mi lista.",
]

# Items the attorney reviewer must read (everything that touches immigration).
ATTORNEY_ITEMS = ["El familiar detenido en la frontera (página 3)", "El gobierno, incluida Inmigración (página 3)",
                  "La página del notario (página 7)", "La línea del notario en la lista del refrigerador",
                  "ATTORNEY_LINE en la portada y en la página del notario"]
