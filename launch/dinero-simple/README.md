# Dinero Simple: Spanish launch pack

The Spanish-language sister brand of Money Made Simple, for US Hispanic viewers. Brand file: `brands/dinero-simple.yaml` (`language: es`, `region: US`).

**Status: machine-adapted, not yet reviewed by a native speaker. Do not post until `REVIEW_CHECKLIST.md` is done.**

| Path | What |
|---|---|
| `content.json` | 14 Shorts + 8 carousels in Spanish, importable with `factory import launch/dinero-simple/content.json --brand dinero-simple` |
| `src/` | The Spanish copy (`shorts_*.py`, `carousels_*.py`) and the build scripts for content.json, the spreadsheet and the PDF |
| `product/` | El Presupuesto de 20 Minutos: guide (HTML + PDF), spreadsheet, store listing |
| `POSTING_PLAN.md` | 14-day plan, mirroring the English one |
| `REVIEW_CHECKLIST.md` | What the native-speaker reviewer checks, and the translation choices to confirm |

Rebuild everything after editing the Spanish:

```bash
python launch/dinero-simple/src/build_content.py
python launch/dinero-simple/src/build_xlsx.py
node launch/dinero-simple/src/render_pdf.js $PWD/launch/dinero-simple/product/el-presupuesto-de-20-minutos.html $PWD/launch/dinero-simple/product/El-Presupuesto-de-20-Minutos.pdf
factory pack launch/dinero-simple/content.json --brand dinero-simple --out output/dinero-simple-pack
```

Not adapted yet: the two long-form videos, the link-in-bio page, the email sequence and the website. Visual prompts, sources and fact-check lists stay in English on purpose so the operator can check them.
