# Template line: Google Sheets + Notion

Template-only versions of the budget, debt payoff and savings tools, plus a free Notion starter that collects emails.
`SETUP.md` is the launch guide (links, Gumroad, Notion Marketplace).

| File | What it does |
|---|---|
| `sheets_templates.py` | Builds the three Google Sheets templates (.xlsx). The debt sheet reuses the payoff engine in `launch/products/sheets.py`. |
| `notion_spec.py` | The Notion templates as data: pages, databases, properties, formulas (with Python twins for previews), example rows. |
| `notion_build.py` | Builds a Notion template in your workspace through the Notion API (`--dry-run` to see the calls). |
| `catalog.py` | Names, prices and store copy for all nine products. |
| `previews.py` | Screenshots, covers and Start Here PDFs (HTML, rendered with Playwright). |
| `build_templates.py` | Builds everything into `dist/` (git-ignored). |
| `links.json` | The copy/duplicate links, filled in once the templates are published. |

    python launch/templates/build_templates.py
    pytest tests/test_templates.py
