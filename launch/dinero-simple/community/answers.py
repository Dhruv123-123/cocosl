"""Answer bank for Quora en español and Facebook groups: 30 drafts, no links. Built into ANSWER_BANK.md by build_answers.py."""
A = []  # (topic, question, answer, check)

A.append(("bancos", "¿Puedo abrir una cuenta de banco si solo tengo ITIN?",
"""Sí, en muchos lugares se puede. No hay una ley que exija número de Seguro Social para abrir una cuenta. Cada banco o cooperativa decide qué documentos acepta.

Lo que normalmente te piden:
- Tu ITIN (o a veces solo pasaporte o matrícula consular, según el lugar)
- Una identificación con foto
- Un comprobante de domicilio, como un recibo de luz o un contrato de renta

Las cooperativas de crédito (credit unions) suelen ser más flexibles, sobre todo las que atienden a la comunidad hispana. Antes de ir, llama y pregunta tal cual: "¿Abren cuentas con ITIN y matrícula consular?" Te ahorras la vuelta.

Y revisa que la cuenta esté asegurada (FDIC en bancos, NCUA en cooperativas) y que no tenga cargos mensuales que no puedas evitar.""",
["Las cooperativas y bancos que aceptan ITIN o matrícula varían por lugar."]))

A.append(("crédito", "¿Cómo saco mi primera tarjeta de crédito si no tengo historial?",
"""La forma más común de empezar es una tarjeta asegurada (secured card). Dejas un depósito, por ejemplo $200, y ese es tu límite. La usas como una tarjeta normal y el banco reporta tus pagos a las agencias de crédito.

Para que te sirva:
1. Úsala para algo chico y fijo, como el celular.
2. Págala completa cada mes, de preferencia en automático.
3. Usa poco del límite: menos de 30% es una buena regla, y menos de 10% es mejor.

Antes de sacarla, pregunta dos cosas: si reporta a las tres agencias (Equifax, Experian y TransUnion) y si después de un tiempo te devuelven el depósito y la pasan a tarjeta normal.

Hay tarjetas aseguradas que aceptan ITIN, sobre todo en cooperativas de crédito. En 6 a 12 meses de pagos a tiempo, normalmente ya tienes un puntaje con el que puedes pedir algo mejor.""",
["Regla general de uso del crédito por debajo de 30%.", "Plazo típico de 6 a 12 meses para tener puntaje."]))

A.append(("envíos", "¿Cuál es la forma más barata de mandar dinero a México?",
"""Depende del día y de cuánto mandes, así que la mejor respuesta es saber comparar.

Lo que de verdad te cuesta un envío son dos cosas: la comisión y el tipo de cambio. Muchas apps dicen "sin comisión", pero te dan un tipo de cambio peor y ahí se cobran.

Cómo comparar en 2 minutos:
1. Abre dos o tres apps o servicios con la misma cantidad, por ejemplo $300.
2. No mires la comisión. Mira cuántos pesos le llegan a tu familia.
3. El que deje más pesos, ese gana ese día.

También fíjate en cómo recibe tu familia: depósito a cuenta, retiro en tienda o en banco. A veces el más barato no le queda cerca.

Por ley, el servicio te tiene que dar un recibo con lo que pagaste, el tipo de cambio y lo que va a recibir tu familia. Y si hay un error, tienes 180 días para reclamarlo.""",
["Recibo obligatorio y plazo de 180 días para errores (regla de remesas de la CFPB)."]))

A.append(("impuestos", "Si declaro impuestos con ITIN, ¿se entera inmigración?",
"""Esta pregunta es muy importante y no tiene una respuesta igual para todos, así que te digo lo que sí sé y a quién preguntarle.

Las reglas sobre qué datos se comparten entre agencias han cambiado y siguen en las cortes, así que no te voy a dar una respuesta general: eso lo tiene que ver alguien con tu caso enfrente. Hay consultas gratis o de bajo costo: busca la lista de proveedores gratuitos del Departamento de Justicia (EOIR).

Lo que te recomiendo:
- Si tienes un caso de inmigración abierto o te preocupa tu situación, habla primero con un abogado de inmigración con licencia o con un representante acreditado por el Departamento de Justicia. No con un notario.
- Muchas organizaciones comunitarias dan esa consulta gratis o barata.

Declarar también tiene beneficios (por ejemplo, dejar un historial de que cumpliste), pero eso lo tiene que pesar alguien que conozca tu caso.""",
["ALTO RIESGO: estado actual del acuerdo IRS–DHS de 2025 y de las demandas. Que lo lea un abogado de inmigración antes de publicar.", "Protecciones de confidencialidad de la sección 6103."]))

