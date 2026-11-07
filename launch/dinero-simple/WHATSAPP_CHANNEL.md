# Dinero Simple: WhatsApp Channel kit

A WhatsApp Channel is a one-way broadcast: you post, followers read, react and vote in polls. Followers can't see each other or your number, and you can't see theirs. For this audience, WhatsApp is where family news, prices and warnings already travel, so a channel with one useful message a day can grow by forwarding alone. Nothing in this kit is posted automatically: Dhruv (or whoever runs the channel) posts every message by hand.

## Set up the channel (15 minutes)

1. In WhatsApp, open **Updates** (Novedades) → **+** → **Create channel**. Use the brand phone or a dedicated number, not a personal one, if you can.
2. **Name:** Dinero Simple
3. **Description** (paste as is; a fluent speaker checks it first):

   > Un paso con tu dinero cada día, en español y sin rollos: presupuesto, envíos a tu familia, crédito, impuestos y cómo no caer en estafas. Información general, no asesoría financiera. Hecho con ayuda de IA y revisado por personas. Tu número no lo ve nadie: así funcionan los canales.

4. **Picture:** the round brand logo from `brand-kit/` (the piggy-bank mascot on coral).
5. **Settings:** allow emoji reactions (they're the main signal you'll get). Turn on the setting that keeps the channel in the public directory once you have a few weeks of posts.
6. Copy the **channel link** (Share → Copy link). Add it to `sites/dinero-simple/site.json` → `"socials"` as `"WhatsApp": "<link>"`, so it shows in the site footer, and rebuild the site. Put it on the Instagram and TikTok bios through the link page, and in the newsletter footer in place of `[ENLACE: canal de WhatsApp]`.

## Posting rules

- **One message a day**, at the same time. 7:30 pm Eastern works for workers after their shift. More than one a day and people mute the channel.
- **Weekly rhythm:**
  - Monday: a tip
  - Tuesday: a scam alert
  - Wednesday: the number of the week
  - Thursday: a poll
  - Friday: "haz esto hoy"
  - Saturday: what's new from Dinero Simple
  - Sunday: a question to think about
- **Short.** Every message fits on one phone screen (under 700 characters). Bold with `*asteriscos*`, italics with `_guiones bajos_`. At most one or two emoji.
- **Links:** the messages use `[ENLACE: ...]` placeholders. Swap each for the real link with `utm_source=whatsapp&utm_medium=channel&utm_campaign=dia-NN`, or delete the line. No more than one message in three should carry a link: the channel earns trust by being useful in the message itself.
- **Polls:** post them as WhatsApp polls (the 📊 attach option), not as text. Next week's Monday tip should follow the winning answer.
- **Same rules as all Spanish copy:** a fluent speaker reviews every message before it goes out, check the facts listed under "Verificar", and anything about immigration sends people to a licensed attorney or DOJ-accredited representative, never a notario.
- Never post anything that names a real person who wrote to you, and never post "testimonials".

## Grow it by hand (no ads, no bought followers, no adding people)

WhatsApp Channels grow by people choosing to follow. Never add anyone to a group or list without asking, and never post the link in groups that don't allow promotion.

1. **Your own circle first (week 1):** send the link one by one to 20 people you know who would find it useful, with a personal line: _"Empecé un canal con consejos de dinero en español, uno al día. Si te sirve, síguelo."_ Post it on your own WhatsApp Status (Estado) twice in the first week.
2. **Everywhere the brand already is (week 1):**
   - The `/links/` page and the bios.
   - The newsletter footer.
   - The end of every long YouTube description.
   - A pinned comment on the best-performing TikTok each week.
   - One line at the end of the welcome email.
3. **Make the messages forwardable (always):** the scam alerts get forwarded the most. End some of them with "Reenvíaselo a quien...". Every forward shows the channel name.
4. **Partners and workshops (month 2 on):** print the channel's QR code (Share → QR) on the workshop worksheets and the B2B partner one-pager (`partners-b2b/`). Ask partner organizations if they'd share the link with their members, by hand, with their permission.
5. **Answer, don't spam:** in Facebook groups and Quora (`ANSWER_BANK.md`), answer the question fully, with no link. Put the channel link in your profile only.
6. **Measure weekly:** followers, reactions per message and poll votes, in a simple table. Keep the message types that get reactions; drop the ones that don't.

## The first 30 days


### Día 1 · Bienvenida

