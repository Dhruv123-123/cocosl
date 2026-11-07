"""Taller 'Tu presupuesto en 20 minutos' (75 min), based on El Presupuesto de 20 Minutos (launch/dinero-simple/product/)."""
SLUG = "tu-presupuesto-en-20-minutos"
TITLE = "Tu presupuesto en 20 minutos"
SUBTITLE = "Un solo número por semana, y 20 minutos para revisarlo"
MINUTES = 75
FREE = False
MATERIALS = ["Proyector o pantalla (o imprima las diapositivas)", "Una copia por persona de las dos hojas de trabajo", "Plumas y calculadora (la del celular sirve)",
             "Pida antes que traigan, si pueden, un talón de pago o su estado de cuenta (no lo van a mostrar a nadie)",
             "Opcional: copias impresas de la guía El Presupuesto de 20 Minutos si su organización tiene licencia"]
AGENDA = [("0–5", "Bienvenida"), ("5–15", "La idea: 4 líneas y un número"), ("15–35", "Pasos 1 a 3 + Actividad 1"),
          ("35–55", "Pasos 4 a 6 + Actividad 2"), ("55–65", "Ponlo en automático y la rutina de 20 minutos"), ("65–75", "Casos especiales y preguntas")]
CHECK = ["El ejemplo de Daniela suma bien: $3,500 − $2,150 − $200 − $350 = $800; $800 × 12 ÷ 52 = $184.62.",
         "Las cuentas de ahorro aseguradas por FDIC (bancos) o NCUA (cooperativas)."]
RULES = ["Esto es información general, no asesoría financiera. Dígalo al empezar.",
         "Nadie tiene que mostrar ni decir sus números. Las hojas son para cada persona.",
         "Si alguien está en una crisis (desalojo, cobranza, corte de luz), refiéralo a la organización que los recibe o a una agencia de asesoría de crédito sin fines de lucro, después del taller.",
         "No recomiende bancos, tarjetas ni productos específicos. No venda nada durante el taller."]

S = []
S.append(("title", TITLE, SUBTITLE,
 "Bienvenida. Diga: 'Hoy cada quien sale con su número semanal: cuánto puede gastar esta semana en todo lo demás, sin sentir culpa. Nadie va a ver sus números. Esto es información general, no asesoría financiera.'"))
S.append(("agenda", "Lo que vamos a hacer", AGENDA, "Repase la agenda. Pida que tengan a la mano el talón de pago o la app del banco, si la tienen."))
S.append(("big", "¿Por qué fallan los presupuestos?", "Te piden decenas de decisiones chiquitas cada día.",
 "Pregunte: '¿Quién ha intentado hacer un presupuesto y lo dejó?' Normalmente muchos levantan la mano. Diga: 'No es falta de disciplina. Casi todos los presupuestos piden anotar y clasificar cada gasto. Este pide una decisión al mes y una revisión a la semana.'"))
S.append(("four", "Cada dólar va a una de 4 líneas", [("1 · Gastos fijos", "Renta, luz, celular, mínimos de deudas, el envío fijo a tu familia"), ("2 · Fondos", "Gastos que llegan, pero no cada mes: carro, regalos, renovaciones"),
  ("3 · Metas", "Fondo de emergencia, pagos extra a deudas, inversión"), ("4 · Semanal", "Todo lo demás: súper, gasolina, comer fuera, diversión")],
 "Explique: las líneas 1, 2 y 3 se deciden una vez al mes y se pagan solas. Solo la línea 4 necesita su atención durante el mes, y es un solo número."))
S.append(("bullets", "Por qué un número por semana", ["Una semana es corta: si te pasas el martes, lo corriges el domingo", "Un número cabe en la cabeza: 'me quedan $61'",
  "Súper, comida fuera y diversión salen de la misma bolsa: tú decides", "Una mala semana no se come la renta"],
 "Dé el ejemplo en la caja del súper: con un número mensual te enteras el día 28. Con uno semanal, lo sabes cada semana."))
