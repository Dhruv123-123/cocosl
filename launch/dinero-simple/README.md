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
| `content-newyear-2027.json`, `POSTING_PLAN_NEWYEAR_2027.md`, `REVIEW_CHECKLIST_NEWYEAR_2027.md` | New Year pack, January 2027: 8 posts in slots month 2 and the scam series leave free. Covers propósitos, the January money reset, the pay stub line by line, and which tax form arrives for each kind of work. Formats rotate mid, image, carousel, Short. Sources in `src/newyear_2027.py`, built by `src/build_newyear.py` |
| `content-month-6.json`, `POSTING_PLAN_MONTH_6.md`, `REVIEW_CHECKLIST_MONTH_6.md` | Month 6 (May 2027): 14 Shorts, 8 carousels and 2 long videos on Mother's Day remittances and gifts, medical bills and medical debt, buying a used car, teens' first jobs, the trip home, the kids' summer, the summer electric bill and the rent deposit. Sources in `src/month6_*.py`, built by `src/build_month6.py` |
| `WHATSAPP_CHANNEL.md` | WhatsApp Channel kit: setup, name and description, posting rules, growing it by hand, and 30 days of messages (with polls). Links appear only as `[ENLACE: ...]` placeholders. Sources in `whatsapp/messages.py`, built by `whatsapp/build_whatsapp.py` |
| `content-reto-ahorro-2026.json`, `POSTING_PLAN_RETO_AHORRO_2026.md`, `REVIEW_CHECKLIST_RETO_AHORRO_2026.md` | "Reto de diciembre: $10 al día" (Nov 30 – Dec 28, 2026): a 7-post savings challenge done with the viewer (day 1, a tracker, Sunday check-ins, a finale), in free slots next to month 1 and the holiday pack. Numbers are examples, never promises. Sources in `src/reto_ahorro_2026.py`, built by `src/build_reto.py` |
| `GLOSSARY_REVIEW.md` | Review checklist for the site's 50-term glossary (`/glosario/`), built from `glossary/terms.py` by `glossary/build_glossary.py` |
| `content-month-7.json`, `POSTING_PLAN_MONTH_7.md`, `REVIEW_CHECKLIST_MONTH_7.md` | Month 7 (June 2027): 14 shorts, 8 carousels and 2 long videos ("Tu sueldo completo", "Seguro de vida") on unpaid wages and overtime, insurance, a mid-year check and Father's Day without debt. Sources in `src/month7_*.py`, built by `src/build_month7.py` |
| `content-month-8.json`, `POSTING_PLAN_MONTH_8.md`, `REVIEW_CHECKLIST_MONTH_8.md` | Month 8 (July 2027): 14 shorts, 8 carousels and 2 long videos ("La tanda", "Tu primera casa"). 6 pieces mention the ITIN and carry ATTORNEY REVIEW. Sources in `src/month8_*.py`, built by `src/build_month8.py` |
| `content-month-9.json`, `POSTING_PLAN_MONTH_9.md`, `REVIEW_CHECKLIST_MONTH_9.md` | Month 9 (August 2027), "Tu primer año": money basics for recent arrivals, then renting safely. 14 shorts, 8 carousels and 2 long videos ("Tu primer año en Estados Unidos", "Rentar sin que te roben"). 3 pieces mention the ITIN and carry ATTORNEY REVIEW; the 8 renting pieces carry a LEGAL CHECK claim. Sources in `src/month9_*.py`, built by `src/build_month9.py` |
| `content-month-10.json`, `POSTING_PLAN_MONTH_10.md`, `REVIEW_CHECKLIST_MONTH_10.md` | Month 10 (September 2027), "Tu familia, aquí y allá": Labor Day rights at work, helping family without going broke, a family emergency plan, retirement when you start late. 14 shorts, 8 carousels and 2 long videos ("Ayudar a tu familia sin quedarte sin nada", "Tu retiro aunque empieces tarde"). 9 pieces mention the ITIN or immigration status and carry ATTORNEY REVIEW. Sources in `src/month10_*.py`, built by `src/build_month10.py` |
| `GUIA_IMPUESTOS_2027.md`, `REVIEW_CHECKLIST_IMPUESTOS_2027.md` | "Temporada de impuestos 2027": a free family guide for filing tax year 2026 with an ITIN or a W-2 (12 sections and a one-page checklist), with a printable PDF. Every ITIN section is flagged ATTORNEY REVIEW; a tax pro checks every figure. Source `impuestos/guia.py`, built by `impuestos/build_guia.py --pdf` (PDF lands in the gitignored `impuestos/dist/`) |
| `REVIEW_CHECKLIST_MAYORES.md` | "Estafas: guía para papás y abuelos": the Spanish large-print edition of the Scam Decoded seniors pack (15-page booklet, fridge list, wallet cards), with the notario, detained-relative, virtual-kidnapping and remittance-code scams added. Source `mayores/contenido.py`, built by `mayores/build_mayores.py --pdf` |
| `primer-ano/` | "Tu primer año en Estados Unidos": a 19-page printable Spanish workbook for recent arrivals (companion to month 9), **Gumroad only** at [PRICE] (Etsy bans AI-generated functional guides). `build_cuaderno.py --pdf` writes the PDF, `GUMROAD.md` and `REVIEW_CHECKLIST_PRIMER_ANO.md` |
| `imprimibles/` | Three **Etsy-safe** Spanish printables (labels only, no instructions): Registro de Cuentas y Pagos (7 pp), Retos de Ahorro (6 pp), Registro de Renta y Reparaciones (6 pp), each with LISTING.md and cover.png, price [PRICE]. They complement PR #6's El Presupuesto Familiar and El Registro de Envíos. `build_imprimibles.py --pdf` |
| `review/` | The hand-off review packets (native Spanish, immigration attorney), full and lean, with hour estimates: `build_packets.py --pdf`, summary in `review/REVIEW_PACKETS.md` |
| `lean/` | **Start here.** The lean launch: the only phase-1 set (core site, freebie, 5 welcome emails, the Kit, the bill tracker, 14 posts over 4 weeks). `lean_launch.py` writes `content-lean.json`, `POSTING_PLAN_LEAN.md`, the site hold, the PHASE 2 banners and the review-gate tags. Run it again after any month builder. See `lean/LEAN_LAUNCH.md` |
| `src/safe_lines.py` | The standard "consult a lawyer, free help here" lines (with official links) that the attorney approves once |
| `content-envios-2027.json`, `POSTING_PLAN_ENVIOS_2027.md`, `REVIEW_CHECKLIST_ENVIOS_2027.md` | "Mandar dinero a casa" (Tuesdays, Mar 2 – Apr 6, 2027): 6 posts on the real cost of sending money home (fee + exchange-rate markup, the 1% cash tax, comparing fairly, your CFPB rights) and a monthly "¿Cuánto llega?" template filled from public prices on posting day. No provider named or ranked. Sources `src/series_envios.py` |
| `content-credito-sin-ss-2027.json`, `POSTING_PLAN_CREDITO_SIN_SS_2027.md`, `REVIEW_CHECKLIST_CREDITO_SIN_SS_2027.md` | "Crédito sin Seguro Social" (Thursdays, Mar 4 – Apr 15, 2027): 6 Shorts from the ITIN to a growing credit history, plus a summary carousel; ATTORNEY REVIEW and CREDIT EXPERT REVIEW on every piece. Sources `src/series_credito.py` |
| `GUIA_CREDITO_SIN_SS.md`, `REVIEW_CHECKLIST_CREDITO_SIN_SS_GUIA.md` | The series' lead magnet: a 10-section guide with a one-page checklist, a PDF (`/downloads/credito-sin-seguro-social.pdf`) and the site page `/credito-sin-seguro-social/`. Source `credito/guia.py`, built by `credito/build_credito.py --pdf` (it reuses the tax guide's renderer) |
| `content-alertas-inmigrantes-2027.json`, `POSTING_PLAN_ALERTAS_INMIGRANTES_2027.md`, `REVIEW_CHECKLIST_ALERTAS_INMIGRANTES_2027.md` | "Alerta de estafa" (Saturdays, Mar 6 – Apr 17, 2027): 7 scam alerts aimed at immigrants in the Scam Decoded style (fake immigration call, paid free forms, visa job fees, fake lawyers, look-alike .gov sites, advance-fee loans, 7 signs), on top of the January series. Sources `src/series_alertas.py`; all three built by `src/build_series_inmigrantes.py` |
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
factory handoff-pack launch/dinero-simple/content.json --brand dinero-simple --out output/dinero-simple-pack
python launch/dinero-simple/src/build_month1.py
factory handoff-pack launch/dinero-simple/content-month-1.json --brand dinero-simple --out output/dinero-simple-month-1
python launch/dinero-simple/products/build.py --check
python launch/dinero-simple/src/build_estafas.py
python launch/dinero-simple/src/build_month2.py
python launch/dinero-simple/impuestos/build_guia.py --pdf
python launch/dinero-simple/mayores/build_mayores.py --pdf
python launch/dinero-simple/src/build_series_inmigrantes.py
python launch/dinero-simple/credito/build_credito.py --pdf
```

Also adapted: the two long-form videos (`videos/23`, `videos/24`), and the website, link-in-bio page, lead magnet and 10-email sequence in `sites/dinero-simple/` (see its README). Visual prompts, sources and fact-check lists stay in English on purpose so the operator can check them.
