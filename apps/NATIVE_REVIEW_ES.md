# Spanish pages: native review list

Every Spanish page and app on the tools site, for a fluent Spanish speaker to check before it's promoted. Nothing
here has been reviewed by a native speaker yet. The Spanish was written for US Spanish speakers: "tú", US money words
(cheque de pago, tarjeta de crédito, renta), and the IRS's own Spanish terms where they exist.

Do the **first three** first: they are the most-used tools and the ones Dinero Simple links to.

`shared/test/native-review.test.js` fails if a Spanish page is added without a row here.

## How to review

1. Open the page, use it once with real-looking numbers, and read every message it shows, including results and errors.
2. Check: natural wording, the same "tú" form throughout, money and tax terms a US Spanish speaker would recognise, no
   English left over, numbers and dates in a familiar format.
3. Write corrections next to the row (or in a copy of this file): the wrong text, the better text, and the page.
4. Mark the row ✅ when done. Text lives in the files in the last column; send the corrections and they get applied there.

## Priority: the three most-used tools

| # | Page | What to try | Text lives in | Status |
|---|---|---|---|---|
| 1 | `money-calculators/es/tax-refund/` (reembolso de impuestos) | Single, $45,000 W-2, $4,200 withheld, 1 child. Then head of household, tips and overtime. | `money-calculators/pages-es.mjs` (page), `lib/text-extra.js` EXTRA.es `refund` (results) | needs review |
| 2 | `money-calculators/es/debt-payoff/` (pagar deudas, with the payoff chart) | Two cards ($3,000 at 24%, $1,200 at 29%), $250 a month; compare avalanche and snowball; read the chart labels. | `pages-es.mjs`, `lib/text-extra.js` EXTRA.es `debtChart` | needs review |
| 3 | `budget/reto-ahorro.html` (reto de 52 semanas) | Try each style, tick a few weeks, download the calendar file, print. | `budget/reto-ahorro.html`, `budget/savings-challenge.js` (the `es` text block) | needs review |

## Everything else

| Page | Text lives in | Status |
|---|---|---|
| `es/index.html` (hub) | `tools/build-es-hub.mjs` | needs review |
| `es/apps.html` (instala las apps) | `tools/build-apps-page.mjs` (the `es` text block) | needs review |
| `budget/bill-calendar/es.html` (calendario de pagos) | `es.html`, `budget/bill-calendar/app.js` (`es` text), `manifest-es.webmanifest` | needs review |
| `budget/tablero-dinero.html` (tablero de dinero) | `tablero-dinero.html`, `budget/money-dashboard.js`, `budget/lib/dashboard.js` (category names, sheet text) | needs review |
| `money-calculators/es/index.html` | `money-calculators/pages-es.mjs` | needs review |
| `money-calculators/es/take-home-pay/` | `pages-es.mjs`, `lib/text-extra.js` | needs review |
| `money-calculators/es/emergency-fund/` | `pages-es.mjs`, `lib/text-extra.js` | needs review |
| `money-calculators/es/compound-interest/` | `pages-es.mjs` | needs review |
| `money-calculators/es/savings-interest/` | `pages-es.mjs` | needs review |
| `money-calculators/es/credit-card-minimum/` | `pages-es.mjs` | needs review |
| `money-calculators/es/roth-vs-traditional/` | `pages-es.mjs` | needs review |
| `money-calculators/es/student-loans/` | `pages-es.mjs` | needs review |
| `money-calculators/es/rent-vs-buy/` | `pages-es.mjs` | needs review |
| `money-calculators/es/401k-fees/` | `pages-es.mjs` | needs review |
| `money-calculators/es/remittance-cost/` (envíos de dinero) | `pages-es.mjs`, `lib/text-extra.js` EXTRA.es `rf`, `remit` | needs review |
| `money-calculators/es/gracias/` | `pages-es.mjs` | needs review |
| `scam-checker/es/index.html` (¿es una estafa?) | `scam-checker/` i18n (`lib/i18n.js`) | needs review |
| `scam-checker/es/enlace/` | `scam-checker/lib/i18n.js` | needs review |
| `scam-checker/es/thanks.html` | the page | needs review |
| `scam-checker/es/estafas/index.html` | `scam-checker/scams-es.mjs` (built by `scam-checker/build.mjs`) | needs review |
| `scam-checker/es/estafas/alerta-de-fraude-bancaria-falsa/` | `scam-checker/scams-es.mjs` | needs review |
| `scam-checker/es/estafas/correo-falso-de-renovacion/` | `scam-checker/scams-es.mjs` | needs review |
| `scam-checker/es/estafas/estafa-amazon/` | `scam-checker/scams-es.mjs` | needs review |
| `scam-checker/es/estafas/estafa-codigo-de-verificacion/` | `scam-checker/scams-es.mjs` | needs review |
| `scam-checker/es/estafas/estafa-de-empleo-por-mensaje/` | `scam-checker/scams-es.mjs` | needs review |
| `scam-checker/es/estafas/estafa-de-premios/` | `scam-checker/scams-es.mjs` | needs review |
| `scam-checker/es/estafas/estafa-irs/` | `scam-checker/scams-es.mjs` | needs review |
| `scam-checker/es/estafas/estafa-paypal/` | `scam-checker/scams-es.mjs` | needs review |
| `scam-checker/es/estafas/estafa-seguro-social/` | `scam-checker/scams-es.mjs` | needs review |
| `scam-checker/es/estafas/mensaje-numero-equivocado/` | `scam-checker/scams-es.mjs` | needs review |
| `scam-checker/es/estafas/mensaje-peaje-sin-pagar/` | `scam-checker/scams-es.mjs` | needs review |
| `scam-checker/es/estafas/mensaje-usps-falso/` | `scam-checker/scams-es.mjs` | needs review |

Also Spanish, outside the site: the Tablero de dinero Pro spreadsheet and its Empieza aquí PDF
(`launch/dashboard-pro/text.py`, `listing.py`), and the Scam Decoded extension's Spanish messages
(`scam-extension/_locales/es/`).
