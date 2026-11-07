"""Taller 'Que no te roben' (60 min): slides, speaker notes, worksheets and facilitator notes.

Facts come from the scam series (content-estafas.json), whose claims are listed in REVIEW_CHECKLIST_ESTAFAS.md.
"""
SLUG = "que-no-te-roben"
TITLE = "Que no te roben"
SUBTITLE = "Estafas que buscan a nuestra comunidad, y cómo pararlas"
MINUTES = 60
FREE = True
MATERIALS = ["Proyector o pantalla (o imprima las diapositivas)", "Una copia por persona de las dos hojas de trabajo",
             "Plumas", "Opcional: un rotafolio para anotar las estafas que mencione el grupo"]
AGENDA = [("0–5", "Bienvenida y acuerdos"), ("5–15", "Las 3 señales"), ("15–35", "7 estafas, una por una"),
          ("35–45", "Actividad: ¿estafa o no?"), ("45–52", "Si ya te pasó, y cómo protegerte hoy"),
          ("52–60", "Plan de familia y preguntas")]
CHECK = [
    "Los formularios de USCIS son gratis en uscis.gov y las tarifas se pagan solo a USCIS por sus medios oficiales.",
    "El Departamento de Estado no avisa a los ganadores de la lotería de visas por correo, carta ni llamada.",
    "Congelar el crédito en Equifax, Experian y TransUnion es gratis por ley y no baja el puntaje.",
    "El 7726 (SPAM) funciona con las principales compañías de celular en EE. UU.",
    "Quien cobra por preparar impuestos debe firmar la declaración y poner su PTIN.",
    "ReporteFraude.ftc.gov no pregunta el estatus migratorio; RobodeIdentidad.gov existe en español.",
    "El plazo de 180 días para reportar errores en un envío de dinero (regla de remesas de la CFPB).",
    "El localizador de detenidos de ICE (locator.ice.gov) sigue en línea.",
]
RULES = [
    "Esto es información general, no asesoría legal ni financiera. Dígalo al empezar.",
    "Si alguien pregunta por su caso de inmigración: 'Eso se lo debe ver un abogado con licencia o un representante acreditado. Aquí está cómo encontrar uno.' Nunca opine sobre un caso.",
    "Si alguien cuenta que lo estafaron, agradézcale, recuérdele que no es su culpa y pásele la hoja de los primeros 60 minutos. No pida detalles frente al grupo.",
    "No pida nombres, teléfonos ni datos de nadie. Nadie tiene que contar nada para participar.",
    "No venda nada durante el taller.",
]

S = []  # (kind, title, body, notes)
S.append(("title", TITLE, SUBTITLE,
 "Bienvenida. Preséntese en una frase. Diga: 'En la próxima hora vamos a ver las estafas que más le llegan a nuestra comunidad y qué hacer en cada una. No tienen que contar nada personal. Esto es información general, no asesoría legal.'"))
S.append(("agenda", "Lo que vamos a ver", AGENDA,
 "Repase la agenda rápido. Pida que silencien el celular, pero que lo tengan a la mano: al final vamos a activar dos protecciones juntos."))
S.append(("big", "A gente lista también le pasa", "Son profesionales. Su trabajo es que actúes antes de pensar.",
 "Pregunte: '¿A quién le ha llegado un mensaje o una llamada rara este mes?' Deje que levanten la mano, sin pedir detalles. Diga: 'Si le pasa a alguien, no es por tonto. Estas personas hacen esto todo el día. Hoy aprendemos a reconocer el patrón.'"))
S.append(("three", "Las 3 señales de casi toda estafa", [("Prisa", "'Hoy', 'en una hora', 'último aviso'"), ("Secreto", "'No le digas a nadie, ni al banco'"), ("Pago raro", "Tarjeta de regalo, app, cripto, envío a una persona")],
 "Esta es la idea más importante del taller. Si recuerdan solo esto, ya ganaron. Lea cada señal y pida un ejemplo al grupo. Diga: 'Dos de estas tres juntas: cuelga, no toques nada y verifica tú.'"))
S.append(("message", "5 señales en un solo mensaje", ("Último aviso: tu cuenta se suspende en 2 horas por saldo pendiente. Paga ya para evitar un cargo de $45: bit.ly/pago-cuenta",
  ["No lo esperabas", "Cuenta regresiva", "Amenaza o premio", "Su enlace, no el tuyo", "Te pide pagar"]),
 "Este mensaje es inventado. Lea el mensaje en voz alta. Pregunte qué les parece raro antes de mostrar la lista. Luego recorra las 5 señales. Diga: 'Con 2 o más, no toques el enlace: abre la app oficial o escribe tú la página.'"))
