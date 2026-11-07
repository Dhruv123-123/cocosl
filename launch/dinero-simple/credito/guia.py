"""Lead magnet for the "Crédito sin Seguro Social" series: a free Spanish guide to building US credit with an ITIN.

Same shape as impuestos/guia.py, so impuestos/build_guia.py renders it (credito/build_credito.py does that). Every
section that mentions the ITIN is flagged ATTORNEY REVIEW in the checklist, and a credit expert (HUD-approved housing
counselor, NFCC counselor or credit union lender) checks every credit fact. No bank, card or lender is named.
Machine-written Spanish: a native speaker reviews it before it goes out.
"""

TITLE = "Crédito sin Seguro Social: guía para empezar"
SUBTITLE = "Cómo construir tu historial de crédito en Estados Unidos con ITIN, paso a paso"
DEADLINE = ""
FOOTER = ("*Dinero Simple · Información general, no es asesoría financiera ni legal. Hecho con ayuda de IA y revisado "
          "por personas. Las reglas de cada banco cambian: pregunta antes de abrir cualquier cuenta.*")

INTRO = ("Esta guía es para quien vive y trabaja en Estados Unidos sin número de Seguro Social y quiere empezar su "
         "historial de crédito: para rentar, comprar un carro, pagar menos de seguro o tener una tarjeta para "
         "emergencias. Son cinco pasos, en orden, y las trampas que debes evitar. Es información general: cada banco y "
         "cada cooperativa tiene sus propias reglas, así que pregunta antes de abrir cualquier cuenta.")

ATTORNEY_NOTE = ("**Si tienes preguntas sobre tu situación migratoria:** habla con un abogado de inmigración con "
                 "licencia o con un representante acreditado por el Departamento de Justicia (la lista está en "
                 "justice.gov/eoir). Nunca con un notario ni con alguien que te prometa 'arreglar papeles'.")

