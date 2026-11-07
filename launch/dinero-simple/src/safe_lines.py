"""Standard "consult a lawyer, here's free help" lines for Dinero Simple (Spanish; REVISIÓN NATIVA + ATTORNEY REVIEW,
once). The attorney approves these lines one time in the review packet. Any piece that needs to send someone to a
lawyer uses one of them word for word, instead of explaining an immigration rule itself.

Official sources behind the links (check they still load before each posting batch):
  https://www.justice.gov/eoir/list-pro-bono-legal-service-providers      free legal service providers (EOIR)
  https://www.justice.gov/eoir/recognized-organizations-and-accredited-representatives-roster-state-and-city
  https://www.uscis.gov/es/evite-las-estafas-de-inmigracion                USCIS, in Spanish
  https://www.irs.gov/es/individuals/individual-taxpayer-identification-number   the ITIN, in Spanish
  https://irs.treasury.gov/freetaxprep/                                   free VITA tax help
"""

# Where to find free or low-cost legal help (short enough for a caption).
AYUDA_LEGAL = ("Si tu pregunta es sobre tu situación migratoria, no la resuelve un video ni un notario: consulta a un "
               "abogado de inmigración con licencia o a un representante acreditado por el Departamento de Justicia. "
               "Ayuda gratis o de bajo costo: justice.gov/eoir (lista de proveedores gratuitos) y "
               "uscis.gov/es/evite-las-estafas-de-inmigracion.")

# For worries about what happens to your data when you file taxes or open an account. Replaces any line that
# tried to explain data sharing between agencies: those rules change and are in court.
DATOS = ("Si te preocupa qué pasa con tus datos al declarar o al abrir una cuenta, esa decisión depende de tu caso: "
         "pregúntale primero a un abogado de inmigración con licencia o a un representante acreditado. Hay consultas "
         "gratis en justice.gov/eoir (lista de proveedores gratuitos).")

# For rights that depend on the state (work injuries, wages, tenants).
DERECHOS_ESTADO = ("Tus derechos aquí dependen de tu estado: pregunta gratis en la oficina de tu estado o en una "
                   "organización de ayuda legal, y si tu duda es migratoria, consulta a un abogado de inmigración con "
                   "licencia o a un representante acreditado (lista gratis en justice.gov/eoir).")

STANDARD = {"AYUDA_LEGAL": AYUDA_LEGAL, "DATOS": DATOS, "DERECHOS_ESTADO": DERECHOS_ESTADO}
