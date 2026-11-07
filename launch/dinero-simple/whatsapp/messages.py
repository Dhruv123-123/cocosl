# Dinero Simple WhatsApp Channel: the first 30 days of broadcasts, in Spanish. One message a day, a weekly rhythm:
# lun consejo, mar alerta de estafa, mié el número de la semana, jue encuesta, vie haz esto hoy,
# sáb lo nuevo de Dinero Simple, dom una pregunta para pensar.
# WhatsApp formatting: *bold*, _italic_. Links only as [ENLACE: ...] placeholders, swapped by hand when posting.
# Machine-written: a fluent Spanish speaker reviews every message. Nothing here is posted automatically.
#
# Each: day, kind, text, poll (question, options) or None, check (facts to confirm) list.

CHANNEL_NAME = "Dinero Simple"
DESCRIPTION = ("Un paso con tu dinero cada día, en español y sin rollos: presupuesto, envíos a tu familia, crédito, "
               "impuestos y cómo no caer en estafas. Información general, no asesoría financiera. Hecho con ayuda de IA "
               "y revisado por personas. Tu número no lo ve nadie: así funcionan los canales.")

M = [
(1, "bienvenida", """👋 *¡Bienvenido a Dinero Simple!*

Aquí vas a recibir *un mensaje al día*, cortito: un consejo, una alerta de estafa, un número que vale la pena saber o una encuesta.

Nada de "hazte rico rápido". Solo pasos chiquitos con tu dinero, en español.

Si conoces a alguien a quien le sirva, reenvíale este canal. 🙌""", None, []),
(2, "alerta", """🚨 *Alerta de estafa: "Mamá, cambié de número"*

Te escribe "tu hijo" o "tu sobrino" desde un número nuevo y, a los pocos mensajes, pide dinero urgente.

*Antes de mandar un dólar:* llámale al número de siempre. Si no contesta, pregúntale algo que solo él sabría.

La prisa es la herramienta del estafador.""", None, []),
(3, "numero", """🔢 *El número de la semana: 4.3*

Un mes tiene unas *4.3 semanas*, no 4.

Por eso, si te pagan cada semana, cuatro cheques no alcanzan para un mes completo de renta y cuentas. Haz tus cuentas con 4.3 y nunca te va a faltar esa semanita.""", None, ["52 / 12 = 4.33"]),
(4, "encuesta", """📊 *Encuesta rápida*

¿Qué es lo que más te cuesta con tu dinero ahora mismo? Vota y la próxima semana te mando consejos sobre lo que gane.""",
 ("¿Qué te cuesta más ahora?", ["Llegar a fin de mes", "Pagar deudas", "Ahorrar algo", "Mandar dinero a mi familia", "Los impuestos"]), []),
(5, "hazlo", """✅ *Haz esto hoy (5 minutos)*

Abre la app de tu banco y activa *tres alertas*:
1. Saldo bajo
2. Compras grandes
3. Depósitos

Así te enteras de todo al momento, y si alguien usa tu tarjeta, lo ves el mismo día.""", None, []),
(6, "nuevo", """🎬 *Lo nuevo en Dinero Simple*

Esta semana publicamos un video sobre cómo hacer tu presupuesto *por semana*, no por mes. Dura menos de un minuto.

[ENLACE: video de la semana]""", None, ["Swap in the week's actual video and title"]),
(7, "pregunta", """💭 *Una pregunta para el domingo*

Si mañana te llegaran $500 que no esperabas, ¿qué harías con ellos?

No hay respuesta correcta. Pero si ya sabes la tuya, ya tienes un plan para la próxima vez que llegue dinero extra (el reembolso, un bono, un aguinaldo).""", None, []),
(8, "consejo", """💡 *Consejo del lunes: tu número semanal*

Toma lo que te queda al mes después de pagar lo fijo (renta, luz, teléfono, deudas y lo que mandas a casa). Divídelo entre 4.3.

Ese es tu *número semanal* para comida, salidas y todo lo demás. Escríbelo y pégalo donde lo veas.""", None, []),
(9, "alerta", """🚨 *Alerta de estafa: el "notario"*

En Estados Unidos, un notario *no es abogado*. Solo certifica firmas.

No puede darte consejo de inmigración ni llenar tus trámites por ti. Para eso: un abogado con licencia o un representante acreditado por el Departamento de Justicia.

Reenvíaselo a quien esté haciendo un trámite.""", None, ["Notarios públicos in the US cannot give immigration legal advice"]),
(10, "numero", """🔢 *El número de la semana: 7726*

Si te llega un mensaje de texto de estafa, *reenvíalo al 7726* (que en el teclado dice SPAM). Tu compañía de celular lo usa para bloquear a quien lo mandó.

Funciona con mensajes de texto (SMS), no con WhatsApp. En WhatsApp: bloquea y reporta.""", None, ["7726 is the carrier spam-reporting short code"]),
(11, "encuesta", """📊 *Encuesta*

¿Cómo mandas dinero a tu familia casi siempre?""",
 ("¿Cómo mandas dinero?", ["Con una app, desde mi cuenta", "En una tienda, en efectivo", "Con tarjeta de crédito", "Alguien lo lleva", "No mando dinero"]), []),
(12, "hazlo", """✅ *Haz esto hoy: compara cuánto llega*

La próxima vez que mandes dinero, antes de pagar, anota *cuánto llega allá* en dos servicios distintos, a la misma hora.

La comisión es solo la mitad del costo. La otra mitad está en el tipo de cambio. Nuestra calculadora gratis te ayuda: [ENLACE: calculadora de envíos]""", None, []),
(13, "nuevo", """🎬 *Lo nuevo en Dinero Simple*

Un carrusel con *7 cosas que comparar antes de mandar dinero*. Guárdalo para tu próximo envío.

[ENLACE: carrusel de la semana]""", None, ["Swap in the week's actual post"]),
(14, "pregunta", """💭 *Para el domingo*

¿Cuál es la cuenta que más te duele pagar cada mes?

Esa es la primera que vale la pena revisar: a veces una llamada de 10 minutos la baja. Mañana te cuento cómo.""", None, []),
(15, "consejo", """💡 *Consejo del lunes: la llamada de 10 minutos*

Llama a tu compañía de celular, internet o seguro del carro y di:

_"Estoy revisando mis gastos y estoy pensando en cambiarme. ¿Qué planes más baratos o descuentos tienen para mí?"_

Muchas atienden en español. Lo peor que puede pasar es que digan que no.""", None, []),
(16, "alerta", """🚨 *Alerta de estafa: "Ganaste un premio"*

Si "ganaste" una rifa o un premio en algo en lo que nunca participaste, *no ganaste nada*.

La trampa llega después: te piden pagar el envío, un impuesto o un "trámite" para cobrar. Un premio de verdad no te cobra por entregarse.""", None, ["FTC: legitimate prizes don't require payment to collect"]),
(17, "numero", """🔢 *El número de la semana: $1,000*

Tu primera meta de ahorro de emergencias no es seis meses de gastos. Es *$1,000*.

Con eso, una llanta ponchada o una visita al doctor ya no van a la tarjeta. Si apartas $125 por quincena, llegas en 4 meses.""", None, ["$125 x 8 = $1,000"]),
(18, "encuesta", """📊 *Encuesta*

¿Tienes un ahorro para emergencias?""",
 ("¿Tienes ahorro para emergencias?", ["Sí, más de $1,000", "Sí, menos de $1,000", "Lo estoy empezando", "Todavía no"]), []),
(19, "hazlo", """✅ *Haz esto hoy: ponle nombre a tu ahorro*

Abre un apartado o una cuenta de ahorro y ponle nombre: *"Colchón"*, *"Viaje"*, *"Para mamá"*.

El dinero con nombre se toca menos. Y programa una transferencia automática el día de pago, aunque sea de $10.""", None, []),
(20, "nuevo", """🎬 *Lo nuevo en Dinero Simple*

Tenemos una guía *gratis* en español: _Tu dinero en orden en 7 días_. Un paso cortito cada día.

[ENLACE: guía gratis]""", None, []),
(21, "pregunta", """💭 *Para el domingo*

Piensa en tu última compra grande. Si pudieras regresar el tiempo, ¿la volverías a hacer?

Si la respuesta es "no", la regla de las 72 horas te puede ayudar: para todo lo que no sea necesario, espera tres días antes de comprar.""", None, []),
(22, "consejo", """💡 *Consejo del lunes: tu crédito con ITIN*

Si no tienes número de Seguro Social, *sí puedes construir crédito con tu ITIN*. Muchas cooperativas y algunos bancos aceptan ITIN para una tarjeta asegurada.

Pregunta siempre si reportan tus pagos a las tres agencias de crédito. Si no reportan, no te ayuda.""", None, ["Bureaus can keep files under an ITIN; lender acceptance varies", "ATTORNEY REVIEW not needed (no immigration content), but keep it general"]),
(23, "alerta", """🚨 *Alerta de estafa: el trabajo que te cobra*

Si una oferta de trabajo te pide pagar algo primero (un curso, un uniforme, un "kit" o la "verificación"), es estafa.

*Ningún trabajo de verdad te cobra por empezar.* Y nunca des tu número de Seguro Social o ITIN antes de una entrevista real.""", None, []),
(24, "numero", """🔢 *El número de la semana: 1%*

Desde 2026, los envíos de dinero al extranjero que pagas *en efectivo* (o con giro postal o cheque de caja) tienen un impuesto federal de *1%*.

Si pagas desde tu cuenta de banco o con débito, no lo pagas.""", None, ["1% remittance excise tax from Jan 1, 2026 on cash, money order and cashier's check funding"]),
(25, "encuesta", """📊 *Encuesta*

¿Revisaste tu reporte de crédito en el último año? Es gratis.""",
 ("¿Revisaste tu reporte de crédito?", ["Sí, este año", "Hace más de un año", "Nunca", "No sabía que era gratis"]), []),
(26, "hazlo", """✅ *Haz esto hoy: tu reporte de crédito, gratis*

Puedes ver tus reportes de crédito de las tres agencias *gratis*, cada semana, en la página oficial: [ENLACE: AnnualCreditReport.com]

Revisa que todas las cuentas sean tuyas. Si hay un error, se disputa gratis.""", None, ["Free weekly reports from all three bureaus at AnnualCreditReport.com"]),
(27, "nuevo", """🎬 *Lo nuevo en Dinero Simple*

¿Te pagan cada semana o cada quincena y no sabes cuánto te va a llegar? Hicimos una *calculadora gratis de sueldo neto*. Lo que escribes no sale de tu celular.

[ENLACE: calculadora de sueldo]""", None, ["The paycheck calculator uses the current year's tables"]),
(28, "pregunta", """💭 *Para el domingo*

¿Qué te gustaría que tu dinero hiciera por ti en un año? ¿Un viaje a casa, salir de una deuda, tener tu colchón?

Escríbelo en una línea, con un número. Mañana te enseño cómo convertirlo en algo automático.""", None, []),
(29, "consejo", """💡 *Consejo del lunes: un propósito que sí se cumple*

Escribe tu meta así:
*"Paso $___ cada ___ a ___ para ___."*

Ejemplo: _"Paso $50 cada quincena a mi apartado del colchón para tener $1,200 en diciembre."_

Y prográmalo hoy en tu banco. Lo automático le gana a la fuerza de voluntad.""", None, ["$50 x 24 = $1,200"]),
(30, "alerta", """🚨 *Alerta de estafa: el número de tu envío*

El número de tu envío de dinero es *como un billete*: solo lo necesita quien lo va a recibir.

Si alguien te lo pide "para verificar" o "para liberar un premio", es estafa. Si ya lo compartiste, llama a la empresa de inmediato.

Gracias por estar aquí este mes. Si el canal te sirve, compártelo con tu familia. 🙏""", None, []),
]
