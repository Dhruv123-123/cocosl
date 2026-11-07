# Scam Watch in Spanish: native review checklist

**Not ready for any client.** Issues 1 to 3 were adapted from English by AI, in the same style as the
credit union Spanish edition (`../../credit-union-alert/es/REVIEW_CHECKLIST.md`): **usted**, neutral
Latin American Spanish with a light Mexican-American lean, US agency names kept with Spanish
explanations. A fluent es-US speaker, ideally one who works with older adults, must read every word
before a library, senior center or sponsoring credit union sees it. Allow about 45 minutes for all 3.

The readers are older adults, many reading in print, so check above all that each sentence is short
and plain, with no anglicisms a 75-year-old reader would trip on.

## Choices to confirm

| Choice | Alternative |
|---|---|
| **usted** throughout, and the grandchild in the example uses **tú** with the grandmother ("no le digas a mi mamá") | Some families use usted with grandparents; change the example if that reads more naturally |
| "Línea contra el Fraude a Personas Mayores" for the National Elder Fraud Hotline | Keep the English name with a translation beside it, so callers recognize it |
| "tarjetas de regalo", "transferencia", "criptomonedas" | — |
| "carro", "celular", "boleto" | "coche", "móvil", "pasaje" for audiences that aren't Mexican-American |
| The group leader's 10-minute talk (`brief.txt`) stays in English | Translate it for a Spanish-speaking group leader |

## Facts to check (the Spanish adds two claims)

- [ ] **Issue 3 says Social Security (1-800-772-1213) and Medicare (1-800-633-4227) both serve callers in
      Spanish.** Confirm both on ssa.gov/espanol and medicare.gov/es.
- [ ] **Issue 2 sends people to ReporteFraude.ftc.gov** (the FTC's Spanish reporting site) and 1-877-382-4357.
      Open the site in a browser; it couldn't be opened from the build session.
- [ ] The Elder Fraud Hotline (1-833-372-8311): find out whether it offers help in Spanish. If it does,
      add "Atienden en español" to the footer in `product.json` here.
- [x] `https://www.ssa.gov/espanol/estafas/`: checked Nov 7 2026, Spanish page.
- [x] `https://consumidor.ftc.gov`: checked Nov 7 2026, Spanish page.

## Per issue

- [ ] **Mes 1. "Abuela, soy yo. Estoy en problemas."** Lobby headline and bullets, handout, poster, social, email.
- [ ] **Mes 2. Cuando un amor por internet necesita dinero.** Keep it kind, never blaming.
- [ ] **Mes 3. "Su número de Seguro Social ha sido suspendido."** The phone numbers must stay exactly as written.
- [ ] **The sponsored versions** (`out/sample-county-library-cu-sponsored-es/`): the credit union's
      sponsor line in Spanish. The NCUA insurance statement is kept in English, with a translation beside it.
      The sponsoring credit union's compliance officer decides whether that's acceptable.

## Sign-off

Set `"reviewed"` at the top of `issues.json` to the date and the reviewer's name, delete each issue's
`"review"` line, and rebuild: `cd launch/b2b && python3 build.py community-scam-watch/es`.
