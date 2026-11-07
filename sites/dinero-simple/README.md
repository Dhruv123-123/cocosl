# Dinero Simple: Spanish website, link-in-bio page and email funnel

> **Not ready to publish.** Every word here was machine-assisted Spanish. A fluent es-US speaker must read
> the whole site, the lead-magnet PDF and all 10 emails before the site goes live or the email automation
> is switched on. Use `launch/dinero-simple/REVIEW_CHECKLIST.md` (website and email sections).

The same generator as the English site (`site/build.py`), pointed at this folder:

```
SITE_ROOT=sites/dinero-simple python3 site/build.py            # writes sites/dinero-simple/public/
SITE_ROOT=sites/dinero-simple python3 site/build.py --serve    # preview on http://localhost:8080
```

| Path | What it is |
|---|---|
| `site.json` | Brand, URL, colours, email provider, lead magnet, pinned link-in-bio articles, and the `ui` block with every interface string in Spanish |
| `content/blog/` | 13 articles adapted from the English site (Spanish slugs and keywords, US terms kept in English and explained) |
| `content/products/` | El Presupuesto de 20 Minutos ($12) |
| `content/pages/` | Quiénes somos, Transparencia, Privacidad, Términos |
| `content/emails/` | 10-email welcome sequence over 21 days (same schedule as English) |
| `lead-magnet/` | "Tu dinero en orden en 7 días" (HTML source, 10 Letter pages) |
| `static/` | Images in the coral/teal palette and the lead-magnet PDF. CSS and JS are shared from `site/static/` |
| `tools/make_assets.py` | Re-renders the PDF, cover, product image and share image (Python Playwright) |
| `netlify.toml` | For a second Netlify site with Base directory `sites/dinero-simple` |
| `public/` | Built site, committed so it can be dragged onto Netlify Drop |

Pages: home, `/blog/` + 4 topic pages, 13 articles, `/products/`, the product page, `/free/` (lead magnet),
`/free/thanks/`, **`/links/` (link-in-bio page for @dinerosimple)**, about and legal pages, 404, sitemap, RSS,
and `/emails/` (unlinked, noindexed preview of the sequence, with copy-paste HTML and text per email).

## Before going live

1. Native-speaker review (see the checklist). Fix wording in the `.md` files and `site.json`, then rebuild.
2. Replace placeholders: `url`, `contact_email`, the Gumroad `buy_url`, social URLs, and add a postal address
   in your email provider (CAN-SPAM).
3. Point the email form at a **separate Spanish list** (`email.provider` / `email.action`), so Spanish subscribers
   get the Spanish sequence.
4. Set the brand's `link_in_bio` in `brands/dinero-simple.yaml` to `<url>/links/`.
5. Optional: once PR #8 is live, link the Spanish calculators (`/money-calculators/es/`) and scam checker.