A.append(("deudas", "¿Qué hago primero, pagar mis deudas o ahorrar?",
"""Las dos cosas, en este orden:

1. Junta un fondo chico de emergencia primero, aunque sea $500 o $1,000. Sin eso, la próxima llanta ponchada o la próxima consulta al doctor se van otra vez a la tarjeta, y la deuda nunca baja.
2. Luego, todo lo extra a las deudas con interés alto (las tarjetas, que muchas veces cobran 20% o más).
3. Cuando ya no tengas deudas caras, regresa a hacer crecer el ahorro, hasta 3 a 6 meses de gastos.

Si en tu trabajo hay match del 401(k), aporta al menos lo suficiente para recibirlo completo, aun mientras pagas deudas. Es dinero que te dan gratis.

Lo que más ayuda no es la estrategia perfecta, es tener una cantidad fija cada mes, en automático, para cada cosa.""",
["Tasas típicas de tarjetas de crédito por encima de 20%."]))

A.append(("deudas", "¿Qué es mejor para pagar deudas, avalancha o bola de nieve?",
"""Las dos funcionan. La diferencia es qué deuda atacas primero.

Avalancha: pagas el mínimo en todas y lo extra va a la de interés más alto. Es la que menos intereses te cobra en total.

Bola de nieve: pagas el mínimo en todas y lo extra va a la de saldo más chico. Terminas una deuda más rápido y eso te da ánimo para seguir.

En las dos, cuando terminas una deuda, lo que pagabas en ella se suma a la siguiente. Por eso cada vez vas más rápido.

¿Cuál escoger? Si eres de los que necesita ver avances para no aflojar, bola de nieve. Si la diferencia de intereses es grande (por ejemplo, una tarjeta al 29% contra un préstamo al 7%), avalancha.

La peor opción es no escoger ninguna y pagar un poquito de todo cada mes.""",
[]))

A.append(("presupuesto", "¿Cómo hago un presupuesto si mis ingresos cambian cada mes?",
"""Haz tu plan con tu mes más bajo, no con el promedio.

1. Revisa lo que ganaste los últimos 6 meses y toma el mes normal más bajo (no cuentes uno donde estuviste enfermo, por ejemplo).
2. Con esa cantidad cubre primero lo fijo: renta, luz, celular, mínimos de deudas, el envío a tu familia.
3. Lo que sobre de ese mes bajo es tu dinero para la semana: súper, gasolina, lo demás.
4. En los meses buenos, lo que pase de tu mes bajo no se gasta de inmediato. Va a un "colchón" para los meses flojos, y cuando el colchón tenga un mes de gastos, lo extra va a metas.

Si trabajas por tu cuenta, aparta también para impuestos cada vez que cobras. Mucha gente se lleva una sorpresa en abril por no hacerlo.

Es menos emocionante que planear con tu mejor mes, pero es lo que evita quedarte corto.""",
["Si trabaja por su cuenta, debe pagar impuestos estimados; no dar porcentaje."]))

A.append(("ahorro", "¿Es mala idea guardar el dinero en la casa?",
"""Entiendo por qué mucha gente lo hace: desconfianza en los bancos, comisiones, o miedo por papeles. Pero el dinero en casa tiene riesgos que mucha gente no piensa:

- Si hay un robo, un incendio o una inundación, se pierde y nadie te lo repone.
- Es más fácil gastarlo "nomás tantito".
- No te ayuda a construir historial con ningún banco.

En una cuenta asegurada por FDIC (bancos) o NCUA (cooperativas), tu dinero está protegido hasta $250,000 aunque el banco quiebre.

Si te preocupa abrir cuenta, empieza poquito: una cuenta de ahorro en una cooperativa que atienda a la comunidad, con ITIN o matrícula si es lo que tienes. Deja en casa solo lo de la semana.""",
["Límite de $250,000 de FDIC/NCUA por depositante, por banco, por tipo de cuenta."]))

