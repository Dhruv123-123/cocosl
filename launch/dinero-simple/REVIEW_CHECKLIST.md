# Native-speaker review: Dinero Simple

**Nothing in this pack is ready to post until a fluent Spanish speaker (ideally US Hispanic, ideally someone who talks about money in Spanish every day) has read it and fixed it.** It was adapted from the English Money Made Simple pack by AI. It is meant to read like it was written in Spanish, not translated, but only a native speaker can confirm that.

Budget about 2 to 3 hours for everything, or 5 minutes per carousel/short plus 45 minutes for the guide. A paid reviewer on a freelance site is fine; ask for "localization review, US Hispanic audience, personal finance".

## How to sign off

- Edit the text, not the images: fix the Spanish in `launch/dinero-simple/src/*.py`, then rebuild with
  `python launch/dinero-simple/src/build_content.py` and `factory pack launch/dinero-simple/content.json --brand dinero-simple --out <folder>`.
- In the software, each post shows a `language_review` warning until you record the reviewer:
  `factory review-language <post id> --by "Reviewer name"`.
- Tick the box in each item's `caption.txt` ("A fluent es-US speaker has read every word...").

## Decisions the reviewer should confirm or overrule

| Choice made | Why | Alternatives |
|---|---|---|
| **tú**, never usted or vosotros | Young US audience, matches the brand voice | usted for an older audience |
| Neutral Latin American with a light Mexican-American lean: carro, súper, celular, llanta ponchada, departamento, recámara, cafecito, "sin rollos" | Largest share of US Hispanics | Caribbean/South American words if the audience skews that way |
| US product names kept in English: Roth IRA, 401(k), expense ratio, HYSA, match, vesting, target-date fund, glide path | That's what people search and what their bank/HR portal shows | Fully Spanish terms, e.g. "índice de gastos", "fondo con fecha objetivo" |
| "fondos de previsión" for sinking funds | Clear and short | "fondos de ahorro programado", "apartados" |
| "gastos fijos" for bills (the guide's Line 1) | Plain | "cuentas", "pagos fijos" |
| "cuenta de cheques" for checking | US Spanish usage | "cuenta corriente" (not US usage) |
| "puntaje de crédito", "fecha de corte", "fecha límite de pago", "burós de crédito" | Common in US Spanish banking | "puntuación de crédito", "agencias de crédito" |
| "avalancha" / "bola de nieve" | Literal names of the debt methods, used in Spanish finance content | — |
| Hashtags all Spanish plus a few English product tags (#rothira, #401k, #etfs) | Search behaviour is mixed | — |
| CTA: "Síguenos para un paso de dinero cada semana." | Mirrors "one money move a week" | "Síguenos: un consejo de dinero por semana." |

## Things added for this audience (check they land well)

- The guide: sending money to family counted as a fixed bill or a fund.
- Guide FAQ: a short, neutral note on tandas (no interest, no insurance, depends on trust).
- Short 14 and the guide: subscription searches use English words because US statements are in English.
- Guide: NFCC credit counsellors, noting many serve in Spanish (check before claiming for a specific agency).
- The example person is Daniela (Maya in English). Same numbers, so the spreadsheet matches.

## Pieces

- [ ] `videos/01` El truco de las dos cuentas que evita sobregiros  _(from: The two-account trick that stops overdrafts)_
- [ ] `videos/02` Haz tu presupuesto por semana, no por mes  _(from: Budget weekly, not monthly)_
- [ ] `videos/03` Tu dinero en una Roth IRA no está encerrado  _(from: Roth IRA money isn't locked away)_
- [ ] `videos/04` El aumento que estás ignorando: el match de tu 401(k)  _(from: The raise you're ignoring: your 401(k) match)_
- [ ] `videos/05` La comisión que se come $18,000  _(from: The fee that eats $18,000)_
- [ ] `videos/06` ¿Pagaste completo y tu puntaje bajó?  _(from: Paid in full, score still dropped?)_
- [ ] `videos/07` Congela tu crédito gratis esta noche  _(from: Freeze your credit for free tonight)_
- [ ] `videos/08` $60 contra $150 en una tarjeta de $3,000  _(from: $60 vs $150 on a $3,000 card)_
- [ ] `videos/09` ¿Tu app de ahorro de verdad está asegurada?  _(from: Is your savings app actually insured?)_
- [ ] `videos/10` Activa estas 3 alertas del banco hoy  _(from: Set these 3 bank alerts today)_
- [ ] `videos/11` Esa cuenta 'sorpresa' estaba en el calendario  _(from: That 'surprise' bill was on the calendar)_
- [ ] `videos/12` La opción de retiro de un solo fondo  _(from: The one-fund retirement option)_
- [ ] `videos/13` No canceles esa tarjeta vieja todavía  _(from: Don't cancel that old card yet)_
- [ ] `videos/14` Encuentra tus suscripciones olvidadas en 10 minutos  _(from: Find your forgotten subscriptions in 10 minutes)_
- [ ] `carousels/15` Tu cita mensual de 20 minutos con tu dinero  _(from: The 20-minute monthly money date)_
- [ ] `carousels/16` Fondo de emergencia de $1,000 en 8 semanas  _(from: $1,000 emergency fund in 8 weeks)_
- [ ] `carousels/17` ¿Roth o Traditional IRA? Una sola pregunta  _(from: Roth or Traditional IRA? One question)_
- [ ] `carousels/18` Qué tienes de verdad en un fondo índice  _(from: What you actually own in an index fund)_
- [ ] `carousels/19` Revisa tu reporte de crédito como auditor  _(from: Check your credit report like an auditor)_
- [ ] `carousels/20` Avalancha contra bola de nieve, con números reales  _(from: Avalanche vs snowball, with real math)_
- [ ] `carousels/21` App, hoja de cálculo o libreta  _(from: App vs spreadsheet vs notebook)_
- [ ] `carousels/22` Cómo abrir tu primera cuenta de inversión  _(from: Opening your first investment account)_
- [ ] Brand kit: bios (`brand-kit/bio-pack.txt`), banner tagline, highlight names (Presupuesto, Invertir, Crédito, Apps, Empieza aquí)
- [ ] Guide PDF, all 14 pages (`product/El-Presupuesto-de-20-Minutos.pdf`)
- [ ] Spreadsheet labels, dropdowns and status messages (`product/Presupuesto-20-Minutos-Plantilla.xlsx`)
- [ ] Store listing (`product/LISTING.md`)

## Facts to re-check (same as English, plus Spanish-only ones)

Every `caption.txt` lists its own facts under CHECK BEFORE POSTING. The Spanish pack adds three: the "statements are in English" claim (videos/14), the Spanish/English app menu names (videos/10) and whether to mention ITIN for brokerage accounts (carousels/22). The 2026 IRA limit ($7,500) and other numbers are unchanged from the English pack and need the same check.
