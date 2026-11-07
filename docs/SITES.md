# Running every brand's website from one builder

Status: plan (Nov 7, 2026). Nothing here refactors the brand branches; they're mid-merge. Do it in the
order below, one brand per PR, after PR #4 (Money Made Simple site) merges.

## Where things stand

| Brand | Where | How it's built | Pages | Notes |
|---|---|---|---|---|
| Money Made Simple | `site/` (PR #4) | `site/build.py`, stdlib Python, `site.json` + Markdown | Home, 32 articles, 8 comparisons, product, quiz, newsletter archive + RSS, start/resources, free/thanks, links, emails, legal | Plausible, deploy check (`site/tools/check_site.py`), `go-links.json` |
| Dinero Simple | `sites/dinero-simple/` (branch `claude/project-thread-qrazek`) | **A copy of `site/build.py`** with `SITE_ROOT`, a `ui` block of 87 Spanish strings, `colors` and `lang` | Same shape as MMS (13 articles, product, free, links, emails) | Its build.py edits also change `site/build.py`, so it conflicts with PR #4 |
| Scam Decoded | `sites/scam-decoded/` (branch `claude/project-thread-wa5csw`) | **Its own** `build.py` (same conventions, separate code) | Funnel only: landing, /checker/, kit sales page + product ladder, free/thanks, legal, 7 emails | `REPLACE_ME` placeholders are hidden and reported by the build |
| 1099 Money | `apps/freelance-tax/` (branch `claude/project-thread-7o0kyt`) | Hand-written HTML/JS, no build step; compare pages from `tools/build-pages.mjs` | Tax calculator (home), 5 comparisons, free/thanks, emails | Node tests + Playwright smoke; affiliate links in `config.js` |

Three builders and three config formats for four sites that share almost every feature (lead magnet,
email provider switch, emails export, legal pages, Plausible, affiliate slots, link-in-bio).

## Target

One generator, `site/build.py`, and one folder per brand:

```
site/                      # the generator + Money Made Simple (stays where it is; its folder is MMS)
  build.py  tools/check_site.py  tools/make_go_links.py  static/style.css  static/site.js
sites/
  dinero-simple/  site.json  content/  static/  lead-magnet/  netlify.toml
  scam-decoded/   site.json  content/  static/  lead-magnet/  netlify.toml
  1099-money/     site.json  content/  static/  lead-magnet/  netlify.toml   (+ the calculator as static files)
```

Build any brand with `SITE_ROOT=sites/<brand> python3 site/build.py`, then
`python3 site/tools/check_site.py --dir sites/<brand>/public`.

### What goes in each brand's `site.json`

The keys MMS already uses, plus Dinero's additions, merged into one schema:

| Key | Purpose | Comes from |
|---|---|---|
| `name`, `url`, `tagline`, `description`, `socials`, `contact_email` | Identity | all |
| `lang`, `ui` | Interface strings. English defaults live in the builder; a brand overrides any of them | Dinero |
| `colors` | Overrides the CSS `:root` variables (ink, paper, green, gold...) | Dinero |
| `pillars` | Blog topics; omit to turn the blog off | MMS |
| `email` | Provider switch: netlify, kit, mailerlite, buttondown, factory | all |
| `lead_magnet` | Title, file, pitch, days | all |
| `analytics.plausible_domain` | One Plausible site per brand | MMS (Dinero and Scam use top-level `plausible_domain`; accept both during migration) |
| `programs` + `go-links.json` | Affiliate slots; empty means an official link with no "sponsored" label | MMS (1099's `config.js` affiliates map 1:1) |
| `features` | Optional switches: `quiz`, `compare`, `resources`, `start`, `newsletter` (default: on if the content exists) | new |
| `blog_redirects`, `article_compare` | Retired slugs and cross-links | MMS |
| `placeholders_hidden` | Hide links containing `REPLACE_ME` and list them in the build output | Scam Decoded |

Features turn on when their content exists: `content/blog/` gives a blog, `content/compare/` gives
comparison pages, `content/products/` gives product pages, `content/quiz.json` gives the quiz,
`content/newsletter/` gives the archive. That lets Scam Decoded stay a funnel-only site without special code.

### Brand-specific pages

Anything one brand needs that the generator doesn't (Scam Decoded's `/checker/`, 1099's calculator) goes
in that brand's `static/` folder as plain HTML/JS, which the build copies as-is. The generator only needs
to inject the shared header, footer and analytics, via an `{{layout}}` marker or by wrapping
`static/*.page.html` files. No calculator code moves into Python.

## Migration, one PR per brand

1. **Merge PR #4** (MMS). It's the base the others copied.
2. **Dinero Simple:** port Dinero's builder changes (`SITE_ROOT`, `T()` strings with English defaults,
   `colors`, `lang`) into `site/build.py` as one PR, keeping MMS output byte-identical. Build both sites
   and diff `site/public/` before and after. Then delete the duplicate code on the Dinero branch.
3. **Scam Decoded:** move its pages into `content/pages/` and `static/checker/`, product ladder into
   `content/products/` (one file per rung), and delete `sites/scam-decoded/build.py`. The kit sales
   page becomes a product page with an extra `layout: sales` front-matter switch.
4. **1099 Money:** move the calculator (`index.html`, `app.js`, `lib/tax.js`, tests) to
   `sites/1099-money/static/` (served at `/calculator/` or `/`), the 5 comparisons from
   `tools/compare-data.mjs` to `content/compare/*.md`, emails to `content/emails/`, and `config.js`
   affiliates to `go-links.json`. Keep the Node tests for the tax maths; the site tests become the shared
   Python ones.
5. **Shared tests:** parametrise `tests/test_site.py` over every folder in `sites/` plus `site/`, so each brand
   gets the link checker, deploy check, SEO and Plausible tests for free.

Each step is shippable on its own; until a brand migrates, its current build keeps working.

## Deploy steps, per brand

Each brand is its own Netlify site from the same repo (free plan: unlimited sites, one build at a time).

| Brand | Netlify base directory | Default URL | Suggested domain | Plausible site | Email form name |
|---|---|---|---|---|---|
| Money Made Simple | repo root (`netlify.toml` points at `site/`) | moneymadesimple.netlify.app | moneymadesimple.co (or .com if free) | moneymadesimple.netlify.app, then the custom domain | `lead-magnet` |
| Dinero Simple | `sites/dinero-simple` | dinerosimple.netlify.app | dinerosimple.com / .co | dinerosimple.netlify.app | `lead-magnet` |
| Scam Decoded | `sites/scam-decoded` | scamdecoded.netlify.app | scamdecoded.com | scamdecoded.netlify.app | as set in its site.json |
| 1099 Money | `apps/freelance-tax` now, `sites/1099-money` after step 4 | 1099money.netlify.app | 1099money.co | 1099money.netlify.app | `tax-calendar` |

For each brand:

1. **Netlify site.** app.netlify.com > Add new site > Import an existing project > GitHub > `cocosl`.
   Set **Base directory** from the table (MMS needs none: the root `netlify.toml` already sets `base = "site"`).
   Deploy. Then Site configuration > Change site name to the default URL in the table.
2. **Forms.** Forms > Enable form detection, redeploy once. Set a notification or a Zapier/Make hook that
   adds new signups to the brand's email provider (or switch `email.provider` in its `site.json`).
3. **Domain (optional, ~$10-15/year).** Buy it at a registrar (Cloudflare, Porkbun, Namecheap), then
   Netlify > Domain management > Add a domain, and either point the registrar's nameservers at Netlify DNS
   or add the `CNAME` / `A` records Netlify shows. HTTPS is issued automatically. Then set the brand's
   `url` in `site.json` (Netlify's `URL` env var also covers it on Netlify builds).
4. **Plausible.** Add one site per domain with exactly the domain the site is served on
   (change it, or add the custom domain, when you move off `*.netlify.app`). Goals: `Product Click`,
   `Affiliate Click`, `Signup`, `Outbound Link: Click`, plus `Quiz Complete` for MMS. Custom properties:
   `brand`, `app`, `link`, `form`, `result`. Put the domain in the brand's `site.json`
   (`analytics.plausible_domain`), see `docs/UTM.md` section 3.
5. **Search.** Add the domain in Google Search Console and Bing Webmaster Tools and submit `/sitemap.xml`.
6. **Pinterest (MMS, Dinero).** Claim the domain in Pinterest business settings; rich pins then work from the
   page meta tags.
7. **Before going live,** run the deploy check and each brand's own pre-publish list: MMS
   `site/README.md` + `site/AFFILIATE_ARTICLES.md`; Dinero `launch/dinero-simple/REVIEW_CHECKLIST.md` (a fluent
   es-US reviewer must read everything); Scam Decoded `REPLACE_ME` report; 1099 Money tax-year figures.

GitHub Pages works for any one brand (`.github/workflows/pages.yml`, set `EMAIL_PROVIDER` since Netlify Forms
don't exist there), but one repo gets one Pages site, so Netlify is the practical choice for four brands.