A.append(("crédito", "¿Cómo se calcula el puntaje de crédito?",
"""El puntaje más usado (FICO) se calcula con cinco cosas, más o menos con este peso:

- Pagos a tiempo: alrededor de 35%. Es lo más importante. Un pago con más de 30 días de atraso pega fuerte.
- Cuánto debes contra tu límite: alrededor de 30%. Usar menos de 30% de tus tarjetas ayuda, y menos de 10% ayuda más.
- Antigüedad de tus cuentas: alrededor de 15%.
- Crédito nuevo: alrededor de 10%. Muchas solicitudes juntas bajan un poco.
- Tipos de crédito: alrededor de 10%.

Lo que NO cuenta: tu sueldo, tu estatus migratorio, cuánto tienes ahorrado.

Puedes ver tus reportes de crédito gratis en el sitio oficial de reportes anuales. Revísalos: los errores son más comunes de lo que crees, y se pueden disputar gratis.""",
["Porcentajes de FICO (35/30/15/10/10).", "Reportes gratis semanales en AnnualCreditReport.com (el texto no incluye el enlace)."]))

A.append(("crédito", "¿Si cancelo una tarjeta de crédito me baja el puntaje?",
"""Puede bajarlo, por dos razones:

1. Pierdes ese límite de crédito. Si tienes deuda en otras tarjetas, ahora usas un porcentaje mayor de tu crédito total, y eso baja el puntaje.
2. Con el tiempo, puede acortar la antigüedad promedio de tus cuentas, sobre todo si es tu tarjeta más vieja.

Por eso, si la tarjeta no cobra anualidad, muchas veces conviene dejarla abierta, ponerle un cargo chico (como una suscripción) y pagarla en automático para que no la cierren por falta de uso.

Sí conviene cancelarla si:
- Cobra una anualidad que no vale la pena (antes, pregunta si te la cambian a una sin anualidad).
- No te puedes controlar con ella. Tu tranquilidad vale más que unos puntos.""",
[]))

A.append(("estafas", "Me llamaron de 'inmigración' diciendo que tengo un problema y que pague hoy. ¿Es real?",
"""Casi seguro es una estafa. Cuelga.

Las agencias de inmigración no te llaman para cobrarte por teléfono, ni te piden pagar con tarjetas de regalo, transferencias a una persona o apps de pago. Las tarifas de trámites se pagan solo a USCIS, por sus medios oficiales.

Las señales de estafa casi siempre son las mismas tres: prisa ("hoy", "en una hora"), secreto ("no le digas a nadie") y un pago raro.

Qué hacer:
- No des datos ni pagues nada.
- Revisa tu caso tú mismo en el sitio oficial de USCIS con tu número de recibo.
- Si tienes dudas sobre tu caso, habla con un abogado con licencia o un representante acreditado.
- Repórtalo a la FTC; tienen formulario en español y no te preguntan tu estatus migratorio.

El número que sale en la pantalla se puede falsificar, así que no te fíes de eso.""",
["El formulario de la FTC en español no pregunta el estatus migratorio."]))

A.append(("estafas", "¿Un notario me puede ayudar con mis papeles de inmigración?",
"""No. Y es una de las estafas que más daño hace en nuestra comunidad.

En muchos países de Latinoamérica, un notario es un abogado con mucha preparación. En Estados Unidos no: un notario público solo certifica firmas. No puede darte consejos de inmigración ni escoger o llenar tus formularios.

Quién sí puede ayudarte:
- Un abogado con licencia. Pide su número y búscalo en el colegio de abogados de su estado.
- Un representante acreditado que trabaje en una organización reconocida por el Departamento de Justicia. Muchas cobran poco o nada.

Señales de alerta: te garantiza el resultado, se queda con tus papeles originales, te pide firmar formularios en blanco o te cobra por formularios (que son gratis).

Un trámite mal hecho puede dañar tu caso, así que vale la pena buscar bien.""",
[]))

A.append(("ahorro", "¿Las tandas son buena idea?",
"""Las tandas tienen cosas buenas: te obligan a ahorrar, no cobran intereses y se basan en la confianza.

Pero tienen riesgos que conviene tener claros:
- Si alguien deja de pagar después de recibir su turno, los demás pierden.
- Si te toca de los últimos, en realidad estás prestando tu dinero sin interés.
- No hay a quién reclamar si algo sale mal.
- No te ayuda a construir crédito.

Si vas a entrar:
- Solo con gente que conozcas bien y que haya cumplido antes.
- Anoten todo: quién paga cuánto, cuándo y a quién le toca.
- No metas dinero que necesites para renta o comida.

También existen "círculos de préstamo" organizados por algunas organizaciones sin fines de lucro, que funcionan como tanda pero reportan los pagos a las agencias de crédito. Pregunta en tu comunidad si hay alguno cerca.""",
["Existencia de círculos de préstamo que reportan a las agencias (p. ej., programas de organizaciones sin fines de lucro)."]))