S.append(("table", "Paso 1 · Tu sueldo neto al mes", ([("Te pagan…", "Neto al mes ="), ("Cada semana", "cheque × 52 ÷ 12"), ("Cada dos semanas", "cheque × 26 ÷ 12"), ("Dos veces al mes", "cheque × 2"), ("Una vez al mes", "el cheque")],
  "Neto = lo que de verdad cae en tu cuenta. Si cambia, usa tu mes bajo normal."),
 "Haga un ejemplo en voz alta: cheque de $800 cada dos semanas = 800 × 26 ÷ 12 = $1,733 al mes. Si el ingreso cambia (propinas, temporada, por obra), se usa el mes normal más bajo de los últimos seis."))
S.append(("bullets", "Pasos 2 y 3 · Tus gastos fijos", ["Vivienda: renta, seguro", "Servicios: luz, agua, gas, internet, celular", "Transporte: pago y seguro del carro",
  "Pagos mínimos de cada deuda", "Envío fijo a tu familia", "Suscripciones (cancela las olvidadas)"],
 "Diga: si los fijos pasan de más o menos 60% del neto, el número semanal se va a sentir apretado, y lo que más ayuda es bajar un fijo grande (vivienda, carro, celular, seguros), no dejar el cafecito. Truco: buscar en el estado de cuenta 'monthly', 'subscription', 'autopay'."))
S.append(("activity", "Actividad 1", ("10 minutos · Hoja 1, parte A", ["Escribe tu sueldo neto al mes", "Anota tus gastos fijos y súmalos", "Si no sabes un número exacto, pon un estimado un poco alto"]),
 "Camine por el salón. Ayude con la conversión del sueldo. Nadie tiene que compartir. Si alguien no tiene ingreso fijo, que use su mes bajo."))
S.append(("formula", "Paso 4 · Tus fondos de previsión", ("Costo del año ÷ 12 = lo que apartas cada mes", [("Mantenimiento del carro", "$480 al año → $40"), ("Regalos y fiestas", "$600 al año → $50"),
  ("Viajes a ver a la familia", "$480 al año → $40")]),
 "Pregunte: '¿Qué gasto los agarró de sorpresa el año pasado?' (registro del carro, regreso a clases, una quinceañera). Casi ninguno fue sorpresa: tenía fecha. Por eso se aparta un poco cada mes."))
S.append(("steps", "Paso 5 · Tus metas, en este orden", ["Fondo de emergencia de un mes de gastos fijos", "Pagos extra a deudas con interés alto (8% o más)", "Crecer el fondo de emergencia a 3–6 meses",
  "Invertir a largo plazo, empezando por el match de tu trabajo"],
 "Diga: elijan una cantidad que puedan mantener cada mes. Aquí gana la constancia, no el tamaño. Se puede subir en cualquier ajuste mensual."))
S.append(("formula", "Paso 6 · Tu número semanal", ("(Neto − fijos − fondos − metas) × 12 ÷ 52", [("¿Por qué no ÷ 4?", "Un mes tiene 4.33 semanas"), ("Redondea hacia abajo", "Te deja un colchón chico"),
  ("¿No alcanza para vivir?", "Baja una meta por ahora")]),
 "Insista en el × 12 ÷ 52. Dividir entre 4 regala una semana que no existe: justo el hueco de los meses con cinco semanas. Si el número no es realista, mejor bajar una meta que abandonar el plan en la semana dos."))
S.append(("example", "El mes de Daniela (ejemplo)", [("Sueldo neto", "$3,500"), ("− Gastos fijos", "$2,150"), ("− Fondos", "$200"), ("− Metas", "$350"), ("= Bolsa del mes", "$800"), ("× 12 ÷ 52", "$184 por semana")],
 "Daniela es un ejemplo inventado. Con $184 por semana cubre el súper (unos $85), la gasolina (unos $35) y le quedan unos $64 para comer fuera y diversión. No hay categorías que vigilar: ella decide dentro de sus $184."))
S.append(("activity", "Actividad 2", ("10 minutos · Hoja 1, parte B", ["Anota tus fondos y tus metas", "Haz la cuenta de tu número semanal", "Pregúntate: ¿se puede vivir con este número?"]),
 "Ayude con la cuenta. Si a alguien le sale negativo: planeó más de lo que gana; primero se recortan metas o fondos, luego fijos. Celebre a quien termina: ya tiene su número."))
