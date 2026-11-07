# Affiliate-keyword articles (20)

Twenty articles in `content/blog/` target high-intent searches ("best high yield savings account",
"rocket money review", "where to open a roth ira", and so on). They follow the same conventions as
the original 13: one keyword each, sources, a `## Common questions` FAQ, internal links and
`{{signup}}`. Each one sets `affiliate: yes`, so the site shows its affiliate notice at the top of
the article.

## How affiliate links work

Articles never contain a raw affiliate URL. They link to `/go/<slug>/`, and the site build marks
those links `rel="sponsored"`. Each `/go/` page is a tiny noindex redirect made from
`go-links.json`:

1. When a program approves you, paste the tracking link into that entry's `affiliate_url`.
2. Run `python3 site/tools/make_go_links.py` and commit. Every article that uses the link updates.

Until then, `/go/` pages send readers to the company's official page, so no article links to a
program you haven't joined. Leave UTM off affiliate links (docs/UTM.md): the network tracks them.

## Before publishing (human review)

- [ ] **Check every price, fee and rate against the company's page.** They were checked in
      Nov 2026 from published pages and reviews, but the build container couldn't open the sites.
      The ones that change most often: Rocket Money Premium range and negotiation fee, Monarch and
      YNAB prices, Betterment's $4/month rule, Acorns tiers, CIT's $5,000 tier, SoFi's APY
      conditions, FreeTaxUSA's state fee, Self's plans and fees, Aura's plans.
- [ ] Check the 2027 IRA limit once the IRS announces it, and update `where-to-open-a-roth-ira`.
- [ ] Check whether IRS Direct File is offered for the 2027 season (it wasn't for 2026).
- [ ] VITA and Free File income limits for the coming season.
- [ ] Articles marked `compliance: review` (investing: Empower, Betterment, robo-advisers, Acorns,
      Roth IRA, budgeting apps) need a check against FINRA 2210 / the SEC Marketing Rule before an
      affiliate link from a broker or adviser goes live. Several programs require script approval.
- [ ] Source URLs weren't link-checked; open each one.

None of the reviews claims we used the product. They say they're based on published terms. Keep
it that way unless someone really has used it.
