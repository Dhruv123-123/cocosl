# Dinero Simple: Spanish launch pack

The Spanish-language sister brand of Money Made Simple, for US Hispanic viewers. Brand file: `brands/dinero-simple.yaml` (`language: es`, `region: US`).

**Status: machine-adapted, not yet reviewed by a native speaker. Do not post until `REVIEW_CHECKLIST.md` is done.**

| Path | What |
|---|---|
| `content.json` | 14 Shorts + 8 carousels in Spanish, importable with `factory import launch/dinero-simple/content.json --brand dinero-simple` |
| `src/` | The Spanish copy (`shorts_*.py`, `carousels_*.py`) and the build scripts for content.json, the spreadsheet and the PDF |
| `product/` | El Presupuesto de 20 Minutos: guide (HTML + PDF), spreadsheet, store listing |
| `POSTING_PLAN.md` | 14-day plan, mirroring the English one |
| `content-month-1.json`, `POSTING_PLAN_MONTH_1.md`, `REVIEW_CHECKLIST_MONTH_1.md` | Month 1 after launch (Nov 21 – Dec 31): 20 Shorts, 10 carousels, 2 long videos on the holidays, aguinaldo, sending money home, the cuesta de enero and New Year. Sources in `src/month1_*.py`, built by `src/build_month1.py` |
| `content-estafas.json`, `POSTING_PLAN_ESTAFAS.md`, `REVIEW_CHECKLIST_ESTAFAS.md` | Scam series (Jan 4 – Feb 16, 2027): 13 Shorts + 6 carousels. Some are adapted from Scam Decoded, and some are new on notario fraud, immigration impostors, remittance scams, money mules, virtual kidnapping and ghost tax preparers. Sources in `src/estafas_*.py`, built by `src/build_estafas.py` |
| `content-month-2.json`, `POSTING_PLAN_MONTH_2.md`, `REVIEW_CHECKLIST_MONTH_2.md` | Month 2 (January 2027): 14 Shorts, 8 carousels, 2 long videos on the December card bill, a debt list, the year's 'surprise' costs, cutting bills and the 2027 tax season (W-2, ITIN, VITA, refunds). Posts in the slots the scam series leaves free. Sources in `src/month2_*.py`, built by `src/build_month2.py` |
| `content-month-3.json`, `POSTING_PLAN_MONTH_3.md`, `REVIEW_CHECKLIST_MONTH_3.md` | Month 3 (February 2027): 14 Shorts, 8 carousels, 2 long videos on tax season with an ITIN: the first W-7, ITIN myths, documents, dependents, filing status, the refund in your own account, the IP PIN and tax identity theft, IRS letters, owing, and the W-4. Immigration questions go to a licensed attorney, never a notario. Sources in `src/month3_*.py`, built by `src/build_month3.py` |
| `content-month-4.json`, `POSTING_PLAN_MONTH_4.md`, `REVIEW_CHECKLIST_MONTH_4.md` | Month 4 (March 2027): 14 Shorts, 8 carousels and 2 long videos on credit from zero and banking without fees, with or without a Social Security number (ITIN credit, secured cards, builder loans, disputes, overdraft, bank vs credit union), plus the April 15 stretch. Sources are in `src/month4_*.py`, built by `src/build_month4.py` |
| `content-month-5.json`, `POSTING_PLAN_MONTH_5.md`, `REVIEW_CHECKLIST_MONTH_5.md` | Month 5 (April 2027): 14 Shorts, 8 carousels and 2 long videos on taxes for workers before April 15 (W-2 or 1099, cash, expenses, tips and overtime, two jobs, the ITIN deadline) and sending money home for less. Pieces that mention the ITIN carry an ATTORNEY REVIEW line. Sources in `src/month5_*.py`, built by `src/build_month5.py` |
| `content-holiday-2026.json`, `POSTING_PLAN_HOLIDAY_2026.md`, `REVIEW_CHECKLIST_HOLIDAY_2026.md` | Holiday pack, Nov 20 – Dec 31, 2026: 10 posts that rotate Shorts, TikTok mids (65–90 s), carousels and single images. They cover Black Friday traps, December remittance timing, the posada and the gift exchange, and WhatsApp scams, in slots month 1 leaves free. Sources are in `src/holiday_2026.py`, built by `src/build_holiday.py` |
| `NEWSLETTER.md`, `newsletter/issues/` | The weekly Spanish newsletter: 6 evergreen issues plus the 2026 holiday issue (#7), with no links in the body (`[ENLACE: ...]` placeholders), A/B subjects and review boxes. Sources in `newsletter/issues.py`, built by `newsletter/build_newsletter.py` |
| `src/originals.py` | The original element for every long video (a chart of its own numbers and a suggested screen recording). A new long video must be added here or its build fails |
| `ANSWER_BANK.md` | 30 Spanish answers for Quora and Facebook groups, with no links, plus posting rules. Sources in `community/answers.py`, built by `community/build_answers.py` |
| `workshops/` | Workshop kits for partner organizations: 'Que no te roben' and 'Tu presupuesto en 20 minutos' (see `workshops/README.md`) |
| `LINKS.md` | UTM-tagged profile links per platform and store links (`src/links.py`, rules from docs/UTM.md) |
| `products/` | Spanish editions of the $5 Bill Cut Kit (*El Kit para Recortar Gastos*) and the $17 Debt-Free Date Planner (*Tu Fecha Sin Deudas*): guides, translated workbooks, covers, listings. `python launch/dinero-simple/products/build.py --check` |
| `REVIEW_CHECKLIST.md` | What the native-speaker reviewer checks, and the translation choices to confirm |

Rebuild everything after editing the Spanish:

```bash
python launch/dinero-simple/src/build_content.py
python launch/dinero-simple/src/build_xlsx.py
node launch/dinero-simple/src/render_pdf.js $PWD/launch/dinero-simple/product/el-presupuesto-de-20-minutos.html $PWD/launch/dinero-simple/product/El-Presupuesto-de-20-Minutos.pdf
factory pack launch/dinero-simple/content.json --brand dinero-simple --out output/dinero-simple-pack
python launch/dinero-simple/src/build_month1.py
factory pack launch/dinero-simple/content-month-1.json --brand dinero-simple --out output/dinero-simple-month-1
python launch/dinero-simple/products/build.py --check
python launch/dinero-simple/src/build_estafas.py
python launch/dinero-simple/src/build_month2.py
```

Also adapted: the two long-form videos (`videos/23`, `videos/24`), and the website, link-in-bio page, lead magnet and 10-email sequence in `sites/dinero-simple/` (see its README). Visual prompts, sources and fact-check lists stay in English on purpose so the operator can check them.