S.append(("three", "Ponlo en automático", [("Cheques", "Cae tu sueldo. Los fijos salen solos"), ("Ahorro", "Fondos y emergencia, el día de pago"), ("Gasto semanal", "Solo tu número. Cuando se acaba, se acabó la semana")],
 "La cuenta aparte para el gasto semanal es opcional pero ayuda mucho: el saldo es lo que queda de la semana. Muchos bancos y cooperativas abren una segunda cuenta gratis; recomiende buscar que esté asegurada (FDIC o NCUA), sin recomendar un banco en particular."))
S.append(("four", "La rutina de 20 minutos", [("0–5 · Mira", "Abre tus cuentas y anota saldos"), ("5–10 · Anota", "Un solo número: cuánto gastaste"), ("10–15 · Revisa", "¿Salieron los fijos? ¿Algún cargo raro?"), ("15–20 · Decide", "Un paso para la próxima semana")],
 "El mismo día y a la misma hora cada semana, con temporizador. Si se saltan una semana, no la reconstruyen: anotan el total de las dos y siguen. El hábito importa más que el registro perfecto. Una vez al mes, otros 20 minutos para ajustar el plan."))
S.append(("bullets", "Si tu caso es distinto", ["Te pagan cada dos semanas: divide cada transferencia a la mitad", "Ingreso que cambia: planea con tu mes bajo; lo extra va a metas",
  "En pareja: un plan, y cada quien su número semanal", "Ayudas a tu familia: el envío va en gastos fijos o en un fondo"],
 "Abra preguntas. Si alguien pregunta por una deuda, impuestos o su crédito en particular, sugiera hablar después con la organización o con una agencia de asesoría de crédito sin fines de lucro. No dé consejos individuales."))
S.append(("close", "Tu primer paso esta semana", "Elige tu día de revisión y ponlo en el calendario.",
 "Pida que cada quien escriba su día y hora en la Hoja 2 y lo ponga en su celular ahora. Agradezca. Si la organización tiene la guía completa, diga cómo pedirla. No venda nada durante el taller."))

WORKSHEETS = [
 ("Hoja 1 · Mi número semanal", "Nadie más va a ver esta hoja.", [
   ("A1 · Mi sueldo neto al mes", "$ __________   (cada semana: × 52 ÷ 12 · cada dos semanas: × 26 ÷ 12 · dos veces al mes: × 2)"),
   ("A2 · Mis gastos fijos", "Renta $____  Luz/agua/gas $____  Internet/celular $____  Carro y seguro $____  Mínimos de deudas $____  Envío a mi familia $____  Otros $____"),
   ("A3 · Total de gastos fijos", "$ __________"),
   ("B1 · Mis fondos (costo del año ÷ 12)", "__________ $____   __________ $____   __________ $____   Total $____"),
   ("B2 · Mis metas al mes", "Emergencia $____   Deuda extra $____   Otra $____   Total $____"),
   ("B3 · Bolsa del mes", "A1 − A3 − B1 − B2 = $ __________"),
   ("B4 · Mi número semanal", "Bolsa × 12 ÷ 52 = $ __________  (redondea hacia abajo)"),
  ], []),
 ("Hoja 2 · Mi rutina de 20 minutos", "Ponla en tu calendario como evento que se repite.", [
   ("Mi día y hora de revisión", "______________________"),
   ("0–5 · Mira", "Abro mis cuentas y anoto saldos"),
   ("5–10 · Anota", "Escribo cuánto gasté de mi número semanal"),
   ("10–15 · Revisa", "¿Salieron los fijos? ¿Se hicieron las transferencias? ¿Algún cargo que no reconozco?"),
   ("15–20 · Decide", "Un paso para la próxima semana: ____________________________"),
  ], ["Puse mi revisión en el calendario", "Programé la transferencia al ahorro el día de pago", "Busqué suscripciones que ya no uso", "Hice mi ajuste mensual (unos días antes del día de pago)"]),
]