S.append(("scam", "1 · El 'notario'", ("Aquí un notario NO es abogado. Solo certifica firmas.",
  ["SÍ: abogado con licencia (pide su número y búscalo en el colegio de abogados del estado)", "SÍ: representante acreditado por el Departamento de Justicia",
   "NO: notario, 'consultor' o 'gestor' de inmigración", "Nadie puede garantizarte una visa o un permiso"]),
 "Explique que en muchos países de Latinoamérica un notario es un abogado con mucha preparación, y en EE. UU. no. Un trámite mal hecho puede dañar un caso. Nunca le dejen documentos originales a nadie: copias. No opine sobre casos de nadie."))
S.append(("scam", "2 · La llamada 'de inmigración'", ("USCIS no cobra por teléfono ni con tarjetas de regalo.",
  ["Los formularios son gratis en uscis.gov", "Las tarifas se pagan solo a USCIS, por sus medios oficiales", "¿Te llamaron? Cuelga y revisa tu caso tú en uscis.gov",
   "Fíjate que la página termine en .gov"]),
 "Mismo patrón: prisa y miedo. Muestre que una página puede verse oficial y no serlo; la terminación .gov es la pista. La lotería de visas es igual: inscribirse es gratis y nadie avisa por correo que ganaste."))
S.append(("scam", "3 · 'Tenemos a tu familiar'", ("Fianza urgente o secuestro virtual: nadie está detenido ni secuestrado.",
  ["Te piden no colgar y pagar ya, por app o tarjetas de regalo", "Usan datos de tus redes y a veces una voz copiada con IA", "Cuelga y llama tú a tu familiar",
   "Pide la palabra clave de la familia"]),
 "Es la más dura emocionalmente. Hable despacio. Explique la palabra clave: una palabra que la familia elige hoy y que nunca se publica. Si la persona en el teléfono no la sabe, es estafa. Si alguien de verdad está detenido, se busca en el localizador oficial de ICE y se llama a un abogado, nunca se paga a una cuenta personal."))
S.append(("scam", "4 · 'Habla tu banco'", ("Ningún banco te pide mover tu dinero para protegerlo.",
  ["En la pantalla dice el nombre de tu banco: eso se puede falsificar", "Saben tu nombre y los últimos 4 números de tu tarjeta", "'Pasa tus ahorros a una cuenta segura' = estafa",
   "Cuelga y llama al número de atrás de tu tarjeta"]),
 "Esta le roba los ahorros de toda la vida a mucha gente mayor. Insista: el número que aparece en pantalla se puede falsificar. Colgar y llamar al número de la tarjeta es siempre seguro."))
S.append(("scam", "5 · El código de WhatsApp", ("'Te mandé un código por error, ¿me lo pasas?'",
  ["Ese código abre TU cuenta en otro teléfono", "Muchas veces escribe un amigo al que ya le robaron la cuenta", "Nadie necesita tu código: ni el banco ni soporte",
   "Activa la verificación en dos pasos hoy"]),
 "Diga que al final lo activamos juntos. Con la cuenta robada, le piden dinero a todos los contactos."))
S.append(("scam", "6 · El 'trabajo' que te cuesta", ("Si te piden pagar para pagarte, no es trabajo.",
  ["'Califica productos desde casa': los primeros pagos son reales, luego te piden recargar", "'Recibe dinero y reenvíalo, quédate con el 10%': es dinero robado",
   "A las 'mulas de dinero' les cierran la cuenta y pueden tener problemas legales", "Di que no y avisa a tu banco"]),
 "Dos versiones del mismo engaño. La segunda es peligrosa porque la persona termina usada para mover dinero robado. Si ya recibió algo, que no lo mande y llame hoy a su banco."))
S.append(("scam", "7 · El preparador que no firma", ("En temporada de impuestos: si no firma tu declaración, aléjate.",
  ["Quien te cobra por hacer tus impuestos debe firmar y poner su PTIN", "Cuidado: reembolso enorme prometido sin ver tus papeles", "Cuidado: te cobra un porcentaje del reembolso",
   "Pide copia firmada y que el reembolso llegue a tu cuenta"]),
 "Si algo sale mal, quien responde ante el IRS es la persona, no el preparador. Mencione que VITA prepara impuestos gratis para muchas familias y acepta ITIN. Esto es información general, no asesoría de impuestos."))