SECTIONS = [
dict(id="por-que", title="Por qué importa tu crédito", attorney=False, body="""
Tu **historial de crédito** es el registro de cómo pagas lo que debes. Con él se calcula tu **puntaje de crédito**, un número que muchas empresas revisan antes de:

- rentarte un departamento,
- darte un préstamo para carro, y a qué interés,
- darte un plan de teléfono sin depósito,
- y, en muchos estados, decidir cuánto pagas de seguro de carro.

Sin historial, muchas veces te piden depósitos más grandes o te cobran más intereses. Con un buen historial, ahorras dinero durante años.
""", check=["Uses of credit reports: rental screening, auto loans, phone plans, and (in most states) auto insurance pricing (CFPB)"]),

dict(id="itin", title="Paso 1: el ITIN", attorney=True, body="""
El **ITIN** es un número de nueve dígitos que da el IRS a quien tiene que declarar impuestos y no puede tener número de Seguro Social. Muchos bancos, cooperativas y tarjetas lo aceptan para abrir cuentas.

- **Es solo para impuestos:** no te da permiso para trabajar ni cambia tu situación migratoria.
- **Cómo se pide:** con el formulario **W-7**, por lo general junto con tu declaración de impuestos: por correo, en persona con cita en una oficina del IRS, o con un **Agente Certificador de Aceptación**.
- **El formulario es gratis.** Quien te ayude puede cobrar por su tiempo, pero el IRS no cobra.
- **Vence** si no lo usas en una declaración federal tres años seguidos.

""" + ATTORNEY_NOTE, check=["ITIN: 9-digit IRS number for people who must file and are not eligible for an SSN; for federal tax purposes only",
                            "W-7 options: with a return by mail, IRS Taxpayer Assistance Center by appointment, Certifying Acceptance Agent; no IRS fee",
                            "ITINs not used on a federal return for 3 consecutive years expire Dec 31 of the third year",
                            "ATTORNEY REVIEW"]),

dict(id="cuenta", title="Paso 2: una cuenta de banco o cooperativa", attorney=False, body="""
Antes del crédito necesitas una cuenta. Desde ahí vas a pagar tu tarjeta cada mes.

- **Dónde preguntar:** cooperativas de crédito (credit unions) y bancos de tu zona. Pregunta directo: "¿Abren cuentas con ITIN?".
- **Qué llevar:** tu ITIN, una identificación con foto (pasaporte o matrícula consular, según lo que acepte cada lugar) y prueba de domicilio, como un recibo de luz.
- **Que esté asegurada:** en un banco, que diga **FDIC**; en una cooperativa, **NCUA**. Así tu dinero está protegido hasta $250,000.
- **Evita** las cuentas con cuotas mensuales que no puedes evitar.
""", check=["Some banks and credit unions accept an ITIN plus a foreign passport or consular ID (requirements vary)",
            "FDIC/NCUA insurance: up to $250,000 per depositor, per institution, per ownership category"]),

dict(id="tarjeta", title="Paso 3: la tarjeta asegurada", attorney=False, body="""
Una **tarjeta asegurada** funciona como una tarjeta de crédito normal, pero dejas un depósito que se convierte en tu límite. Por ejemplo: dejas $200 y tu límite es $200.

- **Pregunta antes de abrirla:** "¿Aceptan ITIN?" y "¿Reportan a las tres agencias de crédito (Equifax, Experian y TransUnion)?". Si no reporta, no te ayuda.
- **Úsala poco:** un solo gasto chico al mes, como el teléfono.
- **Págala completa y a tiempo**, cada mes. Así no pagas intereses.
- **Ojo con las cuotas:** evita tarjetas con cuota anual alta o cargos por "activación" o "mantenimiento".
- Después de 6 a 12 meses de buenos pagos, pregunta si te pueden devolver el depósito y pasarte a una tarjeta normal.
""", check=["Secured card deposit usually equals the limit; some issuers accept ITIN applications; not all report to all three bureaus",
            "Paying the full statement balance by the due date avoids purchase interest",
            "Graduation to an unsecured card is issuer-specific (6-12 months is common, not guaranteed)"]),

dict(id="prestamo", title="Paso 4: el préstamo para construir crédito", attorney=False, body="""
Un **préstamo para construir crédito** (credit-builder loan) es un préstamo al revés: el dinero se queda guardado en una cuenta mientras haces pagos chicos cada mes, y al final te lo dan.

- Cada pago a tiempo queda en tu historial.
- Los ofrecen muchas **cooperativas de crédito** y **prestamistas comunitarios** (llamados CDFI), y varios aceptan ITIN.
- **Pregunta:** el costo total (intereses y cuotas) y si reporta a las tres agencias.
- Escoge un pago que puedas hacer **siempre**. Un pago atrasado te hace más daño que no tener el préstamo.
""", check=["Credit-builder loans: funds held in savings or a CD until repaid (CFPB); offered by many credit unions and CDFIs, some to ITIN holders"]),

dict(id="cuidar", title="Paso 5: cómo cuidar tu puntaje", attorney=False, body="""
| Qué pesa | Qué hacer |
|---|---|
| **Pagar a tiempo** (lo que más pesa) | Pon pagos automáticos del mínimo y paga el resto antes de la fecha. |
| **Cuánto usas de tu límite** | Usa menos del 30%. Con un límite de $200, menos de $60. |
| **Cuánto tiempo tienes tu crédito** | No cierres tu primera tarjeta si no te cobra cuota. |
| **Cuentas nuevas** | No abras varias al mismo tiempo. |
| **Tipos de crédito** | Una tarjeta y un préstamo bien pagados ayudan. |

Un puntaje se construye en meses, no en semanas. Tu primer puntaje puede tardar unos seis meses en aparecer.
""", check=["FICO factors: payment history (~35%), amounts owed (~30%), length of history (~15%), new credit (~10%), credit mix (~10%)",
            "A FICO score generally needs at least one account open 6 months and one reported in the last 6 months"]),

dict(id="reportes", title="Tus reportes de crédito, gratis", attorney=True, body="""
Tienes derecho a ver tus **reportes de crédito gratis**. Revísalos para que no haya errores ni cuentas que no son tuyas.

- **Dónde:** AnnualCreditReport.com, por teléfono al **1-877-322-8228** o por correo con el formulario de solicitud. Es el único sitio oficial y es gratis.
- **Sin Seguro Social:** si la verificación en línea no funciona con tu ITIN, pídelos por teléfono o por correo, con copia de tu identificación y prueba de domicilio.
- **Si hay un error:** dispútalo con la agencia de crédito. Es gratis. Si no te responden, pon una queja en consumerfinance.gov/es.

""" + ATTORNEY_NOTE, check=["Free weekly reports from all three bureaus at AnnualCreditReport.com, 1-877-322-8228 or by mail",
                            "How ITIN holders request reports in practice (online identity check may require an SSN): confirm with each bureau",
                            "ATTORNEY REVIEW"]),

dict(id="si-recibes-ss", title="Si después recibes número de Seguro Social", attorney=True, body="""
Si un día recibes número de Seguro Social:

- Avísale al **IRS** para que junte tu historial de impuestos con tu número nuevo, y deja de usar el ITIN.
- Avísale a tu **banco, tu tarjeta y tus préstamos** para que actualicen tu número.
- Revisa tus reportes de crédito unos meses después para confirmar que tu historial sigue contigo.

""" + ATTORNEY_NOTE, check=["After getting an SSN, notify the IRS so ITIN records are combined; stop using the ITIN (IRS)",
                            "Ask creditors to update the identifier; bureaus generally keep the history under the same name and address (confirm with a credit expert)",
                            "ATTORNEY REVIEW"]),

dict(id="trampas", title="Las trampas que debes evitar", attorney=True, body="""
- **"Préstamo garantizado, solo pague primero":** los prestamistas de verdad no te cobran por adelantado para darte un préstamo. Es estafa.
- **"Arreglamos tu crédito" cobrando antes:** la ley no deja que las empresas de reparación de crédito te cobren antes de hacer el trabajo. Todo lo que hacen, tú lo puedes hacer gratis.
- **"Número de privacidad" o "CPN":** te venden un número de nueve dígitos para "empezar de cero". Es una estafa, y usarlo para pedir crédito puede ser un delito.
- **Notarios o "consultores"** que mezclan el crédito con "arreglar papeles". El ITIN no arregla tu situación migratoria.

""" + ATTORNEY_NOTE, check=["Advance-fee loans are a scam signal (FTC); Credit Repair Organizations Act bars charging before services are performed",
                            "FTC/CFPB: CPNs are often stolen SSNs; using one on a credit application can be a federal crime",
                            "ATTORNEY REVIEW"]),

dict(id="ayuda", title="Ayuda gratis", attorney=False, body="""
- **Consejeros de vivienda aprobados por HUD:** muchos dan asesoría de crédito gratis y en español. Búscalos en consumerfinance.gov/es o llama al 1-800-569-4287.
- **Consejería de crédito sin fines de lucro:** busca agencias afiliadas a la NFCC (nfcc.org), con atención en español.
- **CFPB en español:** guías y quejas en consumerfinance.gov/es, o al 855-411-2372.
- **Tu cooperativa de crédito:** pregunta por clases o citas de educación financiera. Muchas son gratis.
""", check=["HUD housing counselor line 1-800-569-4287; CFPB 855-411-2372 (Spanish available); NFCC member agencies offer Spanish service"]),
]

CHECKLIST_1PAGE = [
    "Tengo mi ITIN vigente (o pedí uno con el W-7)",
    "Si tengo dudas migratorias: consulté con un abogado o representante acreditado, nunca con un notario",
    "Abrí una cuenta asegurada (FDIC o NCUA) que acepta ITIN",
    "Pregunté si la tarjeta asegurada reporta a las 3 agencias antes de abrirla",
    "Uso la tarjeta para un solo gasto chico y la pago completa cada mes",
    "Pregunté en mi cooperativa por un préstamo para construir crédito",
    "Uso menos del 30% de mi límite",
    "Pedí mis reportes gratis en AnnualCreditReport.com (o por teléfono o correo)",
    "No pagué a nadie por adelantado para 'darme' crédito ni 'arreglarlo'",
]
