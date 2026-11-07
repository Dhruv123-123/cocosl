# "Alerta de estafa": scam alerts aimed at immigrants, in the Scam Decoded style (PR #9): a calm hook that opens with
# a number, the fake message shown as a made-up screenshot with numbered callouts on the red flags, what to do, and
# where to report. 7 posts on Saturdays, Mar 6 - Apr 17, 2027. They add to, and don't repeat, the January scam series
# (estafas/: notario, USCIS letter, visa lottery, bonds, remittances, mules).
#
# Rules (Scam Decoded's, applied in Spanish): every example message, name, number and link is made up and looks fake
# on close reading ("ejemplo" watermark); no real company or agency is accused; no panic ("¡te van a deportar!");
# nothing reads like immigration legal advice: people go to a licensed immigration attorney or a DOJ-accredited
# representative, never a notario. Reports go to the FTC in Spanish (ReporteFraude.ftc.gov). Every piece carries
# ATTORNEY REVIEW. Segment tuples: (heading, on_screen_text, narration, scene).
from month1_shorts_a import CTA

PILLAR = "apps y herramientas de dinero, comparadas sin rodeos"
REPORT = "Repórtalo gratis en ReporteFraude.ftc.gov (en español)."
LAW = "Para cualquier trámite de inmigración: un abogado con licencia o un representante acreditado por el DOJ (lista en justice.gov/eoir). Nunca un notario."
NOTE = "Los mensajes, nombres y números del ejemplo son inventados. Información general, no es asesoría legal."
TAGS = ["alertadeestafa", "estafas", "inmigrantes", "dinerosimple", "fraude"]
ATTORNEY = "ATTORNEY REVIEW: a licensed immigration attorney or DOJ-accredited representative has read this piece the week it posts (immigration scam)"
SCREEN = "made-up screenshot with an 'EJEMPLO' watermark and numbered red callouts: "

