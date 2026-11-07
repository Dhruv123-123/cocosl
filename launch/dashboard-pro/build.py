"""Money Dashboard Pro: the $12 paid spreadsheet behind the free Money Dashboard maker (apps/budget/money-dashboard.html).

    python launch/dashboard-pro/build.py [--out DIR] [--lang en|es|both]

Writes the .xlsx (and, with --kit, the Start Here PDF, covers, screenshots, zip and LISTING.md via kit.py).
Tabs: Start, Dashboard, Transactions, Budget vs Actual, Trends, Sinking Funds, Categories.

Design rules (same as the other Money Made Simple sheets): only functions that survive a Google Sheets import and work in
every Excel since 2010 (SUMIFS, SUMIF, COUNTIFS, INDEX/MATCH, EDATE, DATEDIF, REPT, IFERROR); no TEXT() date formats, because
their codes change with the spreadsheet's language; months are matched by date ranges, never by text. Yellow cells are the
buyer's; everything else calculates. Category names and the Transactions columns match the free tool's download, so a
buyer can paste its Transactions tab straight in.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, DoughnutChart, Reference
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, str(Path(__file__).parent))
from text import TEXT  # noqa: E402

INK, PAPER, GOLD, GREEN, RED, MUTED = "0B1D13", "F4F1E8", "F2B134", "2FBF71", "C0392B", "5B6B61"
HEAD = PatternFill("solid", fgColor="12291B")
INPUT = PatternFill("solid", fgColor="FFF4D6")
BAND = PatternFill("solid", fgColor="F4F1E8")
TOTAL = PatternFill("solid", fgColor="E3F4EA")
MONEY = '"$"#,##0.00;[Red]-"$"#,##0.00'
MONEY0 = '"$"#,##0;[Red]-"$"#,##0'
PCT = "0%"
MONTH = "mmm yyyy"
DATE = "yyyy-mm-dd"
THIN = Border(top=Side(style="thin", color="DDD6C4"))

N_CATS = 40          # Categories rows 2..41
N_TX = 1500          # Transactions rows 2..1501
N_FUNDS = 12
N_CONTRIB = 300
MONTHS = 12


def q(name: str) -> str:
    return "'" + name.replace("'", "''") + "'"


class Book:
    def __init__(self, lang: str):
        self.t = TEXT[lang]
        self.lang = lang
        self.wb = Workbook()
        self.wb.remove(self.wb.active)
        n = self.t["tabs"]
        self.start, self.dash, self.tx, self.bva, self.trend, self.funds, self.cats = (self.wb.create_sheet(n[k]) for k in
            ("start", "dash", "tx", "bva", "trend", "funds", "cats"))
        self.N = {k: q(v) for k, v in n.items()}

    # ---------- helpers ----------
    def title(self, ws, text, sub, widths):
        ws["A1"] = text
        ws["A1"].font = Font(name="Arial", size=18, bold=True, color=INK)
        ws["A2"] = sub
        ws["A2"].font = Font(name="Arial", size=10, italic=True, color=MUTED)
        for col, w in widths.items():
            ws.column_dimensions[col].width = w
        ws.sheet_view.showGridLines = False
        ws.sheet_properties.tabColor = "12291B"
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
        ws.page_setup.orientation = "landscape"

    def header(self, ws, row, labels, col=1):
        for i, v in enumerate(labels):
            c = ws.cell(row=row, column=col + i, value=v)
            c.font = Font(name="Arial", bold=True, color="FFFFFF")
            c.fill = HEAD
            c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.row_dimensions[row].height = 30

    def put(self, ws, ref, value, fmt=None, bold=False, inp=False, fill=None, color=None, size=None):
        c = ws[ref]
        c.value = value
        if fmt:
            c.number_format = fmt
        c.font = Font(name="Arial", bold=bold, color=color or INK, size=size or 11)
        if inp:
            c.fill = INPUT
        elif fill:
            c.fill = fill
        return c

    @staticmethod
    def tidy(ch):
        """Axes that show in every app, legend underneath, gaps (not zeros) for #N/A."""
        for ax in (ch.x_axis, ch.y_axis):
            ax.delete = False
        ch.x_axis.tickLblSkip = 1
        ch.y_axis.majorGridlines = None
        ch.legend.position = "b"
        ch.display_blanks = "gap"

    # ---------- tabs ----------
    def build(self, example: bool = True):
        t = self.t
        self.categories()
        self.transactions(example)
        self.trends()
        self.budget_vs_actual()
        self.sinking_funds(example)
        self.dashboard()
        self.start_tab()
        self.wb.active = 0
        self.wb.calculation.fullCalcOnLoad = True
        self.wb.properties.title = t["product"]
        self.wb.properties.creator = "Money Made Simple"
        return self.wb

    def categories(self):
        t, ws = self.t, self.cats
        self.title(ws, t["cats_title"], t["cats_sub"], {"A": 34, "B": 16, "C": 18, "D": 60})
        self.header(ws, 4, t["cats_head"])
        types = t["types"]
        for i, (name, typ, budget) in enumerate(t["categories"]):
            r = 5 + i
            self.put(ws, f"A{r}", name, inp=True)
            self.put(ws, f"B{r}", types[typ], inp=True)
            self.put(ws, f"C{r}", budget or None, MONEY0, inp=True)
        for r in range(5 + len(t["categories"]), 5 + N_CATS):
            for col in "ABC":
                ws[f"{col}{r}"].fill = INPUT
            ws[f"C{r}"].number_format = MONEY0
        self.put(ws, "D5", t["cats_note"], color=MUTED, size=10)
        ws["D5"].alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells("D5:D14")
        dv = DataValidation(type="list", formula1='"' + ",".join(types.values()) + '"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"B5:B{4 + N_CATS}")
        ws.freeze_panes = "A5"
        self.cat_rng = lambda col: f"{self.N['cats']}!${col}$5:${col}${4 + N_CATS}"  # noqa: E731

    def transactions(self, example):
        t, ws = self.t, self.tx
        self.title(ws, t["tx_title"], t["tx_sub"], {"A": 13, "B": 12, "C": 46, "D": 30, "E": 14})
        self.header(ws, 4, t["tx_head"])
        rows = t["example_tx"] if example else []
        for i in range(N_TX):
            r = 5 + i
            ws[f"B{r}"] = f'=IF(A{r}="","",DATE(YEAR(A{r}),MONTH(A{r}),1))'
            ws[f"B{r}"].number_format = MONTH
            ws[f"B{r}"].font = Font(name="Arial", color=MUTED)
            ws[f"A{r}"].number_format = DATE
            ws[f"E{r}"].number_format = MONEY
            if i < len(rows):
                d, desc, cat, amt = rows[i]
                ws[f"A{r}"] = d
                ws[f"C{r}"] = desc
                ws[f"D{r}"] = cat
                ws[f"E{r}"] = amt
            for col in "ACDE":
                ws[f"{col}{r}"].fill = INPUT if i < 60 or i < len(rows) else PatternFill()
        dv = DataValidation(type="list", formula1=self.cat_rng("A"), allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"D5:D{4 + N_TX}")
        ws.freeze_panes = "A5"
        ws.print_area = f"A1:E{max(60, 8 + len(rows))}"
        ws.auto_filter.ref = f"A4:E{4 + N_TX}"
        last = 4 + N_TX
        self.tx_rng = lambda col: f"{self.N['tx']}!${col}$5:${col}${last}"  # noqa: E731

    def month_sum(self, cat_ref, month_ref, sign_ref):
        a, c, d = self.tx_rng("E"), self.tx_rng("D"), self.tx_rng("A")
        return (f'IF({sign_ref}="{self.t["types"]["income"]}",1,-1)*SUMIFS({a},{c},{cat_ref},{d},">="&{month_ref},'
                f'{d},"<"&EDATE({month_ref},1))')

    def trends(self):
        t, ws = self.t, self.trend
        self.title(ws, t["trend_title"], t["trend_sub"], {"A": 30, **{L(2 + i): 12 for i in range(MONTHS)}, "N": 14, "O": 14, "P": 4, "Q": 14})
        self.header(ws, 4, [t["category"]] + [""] * MONTHS + [t["avg"], t["total"]])
        for i in range(MONTHS):
            c = ws.cell(row=4, column=2 + i, value=f"={self.N['dash']}!$C$5" if i == 0 else f"=EDATE({L(1 + i)}4,1)")
            c.number_format = "mmm yy"
        self.header(ws, 4, [t["helper"]], col=17)
        ws.column_dimensions["Q"].hidden = True
        types = t["types"]
        r0 = 5
        for k in range(N_CATS):
            r = r0 + k
            cr = 5 + k  # Categories row
            ws[f"A{r}"] = f'=IF({self.N["cats"]}!A{cr}="","",{self.N["cats"]}!A{cr})'
            for i in range(MONTHS):
                col = L(2 + i)
                ws[f"{col}{r}"] = f'=IF(OR($A{r}="",{col}$4>{self.N["dash"]}!$C$9),"",{self.month_sum(f"$A{r}", f"{col}$4", f"{self.N["cats"]}!$B{cr}")})'
                ws[f"{col}{r}"].number_format = MONEY0
            ws[f"N{r}"] = f'=IF($A{r}="","",IFERROR(SUMIF($B$4:$M$4,"<="&{self.N["dash"]}!$C$6,B{r}:M{r})/{self.N["dash"]}!$C$7,0))'
            ws[f"O{r}"] = f'=IF($A{r}="","",SUM(B{r}:M{r}))'
            # Helper: this month's amount for spending categories only (for the dashboard's biggest category).
            ws[f"Q{r}"] = f'=IF({self.N["cats"]}!$B{cr}="{types["spend"]}",IFERROR(INDEX(B{r}:M{r},{self.N["dash"]}!$C$8),0),"")'
            for col in "NO":
                ws[f"{col}{r}"].number_format = MONEY0
            if k % 2:
                for col in range(1, 16):
                    ws.cell(row=r, column=col).fill = BAND
        self.trend_rows = (r0, r0 + N_CATS - 1)
        s = r0 + N_CATS + 1
        self.sum_rows = {}
        typ = self.cat_rng("B")
        for j, (key, label) in enumerate([("income", t["money_in"]), ("spend", t["spending"]), ("save", t["saved"])]):
            r = s + j
            self.put(ws, f"A{r}", label, bold=True, fill=TOTAL)
            for i in range(MONTHS + 2):
                col = L(2 + i)
                hide = f'{col}$4>{self.N["dash"]}!$C$9' if i < MONTHS else 'FALSE'
                self.put(ws, f"{col}{r}", f'=IF({hide},"",SUMIF({typ},"{types[key]}",{col}{r0}:{col}{r0 + N_CATS - 1}))', MONEY0, bold=True, fill=TOTAL)
            self.sum_rows[key] = r
        r = s + 3
        self.put(ws, f"A{r}", t["left"], bold=True, fill=TOTAL)
        for i in range(MONTHS + 2):
            col = L(2 + i)
            self.put(ws, f"{col}{r}", f'=IF({col}{s}="","",{col}{s}-{col}{s + 1}-{col}{s + 2})', MONEY0, bold=True, fill=TOTAL)
        self.sum_rows["left"] = r
        r = s + 4
        self.put(ws, f"A{r}", t["rate"], bold=True)
        for i in range(MONTHS + 2):
            col = L(2 + i)
            self.put(ws, f"{col}{r}", f'=IF(N({col}{s})>0,({col}{s + 3}+{col}{s + 2})/{col}{s},"")', PCT)
        self.sum_rows["rate"] = r
        ws.freeze_panes = "B5"
        ws.conditional_formatting.add(f"B{s + 3}:O{s + 3}", CellIsRule(operator="lessThan", formula=["0"], font=Font(color=RED, bold=True)))

        ch = BarChart()
        ch.type = "col"
        ch.gapWidth = 80
        ch.title = t["chart_trend"]
        ch.height, ch.width = 8, 22
        ch.y_axis.number_format = '"$"#,##0'
        ch.y_axis.majorGridlines = None
        for key in ("income", "spend", "left"):
            ch.add_data(Reference(ws, min_col=1, max_col=1 + MONTHS, min_row=self.sum_rows[key], max_row=self.sum_rows[key]), from_rows=True, titles_from_data=True)
        ch.set_categories(Reference(ws, min_col=2, max_col=1 + MONTHS, min_row=4, max_row=4))
        for sr, color in zip(ch.series, (GREEN, RED, GOLD)):
            sr.graphicalProperties.solidFill = color
            sr.graphicalProperties.line.solidFill = color
        self.tidy(ch)
        self.trend_chart = ch
        ws.add_chart(ch, f"A{s + 7}")

    def budget_vs_actual(self):
        t, ws = self.t, self.bva
        self.title(ws, t["bva_title"], t["bva_sub"], {"A": 30, "B": 14, "C": 14, "D": 14, "E": 14, "F": 10, "G": 22, "H": 16})
        self.put(ws, "A4", t["month_label"], bold=True)
        self.put(ws, "B4", f"={self.N['dash']}!$C$6", MONTH, bold=True)
        self.header(ws, 6, t["bva_head"])
        types = t["types"]
        for k in range(N_CATS):
            r, cr = 7 + k, 5 + k
            ws[f"A{r}"] = f'=IF({self.N["cats"]}!A{cr}="","",{self.N["cats"]}!A{cr})'
            ws[f"H{r}"] = f'=IF($A{r}="","",{self.N["cats"]}!B{cr})'
            ws[f"B{r}"] = f'=IF(OR($A{r}="",{self.N["cats"]}!C{cr}=""),"",{self.N["cats"]}!C{cr})'
            ws[f"C{r}"] = f'=IF($A{r}="","",{self.month_sum(f"$A{r}", "$B$4", f"$H{r}")})'
            ws[f"D{r}"] = f'=IF(OR($A{r}="",B{r}=""),"",IF(H{r}="{types["income"]}",C{r}-B{r},B{r}-C{r}))'
            ws[f"E{r}"] = f'=IF($A{r}="","",IFERROR(INDEX({self.N["trend"]}!$N$5:$N${4 + N_CATS},{k + 1}),0))'
            ws[f"F{r}"] = f'=IF(OR($A{r}="",B{r}="",B{r}=0),"",C{r}/B{r})'
            ws[f"G{r}"] = f'=IF(F{r}="","",REPT("█",MIN(10,ROUND(F{r}*10,0)))&REPT("░",MAX(0,10-ROUND(F{r}*10,0))))'
            for col in "BCDE":
                ws[f"{col}{r}"].number_format = MONEY0
            ws[f"F{r}"].number_format = PCT
            ws[f"G{r}"].font = Font(name="Arial", color=GREEN)
            ws[f"H{r}"].font = Font(name="Arial", color=MUTED, size=10)
            if k % 2:
                for col in "ABCDEFGH":
                    ws[f"{col}{r}"].fill = BAND
        last = 6 + N_CATS
        over = FormulaRule(formula=[f'AND($H7="{types["spend"]}",ISNUMBER($D7),$D7<0)'], font=Font(color=RED, bold=True))
        ws.conditional_formatting.add(f"D7:G{last}", over)
        r = last + 2
        self.put(ws, f"A{r}", t["bva_total"], bold=True, fill=TOTAL)
        self.put(ws, f"B{r}", f'=SUMIF($H$7:$H${last},"{types["spend"]}",B7:B{last})', MONEY0, bold=True, fill=TOTAL)
        self.put(ws, f"C{r}", f'=SUMIF($H$7:$H${last},"{types["spend"]}",C7:C{last})', MONEY0, bold=True, fill=TOTAL)
        self.put(ws, f"D{r}", f"=B{r}-C{r}", MONEY0, bold=True, fill=TOTAL)
        self.put(ws, f"E{r}", f'=SUMIF($H$7:$H${last},"{types["spend"]}",E7:E{last})', MONEY0, bold=True, fill=TOTAL)
        self.bva_total = r
        self.put(ws, f"A{r + 1}", t["bva_over"], bold=True)
        self.put(ws, f"B{r + 1}", f'=COUNTIFS($H$7:$H${last},"{types["spend"]}",D7:D{last},"<0")', "0", bold=True)
        ws.freeze_panes = "B7"

        n = sum(1 for c in t["categories"] if c[1] == "spend")
        ch = BarChart()
        ch.type = "bar"
        ch.title = t["chart_bva"]
        ch.height, ch.width = 11, 16
        ch.add_data(Reference(ws, min_col=2, max_col=3, min_row=6, max_row=6 + n), titles_from_data=True)
        ch.set_categories(Reference(ws, min_col=1, min_row=7, max_row=6 + n))
        ch.x_axis.scaling.orientation = "maxMin"
        ch.y_axis.number_format = '"$"#,##0'
        ch.y_axis.majorGridlines = None
        ch.series[0].graphicalProperties.solidFill = "DDD6C4"
        ch.series[1].graphicalProperties.solidFill = GOLD
        ch.gapWidth = 60
        self.tidy(ch)
        ws.add_chart(ch, "J6")
        self.bva_chart_n = n

    def sinking_funds(self, example):
        t, ws = self.t, self.funds
        self.title(ws, t["funds_title"], t["funds_sub"], {"A": 26, "B": 13, "C": 13, "D": 14, "E": 13, "F": 11, "G": 15, "H": 9, "I": 16, "J": 3, "K": 13, "L": 26, "M": 13})
        self.header(ws, 4, t["funds_head"])
        self.header(ws, 4, t["contrib_head"], col=11)
        cl = f"$L$5:$L${4 + N_CONTRIB}"
        ca = f"$M$5:$M${4 + N_CONTRIB}"
        funds = t["example_funds"] if example else []
        for k in range(N_FUNDS):
            r = 5 + k
            if k < len(funds):
                name, target, due = funds[k]
                ws[f"A{r}"], ws[f"B{r}"], ws[f"C{r}"] = name, target, due
            for col in "ABC":
                ws[f"{col}{r}"].fill = INPUT
            ws[f"B{r}"].number_format = MONEY0
            ws[f"C{r}"].number_format = DATE
            ws[f"D{r}"] = f'=IF(A{r}="","",SUMIF({cl},A{r},{ca}))'
            ws[f"E{r}"] = f'=IF(A{r}="","",MAX(0,B{r}-D{r}))'
            ws[f"F{r}"] = f'=IF(OR(A{r}="",C{r}=""),"",IF(C{r}<=TODAY(),0,DATEDIF(TODAY(),C{r},"m")+1))'
            ws[f"G{r}"] = f'=IF(OR(A{r}="",F{r}=""),"",IF(E{r}=0,0,IF(F{r}=0,E{r},E{r}/F{r})))'
            ws[f"H{r}"] = f'=IF(OR(A{r}="",B{r}="",B{r}=0),"",MIN(1,D{r}/B{r}))'
            ws[f"I{r}"] = f'=IF(H{r}="","",REPT("█",ROUND(H{r}*10,0))&REPT("░",10-ROUND(H{r}*10,0)))'
            for col in "DEG":
                ws[f"{col}{r}"].number_format = MONEY0
            ws[f"F{r}"].number_format = "0"
            ws[f"H{r}"].number_format = PCT
            ws[f"I{r}"].font = Font(name="Arial", color=GREEN)
        last = 4 + N_FUNDS
        r = last + 1
        self.put(ws, f"A{r}", t["total"], bold=True, fill=TOTAL)
        for col in "BDEG":
            self.put(ws, f"{col}{r}", f"=SUM({col}5:{col}{last})", MONEY0, bold=True, fill=TOTAL)
        self.funds_total = r
        ws.conditional_formatting.add(f"A5:I{last}", FormulaRule(formula=[f'AND($H5<>"",$H5>=1)'], fill=PatternFill("solid", fgColor="E3F4EA")))
        ws.conditional_formatting.add(f"F5:G{last}", FormulaRule(formula=[f'AND($F5<>"",$F5=0,$E5>0)'], font=Font(color=RED, bold=True)))
        contrib = t["example_contrib"] if example else []
        for k in range(N_CONTRIB):
            rr = 5 + k
            if k < len(contrib):
                d, f, a = contrib[k]
                ws[f"K{rr}"], ws[f"L{rr}"], ws[f"M{rr}"] = d, f, a
            ws[f"K{rr}"].number_format = DATE
            ws[f"M{rr}"].number_format = MONEY
            if k < 40:
                for col in "KLM":
                    ws[f"{col}{rr}"].fill = INPUT
        dv = DataValidation(type="list", formula1=f"$A$5:$A${last}", allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"L5:L{4 + N_CONTRIB}")
        self.put(ws, f"A{r + 2}", t["funds_note"], color=MUTED, size=10)
        ws.freeze_panes = "A5"

        ch = BarChart()
        ch.type = "bar"
        ch.title = t["chart_funds"]
        ch.height, ch.width = 9, 16
        ch.add_data(Reference(ws, min_col=2, max_col=2, min_row=4, max_row=4 + max(1, len(funds))), titles_from_data=True)
        ch.add_data(Reference(ws, min_col=4, max_col=4, min_row=4, max_row=4 + max(1, len(funds))), titles_from_data=True)
        ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=4 + max(1, len(funds))))
        ch.x_axis.scaling.orientation = "maxMin"
        ch.y_axis.number_format = '"$"#,##0'
        ch.y_axis.majorGridlines = None
        ch.series[0].graphicalProperties.solidFill = "DDD6C4"
        ch.series[1].graphicalProperties.solidFill = GREEN
        ch.gapWidth = 60
        self.tidy(ch)
        ws.add_chart(ch, f"A{r + 4}")

    def dashboard(self):
        t, ws = self.t, self.dash
        self.title(ws, t["dash_title"], t["dash_sub"], {"A": 3, "B": 30, "C": 18, "D": 4, "E": 30, "F": 18, "G": 4, "H": 16})
        ex = t["example_settings"]
        self.put(ws, "B5", t["first_month"], bold=True)
        self.put(ws, "C5", ex[0], MONTH, bold=True, inp=True)
        self.put(ws, "B6", t["review_month"], bold=True)
        self.put(ws, "C6", ex[1], MONTH, bold=True, inp=True)
        dv = DataValidation(type="list", formula1=f"{self.N['trend']}!$B$4:$M$4", allow_blank=False)
        ws.add_data_validation(dv)
        dv.add("C6")
        # Helpers: months counted so far, and which Trends column is the month being reviewed.
        self.put(ws, "B7", t["months_so_far"], color=MUTED, size=10)
        self.put(ws, "C7", f'=MAX(1,MIN(12,COUNTIF({self.N["trend"]}!$B$4:$M$4,"<="&C6)))', "0", color=MUTED)
        self.put(ws, "B8", t["column_helper"], color=MUTED, size=10)
        self.put(ws, "C8", f'=IFERROR(MATCH(C6,{self.N["trend"]}!$B$4:$M$4,0),1)', "0", color=MUTED)
        self.put(ws, "B9", t["latest_helper"], color=MUTED, size=10)
        self.put(ws, "C9", f'=IF(COUNT({self.tx_rng("A")})=0,C6,DATE(YEAR(MAX({self.tx_rng("A")})),MONTH(MAX({self.tx_rng("A")})),1))', MONTH, color=MUTED)
        for r in (7, 8, 9):  # helpers: hidden, still calculating
            ws.row_dimensions[r].hidden = True
        ws.page_setup.fitToHeight = 1
        tr, s = self.N["trend"], self.sum_rows
        at = lambda key: f"INDEX({tr}!$B${s[key]}:$M${s[key]},$C$8)"  # noqa: E731
        avg = lambda key: f"{tr}!$N${s[key]}"  # noqa: E731
        self.header(ws, 10, [t["this_month"], ""], col=2)
        self.header(ws, 10, [t["average"], ""], col=5)
        rows = [("money_in", "income"), ("spending", "spend"), ("saved", "save"), ("left", "left")]
        for i, (lab, key) in enumerate(rows):
            r = 11 + i
            self.put(ws, f"B{r}", t[lab], bold=key == "left")
            self.put(ws, f"C{r}", f"={at(key)}", MONEY0, bold=True, size=13)
            self.put(ws, f"E{r}", t[lab], bold=key == "left")
            self.put(ws, f"F{r}", f"={avg(key)}", MONEY0, bold=True, size=13)
            for col in "BCEF":
                ws[f"{col}{r}"].border = THIN
        r = 15
        self.put(ws, f"B{r}", t["rate"])
        self.put(ws, f"C{r}", f'=IFERROR(INDEX({tr}!$B${s["rate"]}:$M${s["rate"]},$C$8),"")', PCT, bold=True, size=13)
        self.put(ws, f"E{r}", t["rate"])
        self.put(ws, f"F{r}", f'={tr}!$N${s["rate"]}', PCT, bold=True, size=13)
        a, b = self.trend_rows
        self.put(ws, "B17", t["biggest"], bold=True)
        self.put(ws, "C17", f'=IFERROR(INDEX({tr}!$A${a}:$A${b},MATCH(MAX({tr}!$Q${a}:$Q${b}),{tr}!$Q${a}:$Q${b},0)),"")', bold=True)
        self.put(ws, "B18", t["over_count"], bold=True)
        self.put(ws, "C18", f"={self.N['bva']}!B{self.bva_total + 1}", "0", bold=True)
        self.put(ws, "E17", t["funds_saved"], bold=True)
        self.put(ws, "F17", f"={self.N['funds']}!D{self.funds_total}", MONEY0, bold=True)
        self.put(ws, "E18", t["funds_monthly"], bold=True)
        self.put(ws, "F18", f"={self.N['funds']}!G{self.funds_total}", MONEY0, bold=True)
        ws.conditional_formatting.add("C14", CellIsRule(operator="lessThan", formula=["0"], font=Font(color=RED, bold=True, size=13)))
        ws.conditional_formatting.add("C18", CellIsRule(operator="greaterThan", formula=["0"], font=Font(color=RED, bold=True)))

        # Charts: the 12-month trend, and where this month's money went.
        trend = BarChart()
        trend.type = "col"
        trend.gapWidth = 80
        trend.title = t["chart_trend"]
        trend.height, trend.width = 8, 17
        trend.y_axis.number_format = '"$"#,##0'
        trend.y_axis.majorGridlines = None
        for key in ("income", "spend", "left"):
            trend.add_data(Reference(self.trend, min_col=1, max_col=1 + MONTHS, min_row=self.sum_rows[key], max_row=self.sum_rows[key]), from_rows=True, titles_from_data=True)
        trend.set_categories(Reference(self.trend, min_col=2, max_col=1 + MONTHS, min_row=4, max_row=4))
        for sr, color in zip(trend.series, (GREEN, RED, GOLD)):
            sr.graphicalProperties.solidFill = color
            sr.graphicalProperties.line.solidFill = color
        self.tidy(trend)
        ws.add_chart(trend, "B20")
        pie = DoughnutChart()
        pie.title = t["chart_where"]
        pie.height, pie.width = 12, 12
        pie.legend.position = "r"
        n = self.bva_chart_n
        pie.add_data(Reference(self.bva, min_col=3, min_row=6, max_row=6 + n), titles_from_data=True)
        pie.set_categories(Reference(self.bva, min_col=1, min_row=7, max_row=6 + n))
        pie.holeSize = 55
        ws.add_chart(pie, "E37")
        bva = BarChart()
        bva.type = "bar"
        bva.title = t["chart_bva"]
        bva.height, bva.width = 12, 10
        bva.add_data(Reference(self.bva, min_col=2, max_col=3, min_row=6, max_row=6 + n), titles_from_data=True)
        bva.set_categories(Reference(self.bva, min_col=1, min_row=7, max_row=6 + n))
        bva.x_axis.scaling.orientation = "maxMin"
        bva.y_axis.majorGridlines = None
        bva.series[0].graphicalProperties.solidFill = "DDD6C4"
        bva.series[1].graphicalProperties.solidFill = GOLD
        bva.legend.position = "b"
        self.tidy(bva)
        ws.add_chart(bva, "B37")

    def start_tab(self):
        t, ws = self.t, self.start
        self.title(ws, t["product"], t["start_sub"], {"A": 3, "B": 110})
        r = 4
        for kind, text in t["start"]:
            c = ws.cell(row=r, column=2, value=text)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            if kind == "h":
                c.font = Font(name="Arial", bold=True, size=13, color=INK)
                r += 1
            else:
                c.font = Font(name="Arial", size=11, color=INK)
                ws.row_dimensions[r].height = 15 * max(1, len(text) // 100 + 1)
                r += 1
        ws.cell(row=r + 1, column=2, value=t["legal"]).font = Font(name="Arial", italic=True, size=9, color=MUTED)


def build(lang: str, out: Path, example: bool = True) -> Path:
    b = Book(lang)
    wb = b.build(example)
    path = out / TEXT[lang]["file"]
    out.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist/dashboard-pro")
    ap.add_argument("--lang", default="both", choices=["en", "es", "both"])
    a = ap.parse_args()
    for lang in (["en", "es"] if a.lang == "both" else [a.lang]):
        print(build(lang, Path(a.out) / lang))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
