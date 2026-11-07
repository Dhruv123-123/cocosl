# Alerta de Estafas: Scam Watch in Spanish

The first 3 Scam Watch issues in US Spanish (usted, large print), in every format: large-print handout,
flyer, screen slide, Facebook post and email. **Machine-adapted and not yet reviewed by a native
speaker: see `REVIEW_CHECKLIST.md` before anyone outside sees it.**

Two ways it's sold:

- **Library add-on:** a Spanish edition for libraries and senior centers that serve Spanish speakers.
  A suggested price is in `../README.md`; it's a proposal.
- **Credit-union-sponsored sites:** the $99-a-month sponsor tier can run in Spanish, English or both.
  `brands/cu-sponsored.json` is a fictional sample: Sample County Library, sponsored by the fictional
  Sample Community Credit Union, with the sponsor line in Spanish on every format.

| File | What |
|---|---|
| `product.json` | Spanish labels, call to action and disclaimer (`"lang": "es"`). |
| `issues.json` | Issues 1 to 3 in Spanish. Same ids and dates as `../issues.json`. The group leader's talk stays in English. |
| `brands/example.json` | The fictional library, with its help line in Spanish. |
| `brands/cu-sponsored.json` | The same library, sponsored by the fictional credit union. |
| `brands/placeholders.json` | Every brand slot shown as a token. |
| `REVIEW_CHECKLIST.md` | What the native reviewer checks, plus 3 facts to confirm. |

Build from `launch/b2b/` with `python3 build.py community-scam-watch/es` (plain `python3 build.py` builds it too).
