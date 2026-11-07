# Dinero Simple: Spanish website, link-in-bio page and email funnel

> **Not ready to publish.** Every word here was machine-assisted Spanish. A fluent es-US speaker must read
> the whole site, the lead-magnet PDF and all 10 emails before the site goes live or the email automation
> is switched on. Use `launch/dinero-simple/REVIEW_CHECKLIST.md` (website and email sections).

Built by this folder's own `build.py` (standard library only). It started as a copy of the English site's
generator in PR #4 and is kept separate so the two sites never conflict:

```
python3 sites/dinero-simple/build.py            # writes sites/dinero-simple/public/
python3 sites/dinero-simple/build.py --serve    # preview on http://localhost:8080
```

| Path | What it is |
|---|---|
| `build.py` | The generator: articles, products, pages, `/links/`, `/go/` redirects, emails, sitemap, RSS |
| `site.json` | Brand, URL, colours, email provider, lead magnet, pinned link-in-bio articles, and the `ui` block with every interface string in Spanish |
| `content/blog/` | 16 articles, mostly adapted from the English site (Spanish slugs and keywords, US terms kept in English and explained) |
| `content/products/` | Five products, $5 to $29 |
| `content/pages/` | Quiénes somos, Cómo ganamos dinero, Transparencia, Privacidad, Términos, the two calculators, and the glossary (built from `launch/dinero-simple/glossary/`) |
| `content/emails/` | 10-email welcome sequence over 21 days (same schedule as English) |
| `lead-magnet/` | "Tu dinero en orden en 7 días" (HTML source, 10 Letter pages) |
| `static/` | Images in the coral/teal palette and the lead-magnet PDF. plus `style.css` and `site.js` |
| `tools/make_assets.py` | Re-renders the PDF, cover, product image and share image (Python Playwright) |
| `netlify.toml` | For a second Netlify site with Base directory `sites/dinero-simple` |
| `public/` | Built site, committed so it can be dragged onto Netlify Drop |

Pages: home, `/blog/` + 4 topic pages, 16 articles, `/products/`, five product pages, `/free/` (lead magnet),
`/free/thanks/`, **`/links/` (link-in-bio page for @dinerosimple)**, about and legal pages, 404, sitemap, RSS,
and `/emails/` (unlinked, noindexed preview of the sequence, with copy-paste HTML and text per email).

## Before going live

1. Native-speaker review (see the checklist). Fix wording in the `.md` files and `site.json`, then rebuild.
2. Replace placeholders: `url`, `contact_email`, the five Gumroad `buy_url`s (in `content/products/`), social URLs, and add a postal address
   in your email provider (CAN-SPAM).
3. Point the email form at a **separate Spanish list** (`email.provider` / `email.action`), so Spanish subscribers
   get the Spanish sequence.
4. `link_in_bio` in `brands/dinero-simple.yaml` already points at `/links/`. For profiles, paste the per-platform UTM links from `launch/dinero-simple/LINKS.md`.
5. Once PR #8's apps are deployed, set `tool_urls.calculators` and `tool_urls.scam_checker` in `site.json`, then rebuild. For example: `https://YOUR-APPS-SITE/money-calculators/es` and `https://YOUR-APPS-SITE/scam-checker/es`. The 9 entries in `free_tools` cover the scam checker, link checker, scam guides and 6 calculators. They then appear on `/links/` ("Herramientas gratis"), on the home page, and as a box on matching articles. While those URLs still contain `REPLACE_ME`, nothing is shown.
6. Analytics: every page loads Plausible (`plausible_domain` in `site.json`, currently `dinerosimple.netlify.app`; set `plausible_host` if you self-host). Add the site in Plausible with the goals `Product Click`, `Affiliate Click`, `Signup` and `Outbound Link: Click`, and allow the custom properties `brand`, `link` and `form` (docs/UTM.md section 3, PR #8). Buy buttons send Product Click, affiliate links send Affiliate Click and the email forms send Signup. The exported welcome emails tag every link to the site with UTM (`utm_emails`).