A.append(("inversión", "¿Cómo empiezo a invertir si tengo poco dinero?",
"""Con $100 al mes, o incluso menos, ya se puede. Lo importante es empezar y ser constante.

Antes de invertir:
- Ten un fondo de emergencia, aunque sea chico.
- Paga las deudas de interés alto (las tarjetas), porque cuestan más de lo que normalmente gana una inversión.

Por dónde empezar:
1. Si tu trabajo tiene 401(k) con match, aporta al menos para recibirlo completo. Es lo primero.
2. Después, una cuenta de retiro como una IRA.
3. Dentro de la cuenta, mucha gente usa fondos indexados de bajo costo, que compran un pedacito de cientos de empresas a la vez.

Fíjate en la comisión anual del fondo (el "expense ratio"). Un fondo que cobra 1% contra uno de 0.05% hace una diferencia enorme en 30 años.

Y no inviertas dinero que vas a necesitar en los próximos 5 años: la bolsa sube y baja.""",
["Expense ratios típicos de fondos indexados.", "Recomendación general de horizonte de 5 años."]))

A.append(("inversión", "¿Qué es el 'match' del 401(k) y por qué dicen que no lo deje pasar?",
"""El match es dinero que tu empleador pone en tu cuenta de retiro cuando tú también pones.

Ejemplo común: "te igualamos 50% hasta el 6% de tu sueldo". Si ganas $3,000 al mes y pones 6% ($180), tu trabajo pone $90 más. Es como un aumento que solo recibes si participas.

Por eso dicen que no lo dejes pasar: es difícil encontrar otra forma de ganar 50% o 100% al instante sobre tu dinero.

Cosas a revisar con Recursos Humanos:
- Cuánto es el match y hasta qué porcentaje.
- Si hay un periodo de "vesting", es decir, cuánto tiempo tienes que quedarte para que el dinero del match sea tuyo.
- Qué fondos hay. Muchas veces hay un fondo "target date" con el año de tu retiro, que es una opción sencilla.

Si apenas te alcanza, empieza con lo mínimo para el match completo y súbele 1% cada año.""",
["Fórmulas de match son ejemplos, cada plan es distinto."]))

A.append(("bancos", "Me aparece un cargo en mi tarjeta que no reconozco. ¿Qué hago?",
"""Muévete rápido, pero con calma:

1. Revisa primero que no sea algo tuyo con otro nombre. Muchos comercios aparecen con un nombre distinto al de la tienda, o es una suscripción que olvidaste.
2. Si no es tuyo, llama al número que viene atrás de tu tarjeta (no a un número que te llegó por mensaje). Pide que bloqueen la tarjeta y que disputen el cargo.
3. Cambia la contraseña de tu banco y de tu correo.
4. Revisa los cargos de los últimos dos o tres meses: a veces empiezan con cargos chiquitos de prueba.

Con tarjeta de crédito estás bastante protegido por ley. Con tarjeta de débito también, pero el tiempo cuenta más: entre más rápido lo reportes, mejor.

Y si alguien abrió cuentas a tu nombre, congela tu crédito en las tres agencias. Es gratis.""",
["Protecciones de la ley para crédito y débito y los plazos del débito (Reg E)."]))

A.append(("deudas", "Necesito dinero ya. ¿Un préstamo de día de pago (payday) es buena opción?",
"""Casi siempre es la opción más cara. Muchos préstamos de día de pago cobran una cuota que, convertida a tasa anual, sale arriba de 300%, y mucha gente termina sacando uno nuevo para pagar el anterior.

Antes de firmar, revisa estas opciones:
- Préstamos chicos en cooperativas de crédito. Muchas tienen préstamos "alternativos al payday" con tasa limitada.
- Pedirle al acreedor más tiempo. La compañía de luz, el hospital o tu casero muchas veces aceptan un plan de pagos si llamas antes de atrasarte.
- Un adelanto de tu sueldo con tu empleador.
- Organizaciones comunitarias o parroquias que ayudan con renta o servicios en emergencias.

Si de plano lo vas a sacar, pide por escrito el costo total en dólares y la fecha de pago, y no saques otro para cubrirlo.""",
["Tasas anuales típicas de payday por encima de 300%.", "Préstamos PAL de cooperativas federales (límite de tasa)."]))