```
👋 *¡Bienvenido a Dinero Simple!*

Aquí vas a recibir *un mensaje al día*, cortito: un consejo, una alerta de estafa, un número que vale la pena saber o una encuesta.

Nada de "hazte rico rápido". Solo pasos chiquitos con tu dinero, en español.

Si conoces a alguien a quien le sirva, reenvíale este canal. 🙌
```

*307 caracteres*
- [ ] Revisión de hablante nativo


### Día 2 · Alerta de estafa

```
🚨 *Alerta de estafa: "Mamá, cambié de número"*

Te escribe "tu hijo" o "tu sobrino" desde un número nuevo y, a los pocos mensajes, pide dinero urgente.

*Antes de mandar un dólar:* llámale al número de siempre. Si no contesta, pregúntale algo que solo él sabría.

La prisa es la herramienta del estafador.
```

*305 caracteres*
- [ ] Revisión de hablante nativo


### Día 3 · El número de la semana

```
🔢 *El número de la semana: 4.3*

Un mes tiene unas *4.3 semanas*, no 4.

Por eso, si te pagan cada semana, cuatro cheques no alcanzan para un mes completo de renta y cuentas. Haz tus cuentas con 4.3 y nunca te va a faltar esa semanita.
```

*235 caracteres*
- [ ] Verificar: 52 / 12 = 4.33
- [ ] Revisión de hablante nativo


### Día 4 · Encuesta

```
📊 *Encuesta rápida*

¿Qué es lo que más te cuesta con tu dinero ahora mismo? Vota y la próxima semana te mando consejos sobre lo que gane.
```

**Encuesta de WhatsApp:** ¿Qué te cuesta más ahora?
- Llegar a fin de mes
- Pagar deudas
- Ahorrar algo
- Mandar dinero a mi familia
- Los impuestos

*138 caracteres*
- [ ] Revisión de hablante nativo


### Día 5 · Haz esto hoy

```
✅ *Haz esto hoy (5 minutos)*

Abre la app de tu banco y activa *tres alertas*:
1. Saldo bajo
2. Compras grandes
3. Depósitos

Así te enteras de todo al momento, y si alguien usa tu tarjeta, lo ves el mismo día.
```

*210 caracteres*
- [ ] Revisión de hablante nativo


### Día 6 · Lo nuevo en Dinero Simple

```
🎬 *Lo nuevo en Dinero Simple*

Esta semana publicamos un video sobre cómo hacer tu presupuesto *por semana*, no por mes. Dura menos de un minuto.

[ENLACE: video de la semana]
```

*175 caracteres*
- [ ] Verificar: Swap in the week's actual video and title
- [ ] Revisión de hablante nativo


### Día 7 · Pregunta del domingo

```
💭 *Una pregunta para el domingo*

Si mañana te llegaran $500 que no esperabas, ¿qué harías con ellos?

No hay respuesta correcta. Pero si ya sabes la tuya, ya tienes un plan para la próxima vez que llegue dinero extra (el reembolso, un bono, un aguinaldo).
```

*256 caracteres*
- [ ] Revisión de hablante nativo


### Día 8 · Consejo del lunes

```
💡 *Consejo del lunes: tu número semanal*

Toma lo que te queda al mes después de pagar lo fijo (renta, luz, teléfono, deudas y lo que mandas a casa). Divídelo entre 4.3.

Ese es tu *número semanal* para comida, salidas y todo lo demás. Escríbelo y pégalo donde lo veas.
```

*269 caracteres*
- [ ] Revisión de hablante nativo


### Día 9 · Alerta de estafa

```
🚨 *Alerta de estafa: el "notario"*

En Estados Unidos, un notario *no es abogado*. Solo certifica firmas.

No puede darte consejo de inmigración ni llenar tus trámites por ti. Para eso: un abogado con licencia o un representante acreditado por el Departamento de Justicia.

Reenvíaselo a quien esté haciendo un trámite.
```

*319 caracteres*
- [ ] Verificar: Notarios públicos in the US cannot give immigration legal advice
- [ ] Revisión de hablante nativo


### Día 10 · El número de la semana

```
🔢 *El número de la semana: 7726*

Si te llega un mensaje de texto de estafa, *reenvíalo al 7726* (que en el teclado dice SPAM). Tu compañía de celular lo usa para bloquear a quien lo mandó.

Funciona con mensajes de texto (SMS), no con WhatsApp. En WhatsApp: bloquea y reporta.
```

*277 caracteres*
- [ ] Verificar: 7726 is the carrier spam-reporting short code
- [ ] Revisión de hablante nativo


