# Spanish edition: native review checklist

**Not ready for any client.** These 4 issues were adapted from the English samples by AI. They follow
Dinero Simple's style rules (`content-factory/dinero-simple/REVIEW_CHECKLIST.md`), with one deliberate
change, noted below. A fluent es-US speaker must read every word before a Plus client sees them.
Allow about 1 hour for all 4: about 10 minutes per issue (email, lobby, poster, social), plus checking
the links.

The Spanish edition is a **Plus-tier** feature ($149 a month). Don't promise it to a client until this
review is signed off and you have a reviewer you can use every week (see "Every week" below).

## Choices to confirm or overrule

| Choice | Why | Alternative |
|---|---|---|
| **usted**, not tú | Dinero Simple uses tú for a young social audience. Credit union members are all ages, and a financial institution writing to its members normally uses usted. Dinero Simple's own checklist names usted as the option for an older audience. | tú, if a client's Spanish marketing already uses it |
| Neutral Latin American Spanish with a light Mexican-American lean: celular, licencia de manejar, plática | Same as Dinero Simple: largest share of US Hispanics | Caribbean or South American wording for a client whose members skew that way |
| "código de un solo uso", "identificador de llamadas", "cuenta segura" (in quotes) | Plain and common in US bank Spanish | "código de verificación", "caller ID" |
| "transferencia" for wire | US Spanish banking usage | "giro", "transferencia bancaria" |
| "criptomonedas", spelled out | Dinero Simple avoids the slang "cripto"; here it's named as a scam payment, as in the Dinero Simple scam series | — |
| Lobby headline "Un trabajo real no le cobra por pagarle." | Shorter than a literal translation, under 8 words | "Un trabajo real nunca le pide pagar para cobrar." |
| Insurance line kept in English with a Spanish translation in brackets: "Federally insured by NCUA. (Asegurado federalmente por la NCUA.)" | NCUA rules (12 CFR 740) set the wording of the official advertising statement in English. **The client's compliance officer decides** whether the English statement must stay, and whether a translation can sit beside it. | Use whatever the client already uses in its Spanish materials |
| Staff huddle brief stays in English | It's for staff, not members | Translate it for a client with Spanish-speaking staff |

## Per issue

For each one: read the email (`email.html`), the lobby slide, the poster and the social caption and
alt text in `out/sample-community-cu-es/`.

- [ ] **Semana 1. La llamada falsa del departamento de fraudes.** Also check the promise line in the
      brand file (`brands/example.json`). It's the sentence most likely to be read word for word by
      a client's compliance team.
- [ ] **Semana 2. El trabajo que le pide que pague.** "Compensar" for a check clearing: confirm that's
      the word members will know, or use "hasta que el cheque se acredite".
- [ ] **Semana 3. El número equivocado que se vuelve una inversión.** The made-up example uses the name
      "Ana". Check that the tone of the opening message reads as natural.
- [ ] **Semana 4. El IRS no le manda mensajes de texto.** "PIN de Protección de Identidad" should
      match the IRS's own Spanish name for the IP PIN on irs.gov/es. Update it if it differs.

## Links

- [x] `https://www.irs.gov/es/identity-theft-central`: checked Nov 7 2026, Spanish page ("Central de robo de identidad").
- [x] `https://consumidor.ftc.gov`: checked Nov 7 2026, Spanish page.
- [ ] `https://reportefraude.ftc.gov` (the FTC's Spanish reporting site, used in issues 1 to 3): couldn't open it from
      this session. Open it in a browser. If it doesn't work, use `https://reportfraud.ftc.gov` and add "(en inglés)".
- [ ] The other sources are official English pages, labelled "(en inglés)". Swap any for an official
      Spanish version if one exists (the FTC and IRS publish many in Spanish), and drop the label.

## Sign-off

When every box is ticked, set `"reviewed"` at the top of `issues.json` to the date and the reviewer's
name, delete each issue's `"review"` line, and rebuild:
`cd launch/b2b && python3 build.py credit-union-alert/es`.

## Every week (once a Plus client signs)

`DELIVERY_WORKFLOW.md` → "Spanish edition": translate the finished English issue (AI-assisted is fine),
put it in this `issues.json`, and have the same reviewer read it **before day −7**. Budget 10 to 15
minutes of reviewer time a week. A freelance localization reviewer ("es-US, financial services") is
fine. Don't ship an unreviewed week; send the English edition alone and tell the client.
