"""Two-brand 12-month revenue model (Money Made Simple + Scam Decoded), Nov 2026 - Oct 2027.

Builds two-brand-revenue-model-2027.xlsx with live formulas: change any input on the Inputs sheet and every
month recalculates. Run: python3 revenue_model_two_brands.py  (needs openpyxl).
Every input is an assumption or a sourced benchmark; the Inputs sheet says which, with links on Sources.
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.formatting.rule import CellIsRule

OUT = "two-brand-revenue-model-2027.xlsx"
MONTHS = ["Nov 26", "Dec 26", "Jan 27", "Feb 27", "Mar 27", "Apr 27", "May 27", "Jun 27", "Jul 27", "Aug 27", "Sep 27", "Oct 27"]
CASES = ["Low", "Base", "High"]
BRANDS = ["MMS", "Scam Decoded"]

# key: (label, unit, {brand: (low, base, high)}, source tag)
# A single tuple instead of a dict means the same value for both brands.
INPUTS = [
    ("start", "Launch month (1 = Nov 2026)", "month", {"MMS": (1, 1, 1), "Scam Decoded": (2, 2, 2)}, "plan"),
    ("ramp_exp", "Growth curve exponent (level = month-12 level x (active months/12)^exp)", "", (1.5, 1.5, 1.5), "est"),
    # YouTube
    ("yt_views", "YouTube long-form views a month, month 12", "views", {"MMS": (3000, 20000, 100000), "Scam Decoded": (2000, 12000, 60000)}, "est"),
    ("yt_watch", "Average watch minutes per long-form view", "min", {"MMS": (4, 4.5, 5), "Scam Decoded": (3.5, 4, 4.5)}, "est"),
    ("yt_subs", "YouTube subscribers, month 12", "subs", {"MMS": (400, 1500, 6000), "Scam Decoded": (300, 1000, 4000)}, "est"),
    ("yt_rpm", "Long-form RPM (creator share, $ per 1,000 views)", "$", {"MMS": (8, 10, 13), "Scam Decoded": (5, 6, 8)}, "rpm"),
    ("ypp_hours_new", "YPP watch hours for new applicants from Feb 2027 (month 4 on)", "hours", (8000, 8000, 8000), "ypp"),
    ("ypp_hours_old", "YPP watch hours before Feb 2027 (months 1-3)", "hours", (4000, 4000, 4000), "ypp"),
    ("ypp_subs", "YPP subscribers needed", "subs", (1000, 1000, 1000), "ypp"),
    ("shorts_views", "YouTube Shorts views a month, month 12", "views", {"MMS": (30000, 200000, 1500000), "Scam Decoded": (30000, 250000, 2000000)}, "est"),
    ("shorts_gate", "Shorts views in 90 days needed for Shorts ad share (from Feb 2027)", "views", (10_000_000, 10_000_000, 10_000_000), "ypp"),
    ("shorts_rpm", "Shorts RPM ($ per 1,000 views), if ever eligible", "$", (0.03, 0.05, 0.08), "est"),
    # TikTok
    ("tt_followers", "TikTok followers, month 12", "followers", {"MMS": (1500, 5000, 20000), "Scam Decoded": (1000, 4000, 20000)}, "est"),
    ("tt_views", "TikTok views a month, month 12", "views", {"MMS": (30000, 150000, 800000), "Scam Decoded": (30000, 150000, 1000000)}, "est"),
    ("tt_long_share", "Share of TikTok views on original videos over 1 minute that qualify (not fully AI)", "%", {"MMS": (0, 0.3, 0.5), "Scam Decoded": (0, 0.2, 0.4)}, "tt"),
    ("tt_rpm", "TikTok Creator Rewards RPM ($ per 1,000 qualified views)", "$", (0.5, 1.0, 1.5), "tt"),
    ("tt_min_followers", "Creator Rewards: followers needed", "followers", (10000, 10000, 10000), "tt"),
    ("tt_min_views", "Creator Rewards: views in last 30 days needed", "views", (100000, 100000, 100000), "tt"),
    # Email and products
    ("email_subs", "Email subscribers, month 12", "subs", {"MMS": (300, 1500, 6000), "Scam Decoded": (200, 900, 4000)}, "est"),
    ("welcome_conv", "New subscribers who buy during the welcome sequence", "%", {"MMS": (0.01, 0.02, 0.04), "Scam Decoded": (0.01, 0.02, 0.035)}, "ml"),
    ("campaign_conv", "List buyers per broadcast (share of list)", "%", (0.001, 0.002, 0.0032), "ml"),
    ("sends", "Broadcasts a month", "sends", (4, 4, 4), "plan"),
    ("net_order", "Net per email-driven order, after Gumroad fees", "$", {"MMS": (9, 12, 15), "Scam Decoded": (8, 9, 12)}, "cat"),
    ("market_orders", "Etsy and Gumroad Discover orders a month, month 12", "orders", {"MMS": (5, 30, 150), "Scam Decoded": (2, 12, 50)}, "est"),
    ("market_net", "Net per marketplace order, after Etsy fees", "$", (5.5, 5.5, 5.5), "cat"),
    ("jan_boost", "January multiplier on marketplace orders", "x", {"MMS": (1.4, 1.4, 1.4), "Scam Decoded": (1, 1, 1)}, "seas"),
    # Affiliates
    ("aff_clicks", "Affiliate link clicks a month, month 12", "clicks", {"MMS": (50, 400, 2500), "Scam Decoded": (30, 250, 1500)}, "est"),
    ("aff_conv", "Click-to-signup conversion", "%", {"MMS": (0.015, 0.02, 0.03), "Scam Decoded": (0.01, 0.015, 0.025)}, "est"),
    ("aff_payout", "Average payout per signup", "$", {"MMS": (30, 40, 60), "Scam Decoded": (25, 40, 65)}, "aff"),
    ("aff_start", "First month with approved affiliate links", "month", (3, 3, 3), "plan"),
    # Sponsors
    ("spon_min", "List size before sponsors are worth pitching", "subs", (2500, 2500, 2500), "spon"),
    ("spon_place", "Sponsored placements a month, once over the minimum", "placements", (0, 2, 4), "spon"),
    ("spon_per1k", "Sponsor pay per 1,000 subscribers per placement", "$", (5, 7.11, 25), "spon"),
]
COSTS = [
    ("c_domains", "Two domains ($23 a year)", (1.92, 1.92, 1.92), "dec"),
    ("c_api", "Anthropic API for new drafts", (5, 5, 10), "dec"),
    ("c_mailbox", "Mailbox or PO box for CAN-SPAM (estimate; varies by location)", (5, 10, 20), "dec"),
    ("c_etsy", "Etsy listing renewals (15 listings, every 4 months)", (0.75, 0.75, 1.5), "dec"),
    ("c_sender", "Sender paid plan once total subscribers pass 2,500 (estimate)", (30, 30, 50), "send"),
]
SOURCES = {
    "est": "Our estimate, aligned with growth-90-days-two-brands.md (day-90 floors and goals) and kept below revenue-model-2027.md's base case",
    "plan": "two-brand-launch-plan.md and DHRUV_DECISIONS.md row 2b (MMS Mon 16 Nov, Scam Decoded ~Mon 30 Nov)",
    "ypp": "YouTube Official Blog, 10 Aug 2026: 1,000 subs + 8,000 hours or 20M Shorts views for new applicants from 1 Feb 2027; Shorts ad share needs 10M Shorts views in 90 days (youtube-policy-review-nov-2026.md)",
    "rpm": "OutlierKit RPM benchmarks (19 Aug 2026); GoFaceless faceless long-form RPM (13 Oct 2026); revenue-model-2027.md",
    "tt": "ttcalculator.net Creator Rewards guide (updated 10 Jul 2026): 18+, 10K followers, 100K views/30 days, personal account, videos over 1 min, US RPM ~$0.50-2.00; fully-AI exclusion per tiktok-instagram-monetization.md",
    "ml": "MailerLite, 20 Apr 2026: automations convert 0.42% per email and campaigns 0.32% (3.28% for lists under 500); 300M+ emails, e-commerce accounts",
    "cat": "PRODUCTS_CATALOG (PR #6) prices $5-39; fees from free-tool-limits.md (Gumroad 10% + $0.50; Etsy $0.20 + 6.5% + 3% + $0.25)",
    "seas": "bfcm-plan-2026.md / template-pricing-jan-2027.md: budget-planner searches peak in January",
    "aff": "affiliate-answers-five-programs.md: Aura $65 per enrolment, NordVPN 40% of new plans, Keeper up to $50; bank and HYSA bounties from research/02-affiliate-programs.md",
    "spon": "newsletter-sponsorship-benchmarks.md: Paved finance average $7.11 per 1,000 subscribers per placement; vendor quotes up to $25+",
    "dec": "DHRUV_DECISIONS.md rows 4, 5, 8, 18",
    "send": "newsletter-tool-decision.md: Sender Free to 2,500 subscribers; Standard from about $9/month at 500, more at higher tiers (check Sender's pricing page)",
}
LINKS = [
    ("YouTube Official Blog: YPP updates for 2027 (10 Aug 2026)", "https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/"),
    ("YouTube Help: YPP eligibility", "https://support.google.com/youtube/answer/72851"),
    ("TikTok Creator Rewards guide, ttcalculator.net (updated 10 Jul 2026)", "https://ttcalculator.net/guides/creator-rewards-program/"),
    ("MailerLite: email marketing conversion rate (20 Apr 2026)", "https://www.mailerlite.com/blog/email-marketing-conversion-rate"),
    ("OutlierKit: YouTube RPM benchmarks (19 Aug 2026)", "https://outlierkit.com/resources/youtube-rpm-benchmarks/"),
    ("GoFaceless: faceless long-form RPM (13 Oct 2026)", "https://www.gofaceless.ai/blog/faceless-youtube-long-form-video-rpm"),
    ("SenderCircle: finance newsletter advertising rates (2026)", "https://sendercircle.com/guides/finance-newsletter-advertising-rates"),
    ("Instagram: Reels bonuses are invite-only; no per-view pay for accounts our size (tiktok-instagram-monetization.md)", ""),
    ("Pinterest: no open US pay-per-view creator program found; modelled as traffic only", ""),
]

wb = Workbook()
hdr = Font(bold=True, color="FFFFFF"); hfill = PatternFill("solid", fgColor="1F3A5F")
inpfill = PatternFill("solid", fgColor="FFF4CC"); bold = Font(bold=True)
thin = Border(bottom=Side(style="thin", color="BBBBBB"))

# ---------------- Inputs ----------------
wi = wb.active; wi.title = "Inputs"
wi.append(["Two-brand revenue model: inputs (yellow cells are editable)"]); wi["A1"].font = Font(bold=True, size=13)
wi.append(["Every number is an assumption. 'est' rows are our estimates; the others follow the source on the right. Change a yellow cell and the Model and Summary sheets recalculate."])
wi.append([])
wi.append(["Key", "Input", "Unit", "Brand", "Low", "Base", "High", "Source"])
for c in wi[4]: c.font = hdr; c.fill = hfill
REF = {}  # (key, brand) -> row
r = 5
for key, label, unit, vals, src in INPUTS:
    per = vals if isinstance(vals, dict) else {b: vals for b in BRANDS}
    for b in BRANDS:
        lo, ba, hi = per[b]
        wi.append([key, label, unit, b, lo, ba, hi, SOURCES[src]])
        for col in (5, 6, 7):
            cell = wi.cell(r, col); cell.fill = inpfill
            if unit == "%": cell.number_format = "0.0%"
            elif unit == "$": cell.number_format = "$#,##0.00"
            else: cell.number_format = "#,##0.##"
        REF[(key, b)] = r; r += 1
r += 1
wi.cell(r, 1, "Monthly costs (shared by both brands)").font = bold; r += 1
for key, label, vals, src in COSTS:
    wi.append([key, label, "$/month", "Both", *vals, SOURCES[src]])
    for col in (5, 6, 7):
        wi.cell(r, col).fill = inpfill; wi.cell(r, col).number_format = "$#,##0.00"
    REF[(key, "Both")] = r; r += 1
for col, w in zip("ABCDEFGH", (16, 70, 11, 14, 11, 11, 11, 120)):
    wi.column_dimensions[col].width = w
wi.freeze_panes = "E5"

def inp(key, brand, case):
    col = "EFG"[CASES.index(case)]
    return f"Inputs!${col}${REF[(key, brand)]}"

# ---------------- Model ----------------
wm = wb.create_sheet("Model")
wm.append(["Monthly model: one block per brand and case. Month 1 = Nov 2026 (MMS launches Mon 16 Nov); Scam Decoded starts month 2."])
wm["A1"].font = Font(bold=True, size=12)
wm.append(["Month #", ""] + list(range(1, 13)) + ["Year 1"])
wm.append(["Month", ""] + MONTHS + [""])
for c in wm[2] + wm[3]: c.font = bold
MC = [L(3 + i) for i in range(12)]  # C..N
TOT = L(15)                           # O
BLOCK = {}  # (brand, case) -> {rowname: row}
row = 5
STREAMS = [("yt_rev", "YouTube long-form ads"), ("shorts_rev", "YouTube Shorts ads"), ("tt_rev", "TikTok Creator Rewards"),
           ("prod_rev", "Products from email"), ("mkt_rev", "Etsy + Gumroad Discover"), ("aff_rev", "Affiliates"), ("spon_rev", "Newsletter sponsors")]
for b in BRANDS:
    for case in CASES:
        g = lambda k: inp(k, b, case)
        R = {}
        wm.cell(row, 1, f"{b}: {case} case").font = Font(bold=True, size=12, color="1F3A5F"); row += 1
        def line(name, label, fn, fmt="#,##0", total=False, boldrow=False):
            nonlocal_row = line.row
            R[name] = nonlocal_row  # set first, so a row can refer to its own previous month
            wm.cell(nonlocal_row, 1, label)
            for i, col in enumerate(MC):
                wm[f"{col}{nonlocal_row}"] = "=" + fn(i, col)
                wm[f"{col}{nonlocal_row}"].number_format = fmt
            if total:
                wm[f"{TOT}{nonlocal_row}"] = f"=SUM(C{nonlocal_row}:N{nonlocal_row})"
                wm[f"{TOT}{nonlocal_row}"].number_format = fmt; wm[f"{TOT}{nonlocal_row}"].font = bold
            if boldrow:
                for cc in wm[nonlocal_row]: cc.font = bold
            R[name] = nonlocal_row; line.row += 1
        line.row = row
        prev = lambda i, name: (MC[i - 1] + str(R[name])) if i > 0 else None
        line("active", "Active months", lambda i, c: f"MAX(0,{c}$2-{g('start')}+1)", "0")
        line("ramp", "Share of month-12 level", lambda i, c: f"IF({c}{R['active']}=0,0,MIN(1,{c}{R['active']}/12)^{g('ramp_exp')})", "0.00")
        line("ytv", "YouTube long-form views", lambda i, c: f"{g('yt_views')}*{c}{R['ramp']}")
        line("yth", "Watch hours this month", lambda i, c: f"{c}{R['ytv']}*{g('yt_watch')}/60")
        line("ythc", "Watch hours, running total (12 months)", lambda i, c: f"SUM($C{R['yth']}:{c}{R['yth']})")
        line("yts", "YouTube subscribers", lambda i, c: f"{g('yt_subs')}*{c}{R['ramp']}")
        line("ypp", "In YPP (1 = yes)", lambda i, c: f"IF(AND({c}{R['yts']}>={g('ypp_subs')},{c}{R['ythc']}>=IF({c}$2<=3,{g('ypp_hours_old')},{g('ypp_hours_new')})),1,{('0' if i == 0 else prev(i, 'ypp'))})", "0")
        line("yt_rev", "YouTube long-form ad revenue ($)", lambda i, c: ("0" if i == 0 else f"IF({prev(i,'ypp')}=1,{c}{R['ytv']}/1000*{g('yt_rpm')},0)"), "$#,##0", True)
        line("shv", "Shorts views", lambda i, c: f"{g('shorts_views')}*{c}{R['ramp']}")
        line("shorts_rev", "YouTube Shorts ad revenue ($)", lambda i, c: f"IF(AND({c}{R['ypp']}=1,{c}{R['shv']}*3>={g('shorts_gate')}),{c}{R['shv']}/1000*{g('shorts_rpm')},0)", "$#,##0", True)
        line("ttf", "TikTok followers", lambda i, c: f"{g('tt_followers')}*{c}{R['ramp']}")
        line("ttv", "TikTok views", lambda i, c: f"{g('tt_views')}*{c}{R['ramp']}")
        line("tt_rev", "TikTok Creator Rewards ($)", lambda i, c: f"IF(AND({c}{R['ttf']}>={g('tt_min_followers')},{c}{R['ttv']}>={g('tt_min_views')}),{c}{R['ttv']}*{g('tt_long_share')}/1000*{g('tt_rpm')},0)", "$#,##0", True)
        line("subs", "Email subscribers", lambda i, c: f"{g('email_subs')}*{c}{R['ramp']}")
        line("new", "New subscribers this month", lambda i, c: f"{c}{R['subs']}-{('0' if i == 0 else prev(i,'subs'))}")
        line("prod_rev", "Products from email ($)", lambda i, c: f"{c}{R['new']}*{g('welcome_conv')}*{g('net_order')}+{('0' if i == 0 else prev(i,'subs'))}*{g('campaign_conv')}*{g('sends')}*{g('net_order')}", "$#,##0", True)
        line("mkt_rev", "Etsy + Gumroad Discover ($)", lambda i, c: f"{g('market_orders')}*{c}{R['ramp']}*IF({c}$2=3,{g('jan_boost')},1)*{g('market_net')}", "$#,##0", True)
        line("aff_rev", "Affiliates ($)", lambda i, c: f"IF({c}$2>={g('aff_start')},{g('aff_clicks')}*{c}{R['ramp']}*{g('aff_conv')}*{g('aff_payout')},0)", "$#,##0", True)
        line("spon_rev", "Newsletter sponsors ($)", lambda i, c: f"IF({c}{R['subs']}>={g('spon_min')},{g('spon_place')}*{c}{R['subs']}/1000*{g('spon_per1k')},0)", "$#,##0", True)
        line("total", "TOTAL revenue ($)", lambda i, c: "+".join(f"{c}{R[k]}" for k, _ in STREAMS), "$#,##0", True, True)
        BLOCK[(b, case)] = R
        row = line.row + 1
# costs block per case
COSTROW = {}
for case in CASES:
    wm.cell(row, 1, f"Costs and net: {case} case").font = Font(bold=True, size=12, color="7A1F1F"); row += 1
    fixed = "+".join(inp(k, "Both", case) for k in ("c_domains", "c_api", "c_mailbox", "c_etsy"))
    subs_sum = lambda c: "+".join(f"{c}{BLOCK[(b, case)]['subs']}" for b in BRANDS)
    wm.cell(row, 1, "Costs ($)")
    for c in MC:
        wm[f"{c}{row}"] = f"={fixed}+IF(({subs_sum(c)})>2500,{inp('c_sender','Both',case)},0)"; wm[f"{c}{row}"].number_format = "$#,##0"
    wm[f"{TOT}{row}"] = f"=SUM(C{row}:N{row})"; wm[f"{TOT}{row}"].number_format = "$#,##0"
    crow = row; row += 1
    wm.cell(row, 1, "Revenue, both brands ($)")
    for c in MC + [TOT]:
        wm[f"{c}{row}"] = "=" + "+".join(f"{c}{BLOCK[(b, case)]['total']}" for b in BRANDS); wm[f"{c}{row}"].number_format = "$#,##0"
    rrow = row; row += 1
    wm.cell(row, 1, "NET ($)").font = bold
    for c in MC + [TOT]:
        wm[f"{c}{row}"] = f"={c}{rrow}-{c}{crow}"; wm[f"{c}{row}"].number_format = "$#,##0"; wm[f"{c}{row}"].font = bold
    COSTROW[case] = (crow, rrow, row); row += 2
wm.column_dimensions["A"].width = 42; wm.column_dimensions["B"].width = 2
for c in MC + [TOT]: wm.column_dimensions[c].width = 11
wm.freeze_panes = "C4"

# ---------------- Summary ----------------
ws = wb.create_sheet("Summary", 0)
ws.append(["Two-brand revenue model, Nov 2026 - Oct 2027 (Money Made Simple + Scam Decoded)"]); ws["A1"].font = Font(bold=True, size=14)
ws.append(["Organic only. Ad studio, B2B, 1099 Money and Dinero Simple are excluded. All figures after platform fees, before income tax. Edit the yellow cells on Inputs."])
ws.append([])
ws.append(["Year-1 revenue by stream", "", "Low", "Base", "High"])
for c in ws[4]: c.font = hdr; c.fill = hfill
r = 5
for b in BRANDS:
    ws.cell(r, 1, b).font = bold; r += 1
    for k, label in STREAMS + [("total", "Total")]:
        ws.cell(r, 1, "   " + label)
        for j, case in enumerate(CASES):
            cell = ws.cell(r, 3 + j, f"=Model!{TOT}{BLOCK[(b, case)][k]}"); cell.number_format = "$#,##0"
            if k == "total": cell.font = bold
        if k == "total": ws.cell(r, 1).font = bold
        r += 1
r += 1
for label, idx in (("Both brands: revenue", 1), ("Costs", 0), ("NET year 1", 2)):
    ws.cell(r, 1, label).font = bold
    for j, case in enumerate(CASES):
        cell = ws.cell(r, 3 + j, f"=Model!{TOT}{COSTROW[case][idx]}"); cell.number_format = "$#,##0"; cell.font = bold
    r += 1
r += 1
ws.cell(r, 1, "Month 12 (Oct 2027) run rate, both brands").font = bold
for j, case in enumerate(CASES):
    cell = ws.cell(r, 3 + j, f"=Model!N{COSTROW[case][2]}"); cell.number_format = "$#,##0"
r += 2
ws.cell(r, 1, "Platform gates: first month each case gets in (blank = not in year 1)").font = bold; r += 1
for b in BRANDS:
    for gate, key in (("YouTube Partner Program", "ypp"),):
        ws.cell(r, 1, f"   {b}: {gate}")
        for j, case in enumerate(CASES):
            R = BLOCK[(b, case)]
            rng = f"Model!C{R[key]}:N{R[key]}"
            ws.cell(r, 3 + j, f'=IFERROR(INDEX(Model!$C$3:$N$3,MATCH(1,{rng},0)),"-")')
        r += 1
    ws.cell(r, 1, f"   {b}: TikTok Creator Rewards paying")
    for j, case in enumerate(CASES):
        R = BLOCK[(b, case)]
        ws.cell(r, 3 + j, f'=IF(SUM(Model!C{R["tt_rev"]}:N{R["tt_rev"]})>0,"yes","-")')
    r += 1
    ws.cell(r, 1, f"   {b}: newsletter sponsors paying")
    for j, case in enumerate(CASES):
        R = BLOCK[(b, case)]
        ws.cell(r, 3 + j, f'=IF(SUM(Model!C{R["spon_rev"]}:N{R["spon_rev"]})>0,"yes","-")')
    r += 1
r += 1
notes = [
    "What the model says, honestly:",
    "1. Products and affiliates carry year 1. Platform payouts (YouTube, TikTok) are $0 in the low and base cases; only the high case clears the YPP and TikTok gates.",
    "2. YouTube's 2027 rule (8,000 watch hours for new applicants from 1 Feb 2027) keeps long-form ads out of reach unless long videos get real views.",
    "3. TikTok pays only at 10K followers + 100K views in 30 days, only on original videos over 1 minute, and not on fully AI videos. Our Shorts are under a minute.",
    "4. Instagram and Pinterest pay $0 directly at our size; they are traffic sources, counted through email, products and affiliates.",
    "5. Sponsors need a list of about 2,500. Only the high case gets there in year 1.",
    "Re-run with real numbers at day 30, 60 and 90 (growth-90-days-two-brands.md).",
]
for n in notes:
    ws.cell(r, 1, n); r += 1
ws.column_dimensions["A"].width = 60
for c in "CDE": ws.column_dimensions[c].width = 14

# ---------------- Thresholds & Sources ----------------
wt = wb.create_sheet("Thresholds")
wt.append(["Platform", "Programme", "What it takes (Nov 2026)", "What it pays", "In this model", "Source"])
for c in wt[1]: c.font = hdr; c.fill = hfill
for row_ in [
    ("YouTube", "YPP lower tier (fan funding, Shopping)", "500 subs, 3 uploads in 90 days, 3,000 watch hours or 3M Shorts views", "Memberships, Super Thanks, Shopping; no ad share", "Not modelled (small)", "YouTube Help; youtube-policy-review-nov-2026.md"),
    ("YouTube", "YPP full (ad revenue)", "1,000 subs + 4,000 hours to 31 Jan 2027; 8,000 hours or 20M Shorts views for new applicants from 1 Feb 2027", "55% of long-form ad revenue", "Yes: rows 'In YPP' and 'long-form ad revenue'", "YouTube Official Blog, 10 Aug 2026"),
    ("YouTube", "Shorts ad share", "10M qualified Shorts views in 90 days (from Feb 2027)", "45% of the Shorts pool share", "Yes, but no case reaches it", "same"),
    ("TikTok", "Creator Rewards", "18+, 10K followers, 100K views in 30 days, personal account, original videos over 1 minute; fully AI videos excluded", "~$0.50-2.00 per 1,000 qualified views (US, creator-reported)", "Yes", "ttcalculator.net (Jul 2026); tiktok-instagram-monetization.md"),
    ("Instagram", "Reels bonuses, Subscriptions, Gifts", "Bonuses invite-only; Subscriptions and Gifts need eligibility in the app", "Variable", "$0 (traffic only)", "tiktok-instagram-monetization.md"),
    ("Pinterest", "Creator payouts", "No open US pay-per-view programme found", "-", "$0 (traffic only)", "pinterest-playbook-2026.md"),
    ("Email", "Sponsors", "About 2,500 subscribers before a pitch is worth it", "~$7.11 per 1,000 subs per placement (Paved finance average)", "Yes", "newsletter-sponsorship-benchmarks.md"),
    ("Affiliates", "Impact, CJ, direct", "A live site with original content; some accept social-only creators", "Aura $65; NordVPN 40%; Keeper up to $50; bank bounties vary", "Yes, from month 3", "affiliate-answers-five-programs.md"),
]:
    wt.append(list(row_))
for col, w in zip("ABCDEF", (12, 34, 70, 42, 30, 50)): wt.column_dimensions[col].width = w
wsrc = wb.create_sheet("Sources")
wsrc.append(["Source", "Link"]); [setattr(c, "font", bold) for c in wsrc[1]]
for t, u in LINKS:
    wsrc.append([t, u])
    if u: wsrc.cell(wsrc.max_row, 2).hyperlink = u
wsrc.append([]); wsrc.append(["Source tags used on Inputs:"])
for k, v in SOURCES.items(): wsrc.append([k, v])
wsrc.column_dimensions["A"].width = 70; wsrc.column_dimensions["B"].width = 110
wb.save(OUT)
print("wrote", OUT)
