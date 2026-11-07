# Alerta de Estafas Semanal: Spanish edition (Plus tier)

The 4 credit union sample alerts in US Spanish, with the same formats, dates and brand slots as the
English edition. They are written in Dinero Simple's style, using **usted**.

**Status: machine-adapted, not reviewed by a native speaker. Don't send to any client until
`REVIEW_CHECKLIST.md` is done.**

| File | What |
|---|---|
| `product.json` | Spanish labels, call to action and disclaimer (`"lang": "es"`). |
| `issues.json` | The 4 issues in Spanish. Same ids and send dates as `../issues.json`. The staff brief stays in English. |
| `brands/example.json`, `brands/placeholders.json` | The fictional sample CU with a Spanish promise line and footer, plus the token-only version. |
| `samples/week-1.md` … `week-4.md` | Readable master copy of each issue (written by the build). |
| `REVIEW_CHECKLIST.md` | What the native reviewer checks, the choices to confirm, and the links to verify. |

Build (from `launch/b2b/`):

```bash
python3 build.py credit-union-alert/es
python3 build.py credit-union-alert/es --brand credit-union-alert/es/clients/<slug>.json
```

A client's Spanish brand file is their English one with `promise`, `footer_lines` and `unsubscribe`
in Spanish, and `slug` ending in `-es`.
