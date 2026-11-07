"""Build the three immigrant-money series for Spanish-first adults and recent arrivals (Mar 2 - Apr 17, 2027):

  "Mandar dinero a casa"       Tuesdays   content-envios-2027.json
  "Crédito sin Seguro Social"  Thursdays  content-credito-sin-ss-2027.json   (+ the lead magnet in credito/)
  "Alerta de estafa"           Saturdays  content-alertas-inmigrantes-2027.json

Each gets POSTING_PLAN_<NAME>.md and REVIEW_CHECKLIST_<NAME>.md. Tuesdays, Thursdays and Saturdays are free in months
4 and 5, so these never share a day with another Dinero Simple post (a test checks). Anything that mentions the ITIN
gets ATTORNEY REVIEW (flag_attorney); the scam alerts carry it on every immigration piece.

    python launch/dinero-simple/src/build_series_inmigrantes.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
sys.path.insert(0, str(HERE))

import series_alertas  # noqa: E402
import series_credito  # noqa: E402
import series_envios  # noqa: E402
from build_holiday import plan_rows, review_checklist  # noqa: E402
from build_month2 import build  # noqa: E402
from build_month6 import flag_attorney, mentions_itin  # noqa: E402


def _dates(days: list[str], keys: list[str], time: str = "12:30") -> list[tuple[str, str, str]]:
    assert len(days) == len(keys)
    return [(d, time, k) for d, k in zip(days, keys)]


SERIES = {
    "envios": dict(
        name="ENVIOS_2027", folder="envios-2027", source=series_envios,
        title="\"Mandar dinero a casa\" (Tuesdays, Mar 2 – Apr 6, 2027)",
        days=["mar 2 mar", "mar 9 mar", "mar 16 mar", "mar 23 mar", "mar 30 mar", "mar 6 abr"],
        why="The real cost of sending money home: the fee plus the exchange-rate markup, the 1% federal tax on cash-funded transfers, how to compare fairly and your rights. Every post sends people to the site's free calculator (`/calculadora-de-envios/`).",
        rules=["**Public pricing only.** Example numbers are round and labelled as examples. The monthly \"¿Cuánto llega?\" carousel is filled in by hand on posting day from each provider's public quote page, with a screenshot kept.",
               "**No provider is named or ranked** on screen or in captions: \"Opción A / B / C\".",
               "Repeat the \"¿Cuánto llega este mes?\" carousel monthly after this run, same amount, corridor and delivery method."],
        high_risk="the 1% remittance excise tax rules (cash, money order, cashier's check; exempt when funded from a US account or US-issued card), the CFPB 30-minute cancellation and 180-day error rights, and every [LLENAR] in the monthly carousel",
        note="Native-speaker review matters most for money words that vary by country (envío, giro, remesa, tipo de cambio)."),
    "credito": dict(
        name="CREDITO_SIN_SS_2027", folder="credito-sin-ss-2027", source=series_credito,
        title="\"Crédito sin Seguro Social\" (Thursdays, Mar 4 – Apr 15, 2027)",
        days=["jue 4 mar", "jue 11 mar", "jue 18 mar", "jue 25 mar", "jue 1 abr", "jue 8 abr", "jue 15 abr"],
        why="Six Shorts, one step each, from the ITIN to a growing credit history, then a summary carousel. Every post offers the free guide (lead magnet, `credito/`, also on the site at `/credito-sin-seguro-social/`).",
        rules=["**Every piece mentions the ITIN**, so every piece needs ATTORNEY REVIEW the week it posts, and a credit expert (HUD-approved housing counselor, NFCC counselor or credit union lender) checks the credit facts.",
               "**No bank, card or lender is named.** \"Una cooperativa de crédito o un prestamista comunitario\" is enough.",
               "Nothing promises approval or a score. The ITIN never appears as a path to work authorization or status."],
        high_risk="ITIN rules (W-7 options, 3-year expiry, no IRS fee), which products accept an ITIN (it varies by institution), and how ITIN holders can request free credit reports",
        note="Re-check before posting: some lenders change ITIN policies, and immigration-related rules can change quickly."),
    "alertas": dict(
        name="ALERTAS_INMIGRANTES_2027", folder="alertas-inmigrantes-2027", source=series_alertas,
        title="\"Alerta de estafa\" for immigrants (Saturdays, Mar 6 – Apr 17, 2027)",
        days=["sáb 6 mar", "sáb 13 mar", "sáb 20 mar", "sáb 27 mar", "sáb 3 abr", "sáb 10 abr", "sáb 17 abr"],
        why="Scams aimed at immigrants in the Scam Decoded style (PR #9): a calm hook with a number, the fake message as a made-up screenshot with numbered callouts on the red flags, what to do, and where to report. They add to the January scam series (`POSTING_PLAN_ESTAFAS.md`) without repeating it.",
        rules=["**Every example message, name, number and link is made up** and carries an \"EJEMPLO\" watermark. Check no slide shows a real phone number, domain or person.",
               "**No panic** (\"¡te van a deportar!\") and no real company or agency accused of anything.",
               "**Nothing reads like immigration legal advice.** People go to a licensed immigration attorney or a DOJ-accredited representative (EOIR roster), never a notario. Every immigration piece carries ATTORNEY REVIEW."],
        high_risk="the H-2A/H-2B recruitment-fee rule, how USCIS fees are paid, and that no example names a program whose status is in flux",
        note="If a program in the news changes the week a piece posts, swap the example rather than the rule."),
}


def posting_plan(cfg: dict, items: list[dict]) -> str:
    rows = plan_rows(items, _dates(cfg["days"], [i["key"] for i in items]))
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel")}
    n_itin = sum(1 for i in items if mentions_itin(i))
    rules = "\n".join(f"{n}. {r}" for n, r in enumerate(cfg["rules"], 1))
    return f"""# Dinero Simple: {cfg['title']}

For Spanish-first adults and recent arrivals: scouting's creator landscape (`research/scouting/dinero-simple-creator-landscape.md` on PR #2) found nobody in Spanish posts steadily on this, and that our packs leaned heavily on investing. {cfg['why']}

{len(items)} posts: {counts['short']} Shorts and {counts['carousel']} carousel(s), one a week on a day no other Dinero Simple plan uses. {n_itin} mention the ITIN and carry ATTORNEY REVIEW.

## Rules for this series

{rules}

Nothing goes out until a fluent Spanish speaker has signed off the piece (`REVIEW_CHECKLIST_{cfg['name']}.md`) and the facts under CHECK BEFORE POSTING are confirmed. Never name a bank, lender or remittance company on camera. Times America/New_York.

Source: `launch/dinero-simple/content-{cfg['folder']}.json`. Folder numbers match the rendered pack in project files `content-factory/dinero-simple/{cfg['folder']}/`.

| Day | Time | Platform(s) | Folder | Format | Pieza |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"


def main() -> None:
    for cfg in SERIES.values():
        items = flag_attorney(build(cfg["source"].ITEMS, {}))
        (DS / f"content-{cfg['folder']}.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
        (DS / f"POSTING_PLAN_{cfg['name']}.md").write_text(posting_plan(cfg, items))
        (DS / f"REVIEW_CHECKLIST_{cfg['name']}.md").write_text(
            review_checklist(items, cfg["title"], cfg["folder"], cfg["high_risk"], cfg["note"]))
        print(f"{cfg['folder']}: {len(items)} items")


if __name__ == "__main__":
    main()