A.append(("ahorro", "¿Cómo junto un fondo de emergencia si apenas me alcanza?",
"""Con poquito y en automático. La meta no es juntar 6 meses de gastos este año; es tener los primeros $500.

Ideas que funcionan:
- Programa una transferencia automática el día de pago, aunque sea de $20. Lo que no ves, no lo gastas.
- Ponlo en una cuenta aparte, que no esté pegada a tu tarjeta de débito.
- Cada vez que termines de pagar algo (una deuda, un plan del celular), manda esa misma cantidad al ahorro.
- Reembolso de impuestos, aguinaldo, horas extra: decide antes de recibirlos qué parte va al fondo.
- Revisa tus suscripciones y cancela una que no uses. Esa cantidad, directo al ahorro.

$20 por semana son más de $1,000 en un año. Y eso ya cubre muchas emergencias que hoy terminan en la tarjeta.""",
[]))

A.append(("impuestos", "¿Pago a alguien para que me haga los impuestos o los hago yo?",
"""Depende de tu caso, pero antes de pagar, revisa si calificas para ayuda gratis.

El programa VITA prepara impuestos gratis a personas con ingresos bajos o moderados, con voluntarios certificados por el IRS. Muchos sitios atienden en español y aceptan ITIN, y algunos ayudan a sacar o renovar el ITIN.

Si vas a pagarle a alguien:
- Por ley, quien te cobra por preparar tus impuestos tiene que firmar la declaración y poner su número de preparador (PTIN). Si no quiere firmar, aléjate.
- Desconfía si te promete un reembolso enorme sin ver tus papeles o si te cobra un porcentaje del reembolso.
- Pide que el reembolso llegue a tu propia cuenta y que te den una copia firmada.

Recuerda que si algo sale mal, tú respondes ante el IRS, no el preparador.""",
["Requisitos actuales de ingreso de VITA para este año.", "Obligación de firmar y poner PTIN."]))

A.append(("impuestos", "Ya declaré. ¿Cuándo me llega mi reembolso?",
"""Si declaraste en línea y pediste depósito directo, la mayoría de los reembolsos llegan en menos de 21 días. En papel tarda bastante más.

Excepciones comunes:
- Si pediste el crédito por ingreso del trabajo (EITC) o el crédito tributario adicional por hijos, por ley el IRS no puede soltar esos reembolsos antes de mediados de febrero. Si declaraste temprano, eso es normal.
- Si hay un error, falta un documento o el IRS necesita verificar tu identidad, te mandan una carta. Contéstala rápido.
- Si tu declaración tiene ITIN nuevo o renovado, puede tardar más.

Puedes revisar el estado en la herramienta oficial del IRS para ver dónde está tu reembolso. Necesitas tu número (SSN o ITIN), tu estado civil para declarar y la cantidad exacta.

Y cuidado: el IRS no te llama ni te manda mensajes para pedirte datos para "liberar" tu reembolso.""",
["Plazo de 21 días.", "Retención de la Ley PATH para EITC/ACTC hasta mediados de febrero."]))

A.append(("estafas", "Me ofrecieron un trabajo de recibir dinero en mi cuenta y mandarlo a otra persona. ¿Es legal?",
"""No es un trabajo. Es una estafa, y la persona que pone su cuenta es la que más se arriesga.

Ese dinero casi siempre viene de otra víctima de fraude. Te usan para moverlo y que no lo puedan rastrear. A eso le llaman "mula de dinero".

Lo que te puede pasar:
- Que el banco te cierre la cuenta y te pida devolver el dinero, aunque ya lo hayas mandado.
- Que te cueste abrir otra cuenta después.
- Problemas legales, aunque no supieras de dónde venía.

Si ya recibiste algo, no lo mandes a nadie. Llama hoy a tu banco al número de tu tarjeta y cuéntales lo que pasó. Y avísale a tus conocidos: este "trabajo" se ofrece mucho en grupos de empleo y en WhatsApp.""",
[]))

