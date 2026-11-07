# "Temporada de impuestos 2027": a free Spanish guide for families filing their 2026 taxes (Jan - Apr 15, 2027),
# with a W-2 or with an ITIN. Machine-written: a fluent Spanish speaker reviews every word, a tax professional (an
# enrolled agent, CPA or VITA site coordinator) checks every figure, and a licensed immigration attorney or
# DOJ-accredited representative reads every section marked attorney=True before it is shared.
#
# Each section: id, title, body (Markdown), attorney (bool), check (facts to confirm against the source, in English).

TITLE = "Temporada de impuestos 2027: guía para familias"
SUBTITLE = "Tus impuestos de 2026, con W-2 o con ITIN, paso a paso y sin pagar de más"
YEAR = 2026
DEADLINE = "jueves 15 de abril de 2027"

INTRO = ("Esta guía es para familias que trabajan en Estados Unidos y van a declarar sus impuestos de 2026 entre enero y "
         "abril de 2027: con número de Seguro Social, con ITIN, o en una familia donde hay de los dos. Es información "
         "general, no asesoría fiscal ni legal. Las reglas cambian cada año: confirma cada número en irs.gov/es o con "
         "un preparador de confianza antes de declarar.")

ATTORNEY_NOTE = ("**Antes de declarar, si tienes preguntas sobre tu situación migratoria:** habla con un abogado de "
                 "inmigración con licencia o un representante acreditado por el Departamento de Justicia. Nunca con un "
                 "notario ni con un preparador que te prometa 'arreglar papeles'. Muchas organizaciones dan consultas "
                 "gratis o de bajo costo.")

