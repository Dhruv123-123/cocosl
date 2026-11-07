"""El Registro de Envíos: the remittance tracker workbook (Google Sheets / Excel / Numbers), in Spanish.

Tabs: Empieza, Comparar, Envíos, Meses, Servicios. Yellow cells are inputs; everything else is a formula. Comes with
a few made-up example rows marked "(ejemplo)". Needs native review like every Dinero Simple file.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from dinero_simple import BRAND, MESES

ROWS = 300
INK, CREAM = BRAND.ink[1:], BRAND.cream[1:]
YELLOW = "FFF4C2"
EV = "'Envíos'"  # quoted: the sheet name has an accent
SERVICIOS = ["Servicio A (ejemplo)", "Servicio B (ejemplo)", "App del banco (ejemplo)"]
PAGOS = ["Cuenta de banco", "Tarjeta de débito", "Tarjeta de crédito", "Efectivo", "Giro o cheque de caja"]
EXAMPLES = [(date(2027, 1, 10), "Mamá (ejemplo)", SERVICIOS[0], 300, 3.99, 17.55, 18.00, "Cuenta de banco", "A1B2C3"),
            (date(2027, 1, 24), "Mamá (ejemplo)", SERVICIOS[1], 200, 0, 17.20, 18.00, "Tarjeta de débito", "X9Y8"),
            (date(2027, 2, 9), "Hermano (ejemplo)", SERVICIOS[0], 150, 3.99, 17.60, 17.90, "Efectivo", "Q5R6")]


def build(path: Path) -> Path:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = Workbook()
    head_fill, head_font = PatternFill("solid", fgColor=INK), Font(bold=True, color="FFFFFF")
    inp = PatternFill("solid", fgColor=YELLOW)
    tot = PatternFill("solid", fgColor="FDEEE8")
    money, rate, pct = '"$"#,##0.00', "#,##0.00", "0.0%"

    def header(ws, row, labels, widths):
        for c, lab in enumerate(labels, 1):
            cell = ws.cell(row, c, lab)
            cell.fill, cell.font = head_fill, head_font
            cell.alignment = Alignment(vertical="center", wrap_text=True)
        ws.row_dimensions[row].height = 32
        for c, w in enumerate(widths, 1):
            ws.column_dimensions[chr(64 + c)].width = w
        ws.freeze_panes = ws.cell(row + 1, 1)

    def title(ws, text, sub):
        ws["A1"], ws["A2"] = text, sub
        ws["A1"].font = Font(bold=True, size=16, color=INK)
        ws["A2"].font = Font(italic=True, color="5D6470")

    # Empieza
    st = wb.active
    st.title = "Empieza"
    title(st, "El Registro de Envíos", "Dinero Simple · contenido educativo, no es asesoría financiera, fiscal ni legal")
    lines = ["Cómo usarlo",
             "1. Antes de enviar, llena la pestaña Comparar con dos o tres cotizaciones para el mismo monto.",
             "2. Después de enviar, anota el envío en la pestaña Envíos. Las celdas amarillas son las tuyas.",
             "3. Meses y Servicios se llenan solos: cuánto enviaste, cuánto pagaste y cuánto llegó.",
             "4. Borra las filas que dicen (ejemplo) y escribe tus servicios en la pestaña Servicios.",
             "",
             "Lo que importa es cuánto llega, no solo la comisión. Si anotas el tipo de cambio de referencia del día,",
             "la hoja calcula cuánto te costó el cambio además de la comisión.",
             "",
             "Desde 2026 hay un impuesto federal del 1% en envíos pagados en efectivo, giro postal o cheque de caja.",
             "La hoja lo estima si eliges esa forma de pago; verifica el monto real en tu recibo.",
             "",
             "Para Google Sheets: sube el archivo a Google Drive, ábrelo y elige Archivo > Guardar como Hojas de cálculo de Google.",
             "Hecho por Dinero Simple con ayuda de herramientas de IA para el borrador y el diseño; revisado por una persona."]
    for i, t in enumerate(lines, 4):
        st.cell(i, 1, t).font = Font(bold=(i == 4), size=11)
    st.column_dimensions["A"].width = 110

    # Servicios (names are inputs; totals are formulas over Envíos)
    sv = wb.create_sheet("Servicios")
    title(sv, "Servicios", "Escribe en amarillo los servicios que usas; los totales salen de la pestaña Envíos")
    header(sv, 4, ["Servicio", "Envíos", "Total enviado", "Comisiones", "Costo en el cambio", "Costo total", "% del total pagado"],
           [30, 10, 16, 14, 18, 14, 18])
    for r in range(5, 15):
        name = SERVICIOS[r - 5] if r - 5 < len(SERVICIOS) else None
        sv.cell(r, 1, name).fill = inp
        sv.cell(r, 2, f'=IF(A{r}="","",COUNTIF({EV}!$C$5:$C${ROWS + 4},A{r}))')
        for c, col in ((3, "D"), (4, "E"), (5, "I"), (6, "J")):
            sv.cell(r, c, f'=IF(A{r}="","",SUMIFS({EV}!${col}$5:${col}${ROWS + 4},{EV}!$C$5:$C${ROWS + 4},A{r}))').number_format = money
        sv.cell(r, 7, f'=IF(OR(A{r}="",C{r}=0),"",F{r}/(C{r}+D{r}))').number_format = pct

    # Envíos
    ev = wb.create_sheet("Envíos", 1)
    title(ev, "Envíos", "Un renglón por envío. Amarillo = tú; lo demás se calcula")
    header(ev, 4, ["Fecha", "A quién", "Servicio", "Enviaste (USD)", "Comisión (USD)", "Tipo de cambio que te dieron",
                   "Llegó (moneda de allá)", "Tipo de cambio de referencia (opcional)", "Costo en el cambio (USD)",
                   "Costo total (USD)", "% del total pagado", "Cómo pagaste", "1% estimado (efectivo o giro)", "Confirmación #"],
           [12, 20, 22, 13, 12, 14, 15, 16, 14, 13, 12, 18, 14, 16])
    dv_serv = DataValidation(type="list", formula1=f"=Servicios!$A$5:$A$14", allow_blank=True)
    dv_pago = DataValidation(type="list", formula1='"' + ",".join(PAGOS) + '"', allow_blank=True)
    dv_date = DataValidation(type="date", operator="greaterThan", formula1="DATE(2020,1,1)", allow_blank=True)
    for dv in (dv_serv, dv_pago, dv_date):
        ev.add_data_validation(dv)
    for r in range(5, ROWS + 5):
        for c in (1, 2, 3, 4, 5, 6, 8, 12, 14):
            ev.cell(r, c).fill = inp
        ev.cell(r, 1).number_format = "yyyy-mm-dd"
        ev.cell(r, 4).number_format = ev.cell(r, 5).number_format = money
        ev.cell(r, 6).number_format = ev.cell(r, 8).number_format = rate
        ev.cell(r, 7, f'=IF(OR(D{r}="",F{r}=""),"",D{r}*F{r})').number_format = rate
        ev.cell(r, 9, f'=IF(OR(D{r}="",F{r}="",H{r}="",H{r}=0),0,MAX(0,D{r}-G{r}/H{r}))').number_format = money
        ev.cell(r, 10, f'=IF(D{r}="","",N(E{r})+I{r}+M{r})').number_format = money
        ev.cell(r, 11, f'=IF(D{r}="","",J{r}/(D{r}+N(E{r})))').number_format = pct
        ev.cell(r, 13, f'=IF(OR(L{r}="Efectivo",L{r}="Giro o cheque de caja"),ROUND(N(D{r})*0.01,2),0)').number_format = money
    dv_serv.add(f"C5:C{ROWS + 4}")
    dv_pago.add(f"L5:L{ROWS + 4}")
    dv_date.add(f"A5:A{ROWS + 4}")
    for i, (d, who, s, usd, fee, fx, ref, pay, conf) in enumerate(EXAMPLES, 5):
        for c, v in zip((1, 2, 3, 4, 5, 6, 8, 12, 14), (d, who, s, usd, fee, fx, ref, pay, conf)):
            ev.cell(i, c, v)

    # Meses
    ms = wb.create_sheet("Meses", 2)
    title(ms, "Mes por mes", "Escribe el año en amarillo")
    ms["A3"], ms["B3"] = "Año", 2027
    ms["A3"].font = Font(bold=True)
    ms["B3"].fill = inp
    header(ms, 4, ["Mes", "Envíos", "Total enviado", "Comisiones", "Costo en el cambio", "1% estimado", "Costo total",
                   "% del total pagado"], [14, 10, 16, 14, 18, 14, 14, 18])
    ms.freeze_panes = "A5"
    rng = lambda col: f"{EV}!${col}$5:${col}${ROWS + 4}"  # noqa: E731
    for i, m in enumerate(MESES):
        r = 5 + i
        crit = f'{rng("A")},">="&DATE($B$3,{i + 1},1),{rng("A")},"<"&DATE($B$3,{i + 2},1)'
        ms.cell(r, 1, m)
        ms.cell(r, 2, f"=COUNTIFS({crit})")
        for c, col in ((3, "D"), (4, "E"), (5, "I"), (6, "M"), (7, "J")):
            ms.cell(r, c, f"=SUMIFS({rng(col)},{crit})").number_format = money
        ms.cell(r, 8, f'=IF(C{r}=0,"",G{r}/(C{r}+D{r}))').number_format = pct
    r = 17
    ms.cell(r, 1, "Año").font = Font(bold=True)
    for c in range(2, 8):
        L = chr(64 + c)
        ms.cell(r, c, f"=SUM({L}5:{L}16)").number_format = money if c > 2 else "0"
        ms.cell(r, c).fill = tot
    ms.cell(r, 8, '=IF(C17=0,"",G17/(C17+D17))').number_format = pct
    ms.cell(r, 1).fill = ms.cell(r, 8).fill = tot

    # Comparar
    cp = wb.create_sheet("Comparar", 1)
    title(cp, "Comparar antes de enviar", "Mismo monto en los tres; gana el que deja más dinero allá")
    cp["A3"], cp["B3"] = "Monto a enviar (USD)", 300
    cp["A3"].font = Font(bold=True)
    cp["B3"].fill, cp["B3"].number_format = inp, money
    header(cp, 5, ["Servicio", "Comisión (USD)", "Tipo de cambio", "Llega allá", "Total que pagas (USD)", "Llega por cada $1 que pagas"],
           [26, 15, 14, 16, 18, 20])
    cp.freeze_panes = "A6"
    for i, (s, fee, fx) in enumerate(zip(SERVICIOS, (3.99, 0, 1.99), (17.55, 17.20, 17.80))):
        r = 6 + i
        for c, v in ((1, s), (2, fee), (3, fx)):
            cp.cell(r, c, v).fill = inp
        cp.cell(r, 2).number_format = money
        cp.cell(r, 3).number_format = rate
        cp.cell(r, 4, f'=IF(C{r}="","",$B$3*C{r})').number_format = rate
        cp.cell(r, 5, f'=IF(C{r}="","",$B$3+N(B{r}))').number_format = money
        cp.cell(r, 6, f'=IF(C{r}="","",D{r}/E{r})').number_format = rate
    cp["A10"] = "El que deja más allá:"
    cp["A10"].font = Font(bold=True)
    cp["B10"] = "=INDEX(A6:A8,MATCH(MAX(F6:F8),F6:F8,0))"
    cp["B10"].font = Font(bold=True, color=BRAND.accent_d[1:])
    cp["A12"] = "Si pagas en efectivo, giro o cheque de caja, suma el 1% federal (desde 2026). Verifica con tu servicio."
    cp["A12"].font = Font(italic=True, color="5D6470")

    wb.save(path)
    return path