### Día 11 · Encuesta

```
📊 *Encuesta*

¿Cómo mandas dinero a tu familia casi siempre?
```

**Encuesta de WhatsApp:** ¿Cómo mandas dinero?
- Con una app, desde mi cuenta
- En una tienda, en efectivo
- Con tarjeta de crédito
- Alguien lo lleva
- No mando dinero

*60 caracteres*
- [ ] Revisión de hablante nativo


### Día 12 · Haz esto hoy

```
✅ *Haz esto hoy: compara cuánto llega*

La próxima vez que mandes dinero, antes de pagar, anota *cuánto llega allá* en dos servicios distintos, a la misma hora.

La comisión es solo la mitad del costo. La otra mitad está en el tipo de cambio. Nuestra calculadora gratis te ayuda: [ENLACE: calculadora de envíos]
```

*311 caracteres*
- [ ] Revisión de hablante nativo


### Día 13 · Lo nuevo en Dinero Simple

```
🎬 *Lo nuevo en Dinero Simple*

Un carrusel con *7 cosas que comparar antes de mandar dinero*. Guárdalo para tu próximo envío.

[ENLACE: carrusel de la semana]
```

*158 caracteres*
- [ ] Verificar: Swap in the week's actual post
- [ ] Revisión de hablante nativo


### Día 14 · Pregunta del domingo

```
💭 *Para el domingo*

¿Cuál es la cuenta que más te duele pagar cada mes?

Esa es la primera que vale la pena revisar: a veces una llamada de 10 minutos la baja. Mañana te cuento cómo.
```

*183 caracteres*
- [ ] Revisión de hablante nativo


### Día 15 · Consejo del lunes

```
💡 *Consejo del lunes: la llamada de 10 minutos*

Llama a tu compañía de celular, internet o seguro del carro y di:

_"Estoy revisando mis gastos y estoy pensando en cambiarme. ¿Qué planes más baratos o descuentos tienen para mí?"_

Muchas atienden en español. Lo peor que puede pasar es que digan que no.
```

*304 caracteres*
- [ ] Revisión de hablante nativo


### Día 16 · Alerta de estafa

```
🚨 *Alerta de estafa: "Ganaste un premio"*

Si "ganaste" una rifa o un premio en algo en lo que nunca participaste, *no ganaste nada*.

La trampa llega después: te piden pagar el envío, un impuesto o un "trámite" para cobrar. Un premio de verdad no te cobra por entregarse.
```

*272 caracteres*
- [ ] Verificar: FTC: legitimate prizes don't require payment to collect
- [ ] Revisión de hablante nativo


### Día 17 · El número de la semana

```
🔢 *El número de la semana: $1,000*

Tu primera meta de ahorro de emergencias no es seis meses de gastos. Es *$1,000*.

Con eso, una llanta ponchada o una visita al doctor ya no van a la tarjeta. Si apartas $125 por quincena, llegas en 4 meses.
```

*243 caracteres*
- [ ] Verificar: $125 x 8 = $1,000
- [ ] Revisión de hablante nativo


### Día 18 · Encuesta

```
📊 *Encuesta*

¿Tienes un ahorro para emergencias?
```

**Encuesta de WhatsApp:** ¿Tienes ahorro para emergencias?
- Sí, más de $1,000
- Sí, menos de $1,000
- Lo estoy empezando
- Todavía no

*49 caracteres*
- [ ] Revisión de hablante nativo


### Día 19 · Haz esto hoy

```
✅ *Haz esto hoy: ponle nombre a tu ahorro*

Abre un apartado o una cuenta de ahorro y ponle nombre: *"Colchón"*, *"Viaje"*, *"Para mamá"*.

El dinero con nombre se toca menos. Y programa una transferencia automática el día de pago, aunque sea de $10.
```

*250 caracteres*
- [ ] Revisión de hablante nativo


### Día 20 · Lo nuevo en Dinero Simple

```
🎬 *Lo nuevo en Dinero Simple*

Tenemos una guía *gratis* en español: _Tu dinero en orden en 7 días_. Un paso cortito cada día.

[ENLACE: guía gratis]
```

*149 caracteres*
- [ ] Revisión de hablante nativo


### Día 21 · Pregunta del domingo

```
💭 *Para el domingo*

Piensa en tu última compra grande. Si pudieras regresar el tiempo, ¿la volverías a hacer?

Si la respuesta es "no", la regla de las 72 horas te puede ayudar: para todo lo que no sea necesario, espera tres días antes de comprar.
```

