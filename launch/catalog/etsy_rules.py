"""Etsy's 22 Oct 2026 rule on AI-generated functional guides, applied to the whole catalog.

Etsy now bans "AI-generated functional guides": patterns, recipes or instructions, "where the information buyers rely
on must be the seller's own work" (Etsy Seller Handbook, 22 Oct 2026; scouting's
research/scouting/ai-disclosure-rules-nov-2026.md on PR #2). Etsy's examples are crafts and recipes and it hasn't said
whether money guides count, so we take the safe reading: our guides and guide kits honestly say AI helped draft them,
so they're sold on Gumroad (and the sites) only. Etsy keeps printables, planners, trackers, cards, posters and their
bundles. A guide can go back on Etsy only if Dhruv rewrites it so it really is his own work.

`apply()` rewrites the catalog rows: an Etsy edition of a guide is dropped when the same product is on Gumroad, set to
"On hold" when it's Etsy-only (another thread decides), and "Etsy + Gumroad" becomes "Gumroad". `problems()` fails
the build if any guide is still on Etsy, or an Etsy row's name looks like a guide or kit and isn't on the allow list.
"""
from __future__ import annotations

import re

RULE = ("Etsy's 22 Oct 2026 rule bans AI-generated functional guides (instructions buyers rely on must be the seller's own "
        "work), so this guide is sold on Gumroad only.")
HOLD = "On hold (Etsy edition withdrawn: AI-guide rule)"

# (brand, product) -> the thread that decides. "this" = PR #6, already moved.
GUIDES = {
    ("Money Made Simple", "The Bill Cut Kit"): "this",
    ("Money Made Simple", "The 20-Minute Budget"): "this",
    ("Money Made Simple", "The Credit Report Audit Kit"): "this",
    ("Money Made Simple", "The Debt-Free Date Planner"): "this",
    ("Money Made Simple", "Start Investing With $100 a Month"): "this",
    ("Money Made Simple", "The Money Made Simple Toolkit"): "this",
    ("Money Made Simple", "The Money Reset: 30-Day Challenge Workbook"): "this",
    ("1099 Money", "Schedule C Setup Pack for TaxHacker"): "this",
    ("Dinero Simple", "La Lista para Construir tu Crédito"): "this",
    ("Dinero Simple", "El Paquete de la Familia"): "this",
    ("Scam Decoded", "Scam Decoded for Seniors (large print)"): "PR #9 (Scam Decoded), moved Nov 7",
    ("Scam Decoded", "Scam-Proof Your Parents printable kit"): "PR #9 (Scam Decoded), Gumroad from the start",
    ("1099 Money", "The Rate & Contract Kit"): "PR #10 (1099 Money)",
    ("1099 Money", "The Freelancer Money Bundle"): "PR #10 (1099 Money)",
    ("Dinero Simple", "El Kit para Recortar Gastos"): "PR #11 (Dinero Simple)",
    ("Dinero Simple", "El Presupuesto de 20 Minutos"): "PR #11 (Dinero Simple)",
    ("Dinero Simple", "Tu Fecha Sin Deudas"): "PR #11 (Dinero Simple)",
    ("Dinero Simple", "Empieza a Invertir con $100 al Mes"): "PR #11 (Dinero Simple)",
    ("Dinero Simple", "El Paquete Dinero Simple"): "PR #11 (Dinero Simple)",
}
# Kept on Etsy: trackers, planners and cards, checked one by one. (product -> why it isn't a guide)
ALLOWED = {
    "Scam Decoded Card Set": "Reference cards (safe word, call-back rule, phone numbers), not a guide.",
    "The Quarterly Tax Tracker": "A spreadsheet tracker. If PR #10's Etsy edition ships a how-to PDF, drop the PDF from Etsy.",
    "El Registro de Envíos": "A send log and spreadsheet; its two fact pages are short reference, not instructions.",
}
GUIDE_WORDS = re.compile(r"\b(guide|guía|kit|workbook|course|curso|lista para)\b", re.I)


def _no_etsy(platform: str) -> str:
    return re.sub(r"\s*\(Etsy optional\)|Etsy \+ |\s*\+ Etsy", "", platform).strip()


def apply(rows: list[dict]) -> list[dict]:
    on_gumroad = {(r["brand"], r["product"]) for r in rows if "Gumroad" in r["platform"]}
    out = []
    for r in rows:
        key = (r["brand"], r["product"])
        if key in GUIDES and "Etsy" in r["platform"]:
            who = GUIDES[key]
            note = RULE + ("" if who == "this" else f" {who}'s thread decides.")
            if r["platform"] == "Etsy":
                if key in on_gumroad:
                    continue  # the Gumroad row stays; the Etsy edition is withdrawn
                r = dict(r, platform=HOLD)
            else:
                r = dict(r, platform=_no_etsy(r["platform"]))
            r["notes"] = (note + " " + r["notes"]).strip()
        out.append(r)
    return out


def problems(rows: list[dict]) -> list[str]:
    bad = []
    for r in rows:
        if "Etsy" not in r["platform"] or r["platform"].startswith("On hold"):
            continue
        if (r["brand"], r["product"]) in GUIDES:
            bad.append(f"{r['brand']}: '{r['product']}' is a guide and is still on Etsy ({r['platform']})")
        elif GUIDE_WORDS.search(r["product"]) and r["product"] not in ALLOWED:
            bad.append(f"{r['brand']}: '{r['product']}' looks like a guide or kit on Etsy; add it to GUIDES or ALLOWED")
    return bad


def markdown(rows: list[dict]) -> str:
    out = ["## Etsy: guides moved to Gumroad (AI-guide rule, Oct 22 2026)\n",
           "Etsy now bans AI-generated functional guides. Ours say AI helped draft them, so every guide and guide kit is "
           "sold on Gumroad only, and Etsy keeps printables, planners, trackers, cards and posters. Source: scouting's "
           "`research/scouting/ai-disclosure-rules-nov-2026.md` (PR #2). To put a guide back on Etsy, Dhruv rewrites it as "
           "his own work first.\n",
           "| Brand | Guide | Now | Who decides |\n|---|---|---|---|"]
    plat = {}
    for r in rows:
        plat.setdefault((r["brand"], r["product"]), []).append(r["platform"])
    for (b, p), who in GUIDES.items():
        out.append(f"| {b} | {p} | {', '.join(dict.fromkeys(plat.get((b, p), ['not in catalog'])))} | "
                   f"{'Done on PR #6' if who == 'this' else who} |")
    out.append("\n**Kept on Etsy after a check:** " + " ".join(f"{p}: {w}" for p, w in ALLOWED.items()))
    return "\n".join(out) + "\n"