S.append(("activity", "Actividad: ¿estafa o no?", ("10 minutos · Hoja 1", ["En parejas, lean los 4 mensajes de la hoja", "Marquen las señales que ven", "Decidan: ¿qué harían?"]),
 "Reparta la Hoja 1. Dé 6 minutos en parejas y 4 para comentar. Respuestas: 1) estafa (prisa, pago raro, su enlace); 2) estafa (código de WhatsApp); 3) estafa de 'mula' (te pagan por reenviar dinero); 4) probablemente real, pero igual se verifica desde la app oficial, no desde el mensaje. Lo importante no es acertar, sino la regla: verifica tú, por tu cuenta."))
S.append(("steps", "Si ya te pasó: los primeros 60 minutos", ["Llama a tu banco al número de tu tarjeta", "Llama a la app o a la tarjeta de regalo", "Cambia contraseñas, primero la del correo",
  "Congela tu crédito", "Repórtalo en español: ReporteFraude.ftc.gov", "Anota todo. Cuidado con quien cobra por 'recuperar' tu dinero"],
 "Diga primero: no es tu culpa, y la rapidez es lo que más importa. El reporte de la FTC está en español y el formulario no pregunta el estatus migratorio. Si usaron sus datos: RobodeIdentidad.gov. El que llama ofreciendo recuperar el dinero a cambio de un pago es la siguiente estafa."))
S.append(("three", "Protégete hoy (5 minutos)", [("Congela tu crédito", "Equifax, Experian y TransUnion. Gratis, no baja tu puntaje"), ("Reenvía al 7726", "Los mensajes de estafa, gratis. No contestes, ni 'STOP'"),
  ("Verificación en dos pasos", "En WhatsApp: Configuración, Cuenta")],
 "Si hay tiempo, active la verificación en dos pasos de WhatsApp con el grupo, en vivo. Congelar el crédito se hace en las páginas de las tres agencias; si alguien va a pedir un préstamo, se descongela un día en línea."))
S.append(("activity", "Tu plan de familia", ("8 minutos · Hoja 2", ["Elijan su palabra clave (y no la publiquen)", "Anoten los números a los que llamarían", "Compártanlo esta semana con sus papás"]),
 "Reparta la Hoja 2. Pida que la llenen ahora y que la platiquen en la cena esta semana. Abra preguntas. Recuerde las reglas: nada de opinar sobre casos de inmigración ni de impuestos. Cierre con la frase: prisa, secreto y pago raro, cuelga y verifica tú."))
S.append(("close", "Prisa · secreto · pago raro", "Cuelga y verifica tú.",
 "Agradezca. Diga dónde pueden encontrar más: la organización que los recibe y dinerosimple.netlify.app. No pida datos ni haga ventas."))

WORKSHEETS = [
 ("Hoja 1 · ¿Estafa o no?", "Lean cada mensaje. Marquen las señales y escriban qué harían.", [
   ("Mensaje 1", "USPS: Tu paquete no pudo entregarse por dirección incompleta. Actualiza y paga $1.99 hoy o será devuelto: usps-entregas-ayuda.com"),
   ("Mensaje 2", "Hola prima, te llegó un código mío por error, ¿me lo pasas? Es urgente 🙏"),
   ("Mensaje 3", "Trabajo desde casa: recibe depósitos en tu cuenta y reenvíalos a nuestros clientes. Te quedas con el 10%. Sin experiencia."),
   ("Mensaje 4", "Tu banco: se hizo un cargo de $612.40 en tu tarjeta. Si no lo reconoces, revisa en la app de tu banco."),
  ], ["Prisa", "Secreto", "Pago raro", "Su enlace", "No lo esperaba"]),
 ("Hoja 2 · El plan de mi familia", "Llénenla hoy y platíquenla en casa esta semana.", [
   ("Nuestra palabra clave", "(No la escriban en redes ni en el celular)"),
   ("Si alguien llama pidiendo dinero urgente", "Colgamos y llamamos a: __________________  y  __________________"),
   ("El número de atrás de mi tarjeta", "______________________"),
   ("Para reportar una estafa, en español", "ReporteFraude.ftc.gov   ·   Robo de identidad: RobodeIdentidad.gov"),
   ("Ayuda con inmigración", "Solo un abogado con licencia o un representante acreditado. Nunca un notario."),
  ], ["Congelé mi crédito en las 3 agencias", "Activé la verificación en dos pasos en WhatsApp", "Guardé el 7726 para reenviar mensajes de estafa", "Platiqué este plan con mi familia"]),
]