ITEMS = [
dict(
    key="a-llamada-inmigracion", format="short", pillar=PILLAR,
    angle="Fake immigration-agent call: the caller says there's a problem with your case or a deportation order and you must pay a 'fine' today by gift card, wire or app. No US immigration agency collects payment by phone or gift card.",
    title="La llamada de 'Inmigración' que pide un pago",
    hook="Tres cosas delatan la llamada falsa de 'Inmigración'. La tercera es la forma de pago.",
    thumbnail_text="Llamada falsa de Inmigración",
    segments=[
        ("Gancho", "3 señales de la llamada falsa", "Tres cosas delatan la llamada falsa de 'Inmigración'. La tercera es la forma de pago.", SCREEN + "a phone call screen showing 'Inmigración EE.UU.'"),
        ("Señal 1", "1. Te asustan: 'hay una orden contra usted'", "Uno: te asustan. Dicen que hay un problema con tu caso o una orden contra ti.", SCREEN + "callout 1 on the caller's script"),
        ("Señal 2", "2. Prisa: 'tiene que pagar hoy'", "Dos: prisa. Tienes que pagar hoy o 'vienen por ti'.", SCREEN + "callout 2 on a clock"),
        ("Señal 3", "3. Te piden tarjetas de regalo, giros o apps", "Tres: te piden pagar con tarjetas de regalo, giros, cripto o una app. Ninguna agencia de inmigración cobra así.", SCREEN + "callout 3 on gift cards"),
        ("Qué hacer", "Cuelga. No des datos ni dinero.", "Qué hacer: cuelga. No des tu número de caso, ni datos, ni dinero.", "a hand ending a call"),
        ("Verifica", "Consulta tu caso solo con tu abogado", "Si te preocupa tu caso, pregúntale a tu abogado o representante acreditado. Nunca al número que te llamó.", "a lawyer's office, generic"),
    ],
    caption="Llamada falsa de 'Inmigración': 3 señales.\n1. Te asustan: 'hay una orden contra usted'.\n2. Prisa: 'pague hoy'.\n3. Piden tarjetas de regalo, giros, cripto o una app.\nNinguna agencia de inmigración cobra por teléfono ni con tarjetas de regalo. Cuelga y consulta tu caso con tu abogado.\n\n" + REPORT + "\n" + LAW + "\n" + NOTE + "\n\n" + CTA,
    hashtags=TAGS,
    description="Alerta: la llamada falsa de Inmigración que pide un pago.",
    sources=["https://www.uscis.gov/es/evite-estafas", "https://consumidor.ftc.gov/"],
    claims=[ATTORNEY, "USCIS and other immigration agencies don't ask for payment by phone, gift card, wire or payment app (USCIS Avoid Scams)",
            "Scammers spoof caller ID to show government names (FTC)"],
),
dict(
    key="a-formulario-gratis", format="short", pillar=PILLAR,
    angle="Paid-form scam: websites and 'gestores' sell USCIS forms or charge to 'download' them. USCIS forms are free at uscis.gov; filing fees are paid to USCIS as its instructions say, never to a stranger's personal account.",
    title="Te venden un formulario que es gratis",
    hook="Este formulario de inmigración cuesta cero dólares. Hay quien lo vende en cien.",
    thumbnail_text="El formulario es gratis",
    segments=[
        ("Gancho", "El formulario cuesta $0", "Este formulario de inmigración cuesta cero dólares. Hay quien lo vende en cien.", SCREEN + "a fake website selling a form for $99"),
        ("Señal 1", "1. Una página que no termina en .gov", "Uno: la página no termina en punto gov, aunque tenga una bandera y un águila.", SCREEN + "callout 1 on the web address"),
        ("Señal 2", "2. Te cobran por 'descargarlo'", "Dos: te cobran por descargar el formulario. En la página oficial es gratis.", SCREEN + "callout 2 on a 'pay to download' button"),
        ("Señal 3", "3. El pago va a una cuenta personal", "Tres: te piden pagar a una cuenta personal o por una app. Las cuotas oficiales se pagan como dicen las instrucciones de USCIS.", SCREEN + "callout 3 on a payment-app handle"),
        ("Qué hacer", "Formularios gratis solo en uscis.gov/es", "Los formularios son gratis en uscis punto gov. Si no sabes cuál necesitas, pregúntale a un abogado o representante acreditado.", "a laptop showing a generic .gov address"),
        ("Cierre", "Mándaselo a quien está haciendo un trámite", "Mándaselo a quien esté haciendo un trámite.", "two phones sharing a video"),
    ],
    caption="Los formularios de USCIS son gratis en uscis.gov/es.\nSeñales de la estafa:\n1. La página no termina en .gov.\n2. Te cobran por 'descargar' el formulario.\n3. El pago va a una cuenta personal o una app.\nLas cuotas oficiales se pagan como dicen las instrucciones de USCIS.\n\n" + REPORT + "\n" + LAW + "\n" + NOTE + "\n\n" + CTA,
    hashtags=TAGS,
    description="Alerta: páginas que venden formularios de inmigración que son gratis.",
    sources=["https://www.uscis.gov/es/evite-estafas", "https://www.uscis.gov/es/formularios"],
    claims=[ATTORNEY, "USCIS forms are free to download from uscis.gov (USCIS)",
            "USCIS filing fees are paid as each form's instructions say (online, or by check/card to the U.S. Department of Homeland Security); check current fee payment rules"],
),
dict(
    key="a-trabajo-con-visa", format="short", pillar=PILLAR,
    angle="Job-with-visa scam: a recruiter on Facebook or WhatsApp promises a US job with an H-2A or H-2B work visa for a 'recruitment fee'. Under US rules, employers and their recruiters can't charge H-2A/H-2B workers recruitment fees.",
    title="Trabajo con visa: si te cobran, es estafa",
    hook="Una oferta de trabajo con visa que te pide dinero tiene un problema: la ley no deja cobrarte.",
    thumbnail_text="¿Trabajo con visa? Ojo",
    segments=[
        ("Gancho", "La ley no deja cobrarte", "Una oferta de trabajo con visa que te pide dinero tiene un problema: la ley no deja cobrarte.", SCREEN + "a WhatsApp offer: 'Trabajo en EE.UU. con visa, cupo limitado'"),
        ("Señal 1", "1. 'Cupo limitado, paga hoy'", "Uno: cupo limitado, aparta tu lugar hoy.", SCREEN + "callout 1 on 'cupo limitado'"),
        ("Señal 2", "2. Una 'cuota de reclutamiento'", "Dos: te piden una cuota de reclutamiento. En las visas H-2A y H-2B, el patrón y sus reclutadores no pueden cobrártela.", SCREEN + "callout 2 on a fee amount"),
        ("Señal 3", "3. Solo por WhatsApp, sin empresa que verificar", "Tres: todo es por WhatsApp y no hay una empresa que puedas verificar.", SCREEN + "callout 3 on a profile with no company"),
        ("Qué hacer", "No pagues. Busca la oferta en seasonaljobs.dol.gov", "No pagues. Las ofertas reales de estas visas se publican en seasonaljobs punto dol punto gov.", "a laptop with a generic job board"),
        ("Cierre", "Mándaselo a tu familia allá", "Mándaselo a tu familia allá. A ellos es a quienes les llega.", "a phone sending a video abroad"),
    ],
    caption="Trabajo en EE. UU. con visa H-2A o H-2B: si te cobran una 'cuota de reclutamiento', es estafa o es ilegal.\nSeñales:\n1. 'Cupo limitado, paga hoy'.\n2. Te piden una cuota de reclutamiento.\n3. Todo por WhatsApp, sin empresa que verificar.\nLas ofertas reales se publican en seasonaljobs.dol.gov.\n\n" + REPORT + "\n" + LAW + "\n" + NOTE + "\n\n" + CTA,
    hashtags=TAGS,
    description="Alerta: ofertas de trabajo con visa que te cobran.",
    sources=["https://www.dol.gov/agencies/whd/immigration", "https://seasonaljobs.dol.gov/"],
    claims=[ATTORNEY, "H-2A (20 CFR 655.135(j)) and H-2B (20 CFR 655.20(o)) prohibit employers and their agents/recruiters from charging workers recruitment fees",
            "H-2A and H-2B job orders are posted at seasonaljobs.dol.gov (DOL)"],
),
dict(
    key="a-abogado-falso", format="short", pillar=PILLAR,
    angle="Fake lawyer online: a Facebook or WhatsApp 'abogado' or 'consultor' promises a fast work permit or papers. How to check: a lawyer is listed with their state bar; an accredited representative works at a DOJ-recognized organization (EOIR roster).",
    title="El 'abogado' de Facebook que promete papeles rápido",
    hook="En dos minutos puedes saber si ese 'abogado' de Facebook es de verdad.",
    thumbnail_text="¿Abogado de verdad?",
    segments=[
        ("Gancho", "2 minutos para verificar", "En dos minutos puedes saber si ese 'abogado' de Facebook es de verdad.", SCREEN + "a social media ad: 'Permiso de trabajo en 30 días, garantizado'"),
        ("Señal 1", "1. 'Garantizado' y 'rápido'", "Uno: promete resultados garantizados y rápidos. Nadie puede garantizar lo que decide el gobierno.", SCREEN + "callout 1 on 'garantizado'"),
        ("Señal 2", "2. Cobra en efectivo y sin contrato", "Dos: cobra en efectivo, sin contrato por escrito y sin recibo.", SCREEN + "callout 2 on 'solo efectivo'"),
        ("Verifica 1", "Abogado: búscalo en el colegio de abogados", "Para verificar: un abogado aparece en la lista del colegio de abogados de su estado.", "a laptop with a generic bar directory"),
        ("Verifica 2", "Representante: lista del DOJ (EOIR)", "Y un representante acreditado aparece en la lista del Departamento de Justicia, en justice punto gov barra eoir.", "a laptop with a generic government list"),
        ("Cierre", "Si no aparece, no le pagues", "Si no aparece en ninguna, no le des dinero ni documentos.", "a hand holding documents back"),
    ],
    caption="¿Ese 'abogado' de redes es de verdad? Verifícalo:\n• Abogado: en la lista del colegio de abogados (state bar) de su estado.\n• Representante acreditado: en la lista del DOJ, justice.gov/eoir.\nSeñales de estafa: 'garantizado', 'rápido', solo efectivo, sin contrato ni recibo.\nSi no aparece, no le des dinero ni documentos originales.\n\n" + REPORT + "\n" + LAW + "\n" + NOTE + "\n\n" + CTA,
    hashtags=TAGS,
    description="Alerta: cómo verificar a un abogado o representante de inmigración.",
    sources=["https://www.justice.gov/eoir/recognition-and-accreditation-roster-reports", "https://www.uscis.gov/es/evite-estafas"],
    claims=[ATTORNEY, "Accredited representatives and recognized organizations are listed in EOIR's roster (justice.gov/eoir)",
            "Attorneys can be checked with the state bar where they're licensed; EOIR also lists disciplined practitioners"],
),
dict(
    key="a-pagina-falsa", format="short", pillar=PILLAR,
    angle="Look-alike government websites that charge to 'register' you for a program, a lottery or a status renewal. Official US government sites end in .gov; check the address before paying anything.",
    title="La página que se parece al gobierno, pero no es",
    hook="Un detalle de cuatro letras te dice si una página es del gobierno: punto gov.",
    thumbnail_text="¿Termina en .gov?",
    segments=[
        ("Gancho", "4 letras: .gov", "Un detalle de cuatro letras te dice si una página es del gobierno: punto gov.", SCREEN + "a look-alike site with a flag and a fake address"),
        ("Señal 1", "1. La dirección termina en .com, .org o .us", "Uno: la dirección termina en punto com, punto org o algo parecido.", SCREEN + "callout 1 on the address bar"),
        ("Señal 2", "2. Te cobran por 'registrarte' o 'renovar'", "Dos: te cobran por registrarte en un programa o renovar un trámite.", SCREEN + "callout 2 on a payment form"),
        ("Señal 3", "3. Llegaste por un anuncio o un mensaje", "Tres: llegaste por un anuncio o un mensaje, no escribiendo tú la dirección.", SCREEN + "callout 3 on a 'Patrocinado' label"),
        ("Qué hacer", "Escribe tú la dirección: uscis.gov/es", "Escribe tú la dirección oficial. Para inmigración: uscis punto gov barra es.", "a hand typing an address"),
        ("Cierre", "Guarda este video", "Guarda este video para la próxima vez que veas un anuncio así.", "a bookmark icon"),
    ],
    caption="¿Es del gobierno de verdad? Las páginas oficiales de EE. UU. terminan en .gov.\nSeñales de una página falsa:\n1. Termina en .com, .org u otra.\n2. Te cobra por 'registrarte' o 'renovar'.\n3. Llegaste por un anuncio o un mensaje.\nEscribe tú la dirección: uscis.gov/es.\n\n" + REPORT + "\n" + LAW + "\n" + NOTE + "\n\n" + CTA,
    hashtags=TAGS,
    description="Alerta: páginas que imitan al gobierno y cobran por trámites.",
    sources=["https://www.uscis.gov/es/evite-estafas", "https://consumidor.ftc.gov/"],
    claims=[ATTORNEY, "Official US federal government websites use .gov domains (GSA/CISA)",
            "Check whether the trámite named in any example is currently open; don't name a program whose status is in flux"],
),
dict(
    key="a-prestamo-sin-ss", format="short", pillar=PILLAR,
    angle="Advance-fee loan scam aimed at people without an SSN: 'guaranteed loan or card, no SSN, no credit check', pay a fee first. Legitimate lenders don't guarantee approval or ask for a fee before the loan. Ties to the Crédito sin Seguro Social series.",
    title="'Préstamo garantizado sin Seguro Social': la trampa",
    hook="Si un préstamo te pide pagar antes de dártelo, ya sabes cómo termina.",
    thumbnail_text="Préstamo garantizado = trampa",
    segments=[
        ("Gancho", "Pagar antes del préstamo = estafa", "Si un préstamo te pide pagar antes de dártelo, ya sabes cómo termina.", SCREEN + "a text: 'Préstamo garantizado sin Seguro Social, solo pague el seguro'"),
        ("Señal 1", "1. 'Garantizado, sin revisar crédito'", "Uno: garantizado, sin revisar tu crédito. Un prestamista real siempre revisa algo.", SCREEN + "callout 1 on 'garantizado'"),
        ("Señal 2", "2. 'Paga primero el seguro o la cuota'", "Dos: te piden pagar primero un seguro, una cuota o un 'depósito'.", SCREEN + "callout 2 on the fee"),
        ("Señal 3", "3. Pago con tarjeta de regalo o app", "Tres: el pago es con tarjeta de regalo o por una app. Y después piden otro.", SCREEN + "callout 3 on gift cards"),
        ("Qué hacer", "Cooperativas y prestamistas comunitarios", "Si necesitas crédito sin Seguro Social, empieza por una cooperativa de crédito o un prestamista comunitario.", "a credit union front, no logo"),
        ("Cierre", "Serie 'Crédito sin Seguro Social'", "Y mira la serie Crédito sin Seguro Social en el perfil.", "a playlist on a phone"),
    ],
    caption="'Préstamo garantizado sin Seguro Social, solo pague primero': es estafa.\nSeñales:\n1. 'Garantizado', sin revisar crédito.\n2. Te piden pagar antes un seguro, una cuota o un depósito.\n3. Pago con tarjeta de regalo o app.\nLos prestamistas legítimos no cobran por adelantado para 'garantizar' un préstamo.\n\n" + REPORT + "\nInformación general, no es asesoría financiera. Los mensajes del ejemplo son inventados.\n\n" + CTA,
    hashtags=TAGS,
    description="Alerta: préstamos 'garantizados' sin Seguro Social que cobran antes.",
    sources=["https://consumidor.ftc.gov/", "https://www.consumerfinance.gov/es/"],
    claims=["Advance-fee loans: legitimate lenders don't guarantee a loan or ask for a fee up front to get it (FTC)",
            "Some credit unions and community lenders (CDFIs) lend to ITIN holders"],
),
dict(
    key="ac-senales-inmigracion", format="carousel", pillar=PILLAR,
    angle="Save-and-send carousel: 7 signs a trámite offer is a scam (guaranteed result, cash only, no contract, keeps your originals, a site not ending in .gov, a 'fine' by phone, asks you to lie on a form) and the two places to check help (state bar, EOIR roster).",
    title="7 señales de una estafa de inmigración",
    hook="Guárdala y mándasela a quien esté haciendo un trámite.",
    thumbnail_text="7 señales de estafa",
    segments=[
        ("Portada", "7 señales de estafa de inmigración", "Guárdala y mándasela a quien esté haciendo un trámite.", "a checklist with seven red flags"),
        ("1-2", "1. 'Garantizado' · 2. Solo efectivo", "Uno: te garantizan el resultado. Dos: solo aceptan efectivo.", "two red flags"),
        ("3-4", "3. Sin contrato ni recibo · 4. Se quedan tus originales", "Tres: no hay contrato ni recibo. Cuatro: se quedan con tus documentos originales.", "two red flags"),
        ("5", "5. La página no termina en .gov", "Cinco: la página no termina en punto gov.", "an address bar with a red circle"),
        ("6", "6. Una 'multa' por teléfono", "Seis: te llaman para cobrarte una multa.", "a phone with a red flag"),
        ("7", "7. Te piden mentir en un formulario", "Siete: te piden mentir o firmar en blanco. Eso te puede perjudicar a ti.", "a blank form with a red flag"),
        ("Verifica", "Colegio de abogados · lista del DOJ (EOIR)", "Verifica a un abogado en el colegio de abogados de su estado, y a un representante en la lista del DOJ.", "two generic directories"),
        ("Cierre", "Nunca un notario", "Y recuerda: en Estados Unidos, un notario no es abogado.", "a 'no' sign over a notario storefront"),
    ],
    caption="7 señales de una estafa de inmigración:\n1. Te garantizan el resultado.\n2. Solo efectivo.\n3. Sin contrato ni recibo.\n4. Se quedan con tus documentos originales.\n5. La página no termina en .gov.\n6. Una 'multa' que te cobran por teléfono.\n7. Te piden mentir o firmar en blanco.\nVerifica: colegio de abogados de tu estado (abogados) y justice.gov/eoir (representantes acreditados).\n\n" + REPORT + "\n" + LAW + "\n" + NOTE + "\n\n" + CTA,
    hashtags=TAGS,
    description="7 señales de una estafa de inmigración, para guardar y mandar.",
    sources=["https://www.uscis.gov/es/evite-estafas", "https://www.justice.gov/eoir/recognition-and-accreditation-roster-reports"],
    claims=[ATTORNEY, "Signs match USCIS's Avoid Scams guidance (guarantees, keeping originals, false statements, payment demands)"],
),
]