SECTIONS = [
dict(id="calendario", title="El calendario: de enero al 15 de abril", attorney=False, body="""
| Cuándo | Qué pasa |
|---|---|
| Finales de enero | El IRS empieza a recibir declaraciones (la fecha exacta la anuncia en enero). |
| A más tardar el 1 de febrero de 2027 | Tu empleador te tiene que dar tu W-2, y quien te pagó como contratista, tu 1099-NEC. |
| Desde mediados de febrero | Llegan los reembolsos con el crédito por ingreso del trabajo (EITC) o el crédito adicional por hijos: por ley, el IRS no los puede mandar antes de mediados de febrero. |
| {deadline} | Último día para declarar y para **pagar** lo que debas. |

Si no te alcanza el tiempo, puedes pedir una extensión hasta octubre con el formulario 4868. Ojo: la extensión es para **declarar**, no para pagar. Si debes, paga lo que puedas antes del 15 de abril para que la multa y los intereses sean menores.
""".format(deadline=DEADLINE.capitalize()),
 check=["IRS opening day for the 2027 filing season (announced in January)",
        "W-2 and 1099-NEC due to recipients Feb 1, 2027 (Jan 31 falls on a Sunday)",
        "PATH Act: refunds claiming EITC/ACTC can't be issued before mid-February",
        "2027 filing deadline Thu Apr 15, 2027; Form 4868 extends filing to Oct 15, not payment"]),

dict(id="papeles", title="Los papeles que tienes que juntar", attorney=False, body="""
Haz una carpeta (de papel o en el celular) y ve metiendo esto en cuanto llegue:

- [ ] **Identificación** de cada persona en la declaración: tarjeta de Seguro Social o carta de tu ITIN.
- [ ] **W-2** de cada trabajo que tuviste en 2026.
- [ ] **1099** si trabajaste por tu cuenta, por apps o como contratista (1099-NEC, 1099-K), o si tu banco te pagó intereses (1099-INT).
- [ ] **Tus propios registros** de ingresos y gastos si trabajas por tu cuenta, aunque no te llegue ningún 1099.
- [ ] **1095-A** si tuviste seguro médico del Mercado.
- [ ] **Recibos de guardería** con el nombre, la dirección y el número de identificación del lugar o la persona.
- [ ] **El IP PIN** si el IRS te dio uno (llega por carta cada año, o lo sacas en línea).
- [ ] **Tu declaración del año pasado**, si la tienes.
- [ ] **Tu número de cuenta y de ruta** del banco, para que el reembolso llegue directo.
"""
 , check=["1099-K and 1099-NEC thresholds for 2026 under the 2025 law ($20,000 and 200 transactions; $2,000)",
          "Childcare credit requires the provider's name, address and TIN"]),

dict(id="quien", title="¿Tienes que declarar?", attorney=False, body="""
Casi siempre conviene declarar aunque no estés obligado, porque es la única forma de recibir el reembolso de lo que te retuvieron y los créditos por tus hijos.

Estás obligado a declarar si tu ingreso pasa cierto mínimo (para 2026, más o menos la deducción estándar: **$16,100** si eres soltero, **$32,200** si declaras en conjunto), o si **trabajaste por tu cuenta y ganaste $400 o más**, aunque sea en efectivo.

El ingreso cuenta aunque te paguen en efectivo y aunque no te llegue ningún formulario.
""", check=["2026 standard deduction $16,100 single / $32,200 MFJ / $24,150 HoH (Rev. Proc. 2025-32)",
            "Self-employment filing threshold $400 net earnings"]),

dict(id="itin", title="El ITIN: qué es, quién lo necesita y cuándo vence", attorney=True, body="""
El **ITIN** es un número de nueve dígitos que da el IRS a quien tiene que declarar impuestos y no puede tener número de Seguro Social. **Es solo para impuestos:** no te da permiso para trabajar ni cambia tu situación migratoria.

- **Quién lo necesita:** tú, tu cónyuge o tus dependientes que van en la declaración y no tienen ni pueden tener Seguro Social.
- **Cómo se pide:** con el formulario **W-7**, junto con tu declaración, en persona en un centro del IRS con cita, con un **Agente Certificador de Aceptación** (CAA), o por correo con tus documentos originales o copias certificadas por quien los emitió.
- **Cuándo vence:** si no lo usaste en una declaración federal en **tres años seguidos**, vence el 31 de diciembre del tercer año. Si tu ITIN venció, renuévalo con el W-7 **antes** de declarar o junto con tu declaración, o tu reembolso se puede atrasar.
- **Si ya tienes Seguro Social:** avísale al IRS para que junte tu historial con tu número nuevo y deja de usar el ITIN.

""" + ATTORNEY_NOTE,
 check=["ITIN is for federal tax purposes only; doesn't authorize work or change immigration status (IRS)",
        "W-7 filing options: with return by mail, IRS Taxpayer Assistance Center by appointment, Certifying Acceptance Agent",
        "ITINs not used on a federal return for 3 consecutive tax years expire Dec 31 of the third year",
        "ATTORNEY REVIEW"]),

dict(id="datos", title="Tus datos y el IRS: lo que debes saber antes de declarar", attorney=True, body="""
Durante muchos años, el IRS guardó con mucha privacidad los datos de quienes declaran con ITIN. En 2025 hubo cambios y casos en la corte sobre cuándo el IRS puede compartir algunos datos con otras agencias del gobierno, y las reglas pueden seguir cambiando.

No te podemos decir qué te conviene en tu caso. Lo que sí te decimos:

- **Antes de declarar, pregúntale a un abogado de inmigración con licencia o a un representante acreditado** cómo te puede afectar a ti y a tu familia, con las reglas de ese momento.
- Declarar puede ser importante para tu historial: muchas personas lo usan como prueba de que han pagado impuestos y de cuánto tiempo han vivido aquí. Eso también se lo puedes preguntar a tu abogado.
- No le hagas caso a rumores en redes sociales ni a quien te cobre por "proteger tus datos".

""" + ATTORNEY_NOTE,
 check=["ATTORNEY REVIEW: current status of IRS-DHS/ICE data sharing (2025 agreement and litigation) the week this guide is shared; update or remove this section accordingly",
        "Keep the wording neutral: no prediction, no promise of confidentiality"]),

dict(id="estado-civil", title="Cómo declarar: soltero, en conjunto o cabeza de familia", attorney=False, body="""
Tu **estado civil para declarar** cambia cuánto pagas:

- **Casados en conjunto:** casi siempre sale mejor que por separado. Si tu cónyuge no tiene Seguro Social ni puede tenerlo, puede necesitar un ITIN para declarar juntos.
- **Cabeza de familia:** si no estás casado (o vives separado de tu cónyuge en ciertos casos), pagaste más de la mitad de los gastos de la casa y vive contigo un hijo u otro dependiente que califica. Tiene una deducción estándar más alta que soltero (**$24,150** para 2026).
- **Soltero:** si no aplica ninguno de los anteriores.

Si tu cónyuge vive en otro país, las reglas son distintas: pregúntale a un preparador.
""", check=["2026 HoH standard deduction $24,150", "Nonresident alien spouse rules (election to treat as resident; ITIN needed)"]),

dict(id="creditos", title="Los créditos por tus hijos y dependientes", attorney=True, body="""
Aquí es donde más cambia el resultado, y donde importa **qué número tiene cada persona**:

| Crédito (2026) | Cuánto | Qué número piden |
|---|---|---|
| **Crédito tributario por hijos** | Hasta **$2,200** por hijo menor de 17; hasta **$1,700** te lo pueden pagar aunque no debas impuestos | El hijo necesita número de Seguro Social válido para trabajar. Además, por la ley de 2025, **al menos uno de los padres** que declaran (tú o tu cónyuge) tiene que tener Seguro Social |
| **Crédito por otros dependientes** | Hasta **$500** por dependiente | El dependiente puede tener ITIN |
| **Crédito por ingreso del trabajo (EITC)** | Puede ser de varios miles con hijos | Tú, tu cónyuge y los hijos que cuentes necesitan Seguro Social válido para trabajar. **Con ITIN no se puede reclamar** |
| **Crédito por cuidado de niños** | Un porcentaje de lo que pagaste de guardería para poder trabajar | Pide los datos del cuidador |

Las **familias mixtas** (unos con Seguro Social y otros con ITIN) pueden tener derecho a algunos créditos y no a otros. Un preparador con experiencia en ITIN o un sitio VITA te ayuda a no dejar dinero en la mesa, y a no pedir lo que no te toca.

""" + ATTORNEY_NOTE,
 check=["2026 Child Tax Credit $2,200 per child, refundable ACTC up to $1,700 (inflation-adjusted)",
        "2025 law (OBBBA): CTC requires the child's SSN and an SSN for the taxpayer or, if joint, at least one spouse; confirm IRS guidance for tax year 2026",
        "Credit for other dependents $500; dependent may have an ITIN",
        "EITC requires valid SSNs for taxpayer, spouse and qualifying children",
        "ATTORNEY REVIEW"]),

dict(id="nuevas", title="Lo nuevo: propinas, horas extra y la deducción para mayores", attorney=False, body="""
La ley de 2025 creó deducciones nuevas para los años 2025 a 2028. Pueden bajar lo que pagas, pero tienen reglas:

- **Propinas:** se pueden deducir hasta cierto límite si trabajas en una ocupación donde se acostumbra recibir propinas.
- **Horas extra:** se puede deducir la parte "extra" del pago de horas extra (la mitad del tiempo y medio), hasta cierto límite.
- **Personas de 65 años o más:** una deducción adicional.

Para las de propinas y horas extra, se necesita **número de Seguro Social válido para trabajar**. Pregúntale a tu preparador si te tocan y qué papeles necesitas (muchos empleadores las reportan en el W-2).
""", check=["OBBBA 2025: 'no tax on tips' (up to $25,000) and overtime premium (up to $12,500 / $25,000 MFJ) deductions for 2025-2028, phase-outs, SSN requirement",
            "Senior deduction $6,000 per person 65+ (2025-2028), phase-out",
            "How 2026 W-2s report qualified tips and overtime"]),

dict(id="gratis", title="Dónde declarar gratis o barato", attorney=False, body="""
- **VITA:** voluntarios certificados por el IRS te hacen los impuestos **gratis** si ganas por debajo de cierto límite. Muchos sitios atienden en español y ayudan con ITIN (algunos son también Agentes Certificadores). Busca el más cercano en irs.gov/es o llamando al 1-800-906-9887.
- **IRS Free File:** programas gratis en línea si tu ingreso está por debajo del límite del año.
- **Un preparador pagado:** está bien, pero pregunta el precio **antes**, y revisa que tenga **PTIN** (número de preparador) y que **firme** tu declaración.

Más en nuestra guía [Dónde hacer tus impuestos](/blog/donde-hacer-tus-impuestos/).
""", check=["VITA income limit for the 2027 season (about $69,000 for 2025 returns; confirm)", "VITA locator phone 1-800-906-9887",
            "Paid preparers must have a PTIN and sign the return"]),

dict(id="trampas", title="Las trampas de la temporada", attorney=False, body="""
- **El preparador 'fantasma':** no firma tu declaración, te cobra un porcentaje de tu reembolso o te pide que el reembolso llegue a **su** cuenta. Vete.
- **Dependientes inventados o 'prestados':** si alguien te ofrece poner niños que no son tuyos para subir tu reembolso, es fraude, y la responsabilidad es **tuya**, no del preparador.
- **"Te saco el ITIN y los papeles":** nadie que prepare impuestos puede arreglar tu situación migratoria.
- **El IRS no te escribe primero por mensaje de texto, WhatsApp ni redes sociales** para pedirte datos o pagos. Normalmente te manda una carta.
- **Anticipos del reembolso:** si te ofrecen tu reembolso "hoy mismo", pregunta cuánto cuesta. Algunos son gratis; otros cobran cargos altos.
""", check=["IRS warns about ghost preparers who don't sign returns", "IRS initiates most contact by mail; doesn't initiate contact by text/social media for personal info",
            "Refund advance products: some free, some with fees"]),

dict(id="si-debes", title="Si debes, o si te llega una carta", attorney=False, body="""
- **Si debes y no te alcanza:** declara a tiempo de todas formas (la multa por no declarar es mucho más alta que la de no pagar) y pide un **plan de pagos** en irs.gov.
- **Si te llega una carta del IRS:** no te asustes y no la ignores. Lee qué pide y para cuándo. Confirma que es real buscando el número de la carta en irs.gov o llamando al número de irs.gov, no al de la carta si dudas. Un sitio VITA o la **Oficina del Defensor del Contribuyente** (Taxpayer Advocate Service) te puede ayudar gratis.
""", check=["Failure-to-file penalty is generally higher than failure-to-pay (5% vs 0.5% per month)", "IRS online payment plans", "Taxpayer Advocate Service is free"]),

dict(id="reembolso", title="Cuando llegue tu reembolso", attorney=False, body="""
Tu reembolso no es un regalo: es tu propio dinero que el gobierno te guardó sin intereses. Antes de que llegue, decide a dónde va:

1. **Lo que debes con intereses altos** (tarjetas, préstamos de día de pago).
2. **Tu fondo de emergencia** (la primera meta: $1,000).
3. **Un gusto con número** (sí, también cuenta).

Y si cada año te llega un reembolso muy grande, quizás te están reteniendo de más: revisa tu **W-4** con tu empleador, y ese dinero te llega en cada cheque. Nuestra [calculadora de sueldo](/calculadora-de-sueldo/) te da una idea.
""", check=["No numeric claims beyond the $1,000 emergency-fund example"]),
]

CHECKLIST_1PAGE = [
    "Juntar W-2, 1099 y mis registros de ingresos",
    "Revisar que el ITIN de cada persona no esté vencido (o renovarlo con el W-7)",
    "Si tengo dudas migratorias: consulta con abogado o representante acreditado ANTES de declarar",
    "Decidir el estado civil para declarar",
    "Revisar qué créditos le tocan a cada hijo según su número",
    "Buscar VITA o Free File; si pago, preguntar el precio y el PTIN",
    "Poner mi cuenta para depósito directo",
    "Declarar antes del 15 de abril de 2027 (y pagar lo que deba)",
    "Decidir a dónde va el reembolso antes de que llegue",
]
