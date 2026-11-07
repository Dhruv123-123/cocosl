# Affiliate application kit

`python3 launch/affiliates/kit.py` builds:

- `APPLICATIONS.md`: a pre-application checklist, reusable answers for all four brands
  (short and long descriptions within common form limits, audience, promotion methods, methods we
  don't use, compliance statement), network sign-up notes (Impact, CJ, FlexOffers, PartnerStack),
  and a section for each of 31 programs with its own "why us" and "how we'll promote it".
- `applications.html`: the same answers with Copy buttons.
- `applications.csv`: a tracker with one row per program and brand.

Program data is in `programs.json`; brand answers are in `kit.py`. Nothing is submitted. Fill in
the [BRACKETS] with real analytics only. Payout figures come from the Nov 2026 research
(`research/02-affiliate-programs.md`) and must be confirmed in each dashboard.

When a program approves you, paste the tracking link into `site/go-links.json` on the site (see
`site/AFFILIATE_ARTICLES.md`).
