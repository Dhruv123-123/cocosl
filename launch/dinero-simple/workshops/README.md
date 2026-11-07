# Dinero Simple workshop kits

Ready-to-run workshops that partner organizations (parishes, community centers, consulate financial desks, ESL programs, credit unions) can give themselves. They're offered in the partner kit (project files `content-factory/dinero-simple/partners-b2b/`).

| Workshop | Length | Price in the offer | Based on |
|---|---|---|---|
| Que no te roben | 60 min | Always free | The scam series (`content-estafas.json`) |
| Tu presupuesto en 20 minutos | 75 min | Kit $99 (draft) | El Presupuesto de 20 Minutos (`../product/`) |

Each kit has editable slides with the facilitator script in the speaker notes (`.pptx`, plus `.pdf`), a facilitator guide (schedule, materials, rules, facts to check, script per slide) and two worksheets.

```
python launch/dinero-simple/workshops/build_workshops.py     # -> workshops/dist/<slug>/ and <slug>.zip
```

The content lives in `content_estafas.py` and `content_presupuesto.py`. Needs python-pptx, LibreOffice (slides to PDF) and Playwright (guide and worksheets to PDF); `--no-pdf` skips the last two.

**Everything is Spanish and machine-written. A native speaker reviews it before any organization uses it,** and the facilitator guide's "Verificar antes del taller" facts are checked the week of each workshop. The other three topics in the offer (recortar gastos, fecha sin deudas, empezar a invertir) and the tax-season workshop aren't built yet.