*248 caracteres*
- [ ] Revisión de hablante nativo


### Día 22 · Consejo del lunes

```
💡 *Consejo del lunes: tu crédito con ITIN*

Si no tienes número de Seguro Social, *sí puedes construir crédito con tu ITIN*. Muchas cooperativas y algunos bancos aceptan ITIN para una tarjeta asegurada.

Pregunta siempre si reportan tus pagos a las tres agencias de crédito. Si no reportan, no te ayuda.
```

*303 caracteres*
- [ ] Verificar: Bureaus can keep files under an ITIN; lender acceptance varies
- [ ] Verificar: ATTORNEY REVIEW not needed (no immigration content), but keep it general
- [ ] Revisión de hablante nativo


### Día 23 · Alerta de estafa

```
🚨 *Alerta de estafa: el trabajo que te cobra*

Si una oferta de trabajo te pide pagar algo primero (un curso, un uniforme, un "kit" o la "verificación"), es estafa.

*Ningún trabajo de verdad te cobra por empezar.* Y nunca des tu número de Seguro Social o ITIN antes de una entrevista real.
```

*290 caracteres*
- [ ] Revisión de hablante nativo


### Día 24 · El número de la semana

```
🔢 *El número de la semana: 1%*

Desde 2026, los envíos de dinero al extranjero que pagas *en efectivo* (o con giro postal o cheque de caja) tienen un impuesto federal de *1%*.

Si pagas desde tu cuenta de banco o con débito, no lo pagas.
```

*237 caracteres*
- [ ] Verificar: 1% remittance excise tax from Jan 1, 2026 on cash, money order and cashier's check funding
- [ ] Revisión de hablante nativo


### Día 25 · Encuesta

```
📊 *Encuesta*

¿Revisaste tu reporte de crédito en el último año? Es gratis.
```

**Encuesta de WhatsApp:** ¿Revisaste tu reporte de crédito?
- Sí, este año
- Hace más de un año
- Nunca
- No sabía que era gratis

*75 caracteres*
- [ ] Revisión de hablante nativo


### Día 26 · Haz esto hoy

```
✅ *Haz esto hoy: tu reporte de crédito, gratis*

Puedes ver tus reportes de crédito de las tres agencias *gratis*, cada semana, en la página oficial: [ENLACE: AnnualCreditReport.com]

Revisa que todas las cuentas sean tuyas. Si hay un error, se disputa gratis.
```

*260 caracteres*
- [ ] Verificar: Free weekly reports from all three bureaus at AnnualCreditReport.com
- [ ] Revisión de hablante nativo


### Día 27 · Lo nuevo en Dinero Simple

```
🎬 *Lo nuevo en Dinero Simple*

¿Te pagan cada semana o cada quincena y no sabes cuánto te va a llegar? Hicimos una *calculadora gratis de sueldo neto*. Lo que escribes no sale de tu celular.

[ENLACE: calculadora de sueldo]
```

*223 caracteres*
- [ ] Verificar: The paycheck calculator uses the current year's tables
- [ ] Revisión de hablante nativo


### Día 28 · Pregunta del domingo

```
💭 *Para el domingo*

¿Qué te gustaría que tu dinero hiciera por ti en un año? ¿Un viaje a casa, salir de una deuda, tener tu colchón?

Escríbelo en una línea, con un número. Mañana te enseño cómo convertirlo en algo automático.
```

*227 caracteres*
- [ ] Revisión de hablante nativo


### Día 29 · Consejo del lunes

```
💡 *Consejo del lunes: un propósito que sí se cumple*

Escribe tu meta así:
*"Paso $___ cada ___ a ___ para ___."*

Ejemplo: _"Paso $50 cada quincena a mi apartado del colchón para tener $1,200 en diciembre."_

Y prográmalo hoy en tu banco. Lo automático le gana a la fuerza de voluntad.
```

*286 caracteres*
- [ ] Verificar: $50 x 24 = $1,200
- [ ] Revisión de hablante nativo


### Día 30 · Alerta de estafa

```
🚨 *Alerta de estafa: el número de tu envío*

El número de tu envío de dinero es *como un billete*: solo lo necesita quien lo va a recibir.

Si alguien te lo pide "para verificar" o "para liberar un premio", es estafa. Si ya lo compartiste, llama a la empresa de inmediato.

Gracias por estar aquí este mes. Si el canal te sirve, compártelo con tu familia. 🙏
```

*357 caracteres*
- [ ] Revisión de hablante nativo
