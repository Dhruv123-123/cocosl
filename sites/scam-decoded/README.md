# Scam Decoded funnel site

Free lead magnet (**The Scam-Proof Checklist**, 2-page PDF) → landing page → 7-email sequence that sells
**The Family Scam-Proofing Kit** ($9). Same conventions as the Money Made Simple site (`site/`, PR #4):
standard-library `build.py`, settings in `site.json`, emails in `content/emails/*.md`, committed `public/`.

```bash
python3 sites/scam-decoded/build.py          # rebuild public/
python3 sites/scam-decoded/build.py --serve  # preview at http://localhost:8080/
```

| Page | What it does |
|---|---|
| `/` and `/free/` | Landing page with the checklist sign-up form |
| `/free/thanks/` | PDF download, scam checker link, soft kit pitch |
| `/kit/` | Sales page for the $9 kit (who it's for, who it isn't, 14-day refund) |
| `/checker/` | Sends people to the free scam checker (PR #8); "coming soon" until its URL is set |
| `/privacy/`, `/disclosures/`, `404.html` | Legal and fallback |
| `/emails/` | Private (noindex) preview of the sequence |

## Email sequence

| # | Day | Job |
|---|---|---|
| 1 | 0 | Deliver the checklist, set expectations |
| 2 | 1 | The 3 tells every scam shares |
| 3 | 3 | Credit freeze walk-through |
| 4 | 5 | Voice-clone calls and the family safe word |
| 5 | 7 | Main pitch for the $9 kit |
| 6 | 10 | The first-hour plan if it happens |
| 7 | 14 | FAQ + objections, last kit mention, hand-off to the weekly alert |

The build writes `public/emails/sequence.json` (subject, preheader, send day, HTML and text for each email)
plus `public/emails/<slug>/email.html` and `email.txt`, ready to paste into MailerLite, Kit or Buttondown.
Email links are absolute (they use `url` / `SITE_URL`).

## Before launch (the build warns about each)

1. `product.buy_url`: the real Gumroad/Payhip link for the kit.
2. `scam_checker.url`: the deployed checker from PR #8 (or set `SCAM_CHECKER_URL`). Until then the site hides
   the checker box and emails point to `/checker/`.
3. `email.provider` + `email.action`: `netlify` works with zero setup; `mailerlite`, `kit`, `buttondown`
   or `factory` need the form action (or set `EMAIL_PROVIDER` / `EMAIL_FORM_ACTION`).
4. `contact_email` and `url` (or `SITE_URL`).
5. Set the email tool to send the 7 emails on days 0, 1, 3, 5, 7, 10, 14 after sign-up.
6. Analytics: every page loads Plausible (`script.outbound-links.tagged-events.js`, see `docs/UTM.md`
   section 3). The domain is `analytics.plausible_domain` in `site.json` (or `PLAUSIBLE_DOMAIN`; set it
   empty to build without analytics, `PLAUSIBLE_SRC` for a self-hosted script). Buy buttons send
   `Product Click` and affiliate links (any `affiliates[].url` used in page text) send `Affiliate Click`
   with `rel="sponsored"`. Add both goals in Plausible. Outbound links, like the checker, are counted
   automatically. Email bodies carry no script.