A.append(("familia", "¿Cómo ayudo a mi familia en mi país sin quedarme sin nada?",
"""Ayudar a la familia es parte de nuestra vida, y no tienes que dejar de hacerlo. Lo que ayuda es planearlo como un gasto más, no como lo que sobra.

1. Decide una cantidad fija al mes que puedas sostener, y trátala como la renta: sale primero.
2. Ten un fondo aparte para las emergencias de allá (una enfermedad, una reparación). Así, cuando llegue la llamada, no sale de tu renta ni de la tarjeta.
3. Si te piden más de lo que puedes, está bien decir "este mes puedo mandar esto". Mejor una ayuda constante que una grande y luego nada.
4. Compara cada vez cuánto le llega a tu familia con cada servicio de envío. Unos pesos de diferencia, cada mes, suman mucho.

Y no te olvides de ti: tu fondo de emergencia y tu retiro también son una forma de cuidar a tu familia a futuro.""",
[]))

A.append(("deudas", "Tengo una deuda en cobranza. ¿Qué hago?",
"""No pagues nada todavía. Primero verifica que la deuda sea real y que sea tuya.

1. Pide por escrito que te validen la deuda. Por ley, el cobrador tiene que mandarte información sobre lo que debes, y si lo pides a tiempo (normalmente dentro de 30 días de su primer aviso), tiene que pausar el cobro hasta mandarte la validación.
2. Revisa que la cantidad y la cuenta coincidan con tus reportes de crédito.
3. Cuidado con las llamadas de supuestos cobradores que piden pago inmediato por tarjeta de regalo o transferencia: es una estafa común.
4. Si la deuda es tuya, puedes negociar. Muchas veces aceptan menos del total o un plan de pagos. Consigue el acuerdo por escrito antes de pagar.

Ojo: en algunos casos, hacer un pago puede reiniciar el plazo legal de una deuda muy vieja. Si es una deuda de hace muchos años, consulta a una agencia de asesoría de crédito sin fines de lucro o a un abogado antes de pagar.""",
["Derecho de validación y plazo de 30 días (FDCPA/Regla F).", "Reinicio del plazo de prescripción varía por estado."]))

A.append(("deudas", "¿Me conviene consolidar mis deudas en un solo préstamo?",
"""Puede convenir, pero solo si se cumplen dos cosas:

1. La tasa del préstamo nuevo es claramente más baja que la que pagas hoy (contando las comisiones de apertura).
2. No vuelves a usar las tarjetas que liquidaste. Si no, terminas con el préstamo y con las tarjetas llenas otra vez.

Haz la cuenta en dólares, no en pagos mensuales. Un pago mensual más bajo a veces solo significa que pagas por más años y al final pagas más.

Cuidado con las empresas de "arreglo de deudas" (debt settlement) que te piden dejar de pagar y mandarles a ellos el dinero. Cobran comisiones altas, tu crédito se daña y no hay garantía.

Si quieres ayuda para decidir, una agencia de asesoría de crédito sin fines de lucro puede revisar tu caso, muchas veces gratis o barato.""",
[]))

A.append(("crédito", "¿Cómo congelo mi crédito y para qué sirve?",
"""Congelar tu crédito hace que nadie pueda abrir una tarjeta o un préstamo nuevo a tu nombre, porque los prestamistas no pueden ver tu reporte.

- Es gratis, por ley.
- No baja tu puntaje.
- Tus tarjetas y préstamos de ahora siguen funcionando normal.

Se hace en las tres agencias, cada una por separado: Equifax, Experian y TransUnion. En cada página creas una cuenta y lo activas. Toma unos 10 minutos en total.

Cuando vayas a pedir crédito (una tarjeta, un carro, un departamento), lo descongelas en línea por unos días y luego se vuelve a bloquear.

Es de las mejores protecciones que hay contra el robo de identidad, y casi nadie la usa.""",
["Congelamiento gratis por ley desde 2018."]))

A.append(("pareja", "Mi pareja y yo siempre peleamos por dinero. ¿Cómo lo manejamos?",
"""Casi siempre el pleito no es por el dinero, sino porque cada quien cree que el otro gasta "de más" en cosas distintas. Lo que ayuda es tener un plan juntos y un poco de libertad para cada quien.

Una forma que funciona para muchas parejas:
1. Sumen lo que entra y hagan juntos una lista de los gastos fijos de la casa.
2. Decidan juntos cuánto va a ahorro, deudas y el envío a la familia, si lo hay.
3. Lo que sobra se divide: una parte para la casa (súper, salidas juntos) y una cantidad igual para cada uno, que cada quien gasta sin dar explicaciones.
4. Una vez a la semana, 20 minutos, revisan cómo van. Sin reclamos del pasado, solo el plan de la próxima semana.

Si ganan muy distinto, pueden aportar a lo común en proporción a lo que gana cada quien.

Lo más importante: que no haya deudas ni cuentas escondidas.""",
[]))

A.append(("presupuesto", "¿Cómo dejo de vivir de quincena en quincena?",
"""Lo que más ayuda es romper el ciclo una vez, con un pequeño colchón, y luego cuidarlo.

1. Junta un colchón de unos cientos de dólares, aunque tardes unos meses. Con eso ya no dependes del día de pago para cubrir una sorpresa.
2. Haz un plan con dos partes: lo fijo (que se paga en automático el día de pago) y un número por semana para todo lo demás.
3. Busca los gastos "sorpresa" que no son sorpresa: placas del carro, regalos, regreso a clases. Divide su costo del año entre 12 y apártalo cada mes.
4. Revisa una vez a la semana, 20 minutos: cuánto llevas gastado y si viene algo pesado.

Y si los gastos fijos se comen casi todo tu sueldo, la solución está en bajar uno grande (la renta, el carro, el plan del celular, los seguros), no en dejar el cafecito.""",
[]))

A.append(("vivienda", "¿Se puede comprar casa con ITIN?",
"""Sí, existen hipotecas para personas con ITIN, aunque no todos los bancos las ofrecen. Las dan algunos bancos, cooperativas de crédito e instituciones de desarrollo comunitario.

Lo que normalmente piden:
- Un enganche más alto que una hipoteca común, muchas veces de 10% a 20% o más.
- Historial de impuestos de 2 años, más o menos.
- Historial de crédito, o pruebas de pagos a tiempo (renta, servicios) si no tienes puntaje.
- La tasa suele ser algo más alta.

Antes de empezar:
- Habla con una agencia de asesoría de vivienda aprobada por HUD. Muchas atienden en español y son gratis o baratas.
- Si tienes un caso de inmigración, consulta también con un abogado de inmigración con licencia.

Desconfía de quien te "garantiza" la aprobación o te pide dinero por adelantado para conseguirte el préstamo.""",
["Rangos de enganche y requisitos típicos de hipotecas ITIN (varían por prestamista).", "Agencias de asesoría de vivienda aprobadas por HUD con servicio en español."]))

A.append(("carro", "¿Me conviene comprar carro a crédito aunque el interés sea alto?",
"""Antes de decidir, mira el costo total, no el pago mensual. En el lote te van a preguntar "¿cuánto quiere pagar al mes?", y con eso te alargan el plazo hasta que cuadra.

Ejemplo: un préstamo de $20,000 a 6 años con 18% de interés te cuesta en total cerca de $32,800. El mismo préstamo al 7% cuesta unos $24,500. Son más de $8,000 de diferencia.

Lo que ayuda:
- Saca la aprobación de tu préstamo antes de ir al lote, en una cooperativa o banco. Así llegas con una tasa para comparar.
- Negocia el precio del carro aparte del financiamiento y del carro que entregas.
- Considera un carro usado confiable y más barato, aunque no sea el que querías.
- No firmes extras que no entiendes (garantías extendidas, seguros) sin leerlos.

Si tu crédito es bajo, a veces conviene esperar unos meses, mejorar el puntaje y juntar un enganche más grande.""",
["Cálculo: $20,000 a 72 meses: 18% → pago ~$456, total ~$32,840; 7% → pago ~$341, total ~$24,550."]))

A.append(("estafas", "Un 'primo' me escribió por WhatsApp desde otro número pidiendo dinero urgente. ¿Qué hago?",
"""Antes de mandar un solo dólar, verifica por fuera de esa conversación.

Es una estafa muy común: alguien se hace pasar por un familiar, dice que cambió de número o que está en problemas, y pide dinero rápido y en secreto. A veces usan fotos de redes sociales y hasta audios con una voz copiada.

Qué hacer:
1. Llama tú al número que ya tenías de tu familiar, o a alguien que esté con él.
2. Hazle una pregunta que solo él sepa.
3. Si la familia tiene una palabra clave, pídela.
4. Si no puedes verificar, no mandes nada. Un problema real aguanta una llamada.

Y si alguien te pide "un código que te llegó por error", no lo pases: es el código que abre tu propia cuenta de WhatsApp. Activa la verificación en dos pasos en la configuración de WhatsApp.""",
[]))

assert len(A) == 30, len(A)
