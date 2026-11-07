# Analytics and UTM conventions

One set of rules for every link in bios, pins, posts, videos and newsletters, across all four
brands, so Plausible and the owner dashboard can say which channel brought each visit, click
and sale.

## 1. The three values

Every link that points at one of **our own sites or apps**, or at a **Gumroad or Stripe
checkout**, carries three UTM params. Lowercase, words joined with `-`.

| Param | Means | Values |
|---|---|---|
| `utm_source` | The platform the link sits on | `instagram` `tiktok` `youtube` `pinterest` `x` `threads` `facebook` `newsletter` `linkpage`, an app's name (`money-calculators`, `scam-checker`, `budget`, `ad-script-builder`), `embed` |
| `utm_medium` | What kind of placement | `bio` (profile link), `social` (a post, pin, video, thread), `email` (newsletter or welcome sequence), `app` (a button inside one of our apps), `referral` (someone else's site, e.g. an embedded calculator), `paid` (ads) |
| `utm_campaign` | Which piece of content | see the patterns below |
| `utm_content` | Optional: which link in that piece | `cta-top`, `ps`, `button` |

The brand isn't in the UTM: the site's domain already says which brand it is.

### Campaign patterns

| Placement | `utm_campaign` | Example |
|---|---|---|
| Profile bio | `profile` | `?utm_source=tiktok&utm_medium=bio&utm_campaign=profile` |
| Pin | `pin-<article>-<n>` or the pin's id | `pin-emergency-fund-3` |
| Post, video, thread | the content id from the posting plan | `month-1-d14`, `evergreen-003` |
| Newsletter issue | `newsletter-<nn>` | `newsletter-01` |
| Welcome sequence | `welcome-d<day>` | `welcome-d6` |
| App button | the page | `debt-payoff`, `checker` |

These match what the factory already writes (`funnel/attribution.py`, the newsletter and
link-page builders, and `channels.py` for pins, threads and newsletters), so nothing already
generated needs renaming.

### What never gets UTM

- **Affiliate links.** The network tracks those itself and some break with extra params. In the
  apps they're marked `rel="sponsored"` and counted with the "Affiliate Click" event instead.
- Links to other people's sites (FTC, IRS, sources).

### Stripe Payment Links

Stripe drops `utm_*` at checkout, so a Stripe link also gets
`client_reference_id=<source>__<medium>__<campaign>`. The Stripe webhook and the owner
dashboard read it back. Both the factory and `apps/shared/track.js` add it for you.

## 2. Tools

From `apps/`:

```bash
node tools/utm.mjs bios                  # bio link for every brand x platform (paste into profiles)
node tools/utm.mjs link https://me.gumroad.com/l/kit --source pinterest --medium social --campaign pin-kit-1
node tools/utm.mjs check path/to/pins.csv path/to/newsletter/*.txt   # lists our links with no UTM
node tools/utm.mjs tag path/to/file.md --source x --medium social --campaign month-1-d3 --write
```

`check` exits 1 when it finds an untagged link, so it can run in CI. `tag` only touches our
own links and checkout links, never overrides UTM already present, and only prints unless you
pass `--write`. Brand sites live in `apps/tools/brands.json`.

## 3. Plausible

Plausible counts visits without cookies, so there's no cookie banner. It's a paid service
(there's a free trial) or free if self-hosted.

1. Add one Plausible site per domain: `moneymadesimple.netlify.app`, `scamdecoded.netlify.app`,
   `dinerosimple.netlify.app`, `1099money.netlify.app`, plus each app domain you deploy
   (e.g. `scamshield.netlify.app`). If several apps share one Netlify site, that's one domain.
2. In each site's settings add these **goals** (custom events): `Affiliate Click`,
   `Product Click`, `Signup`, and `Outbound Link: Click`.
3. Under **Custom properties** allow `brand`, `app`, `link`, `form`.
4. Apps: set `analytics.plausibleDomain` in each app's `config.js`. Self-hosting? Also set
   `plausibleHost`.
5. Static sites (the brand sites, link pages): put this in every page's `<head>`:

   ```html
   <script defer data-domain="moneymadesimple.netlify.app" src="https://plausible.io/js/script.outbound-links.tagged-events.js"></script>
   ```

   and mark buy buttons and affiliate buttons so they send the same events as the apps:

   ```html
   <a href="https://me.gumroad.com/l/kit?utm_source=linkpage&utm_medium=bio&utm_campaign=kit" class="plausible-event-name=Product+Click">Get the kit</a>
   <a href="https://partner.example/..." rel="sponsored" class="plausible-event-name=Affiliate+Click">See plans</a>
   ```
6. Owner dashboard: add the Plausible API key and `plausible.sites` in `owner.yaml`
   (see `docs/OWNER_DASHBOARD.md`).

Plausible reads `utm_source`/`utm_medium`/`utm_campaign` off the landing URL by itself and
shows them under Sources and Campaigns.

## 4. What the apps do (apps/shared/track.js)

Once `plausibleDomain` is set, every app page:

- loads Plausible's outbound-links script (page views + every outbound click);
- sends **Affiliate Click** for `rel="sponsored"` links, **Product Click** for Gumroad/Stripe
  links and **Signup** for email forms, each with `brand`, `app` and `link`/`form` props;
- tags Gumroad/Stripe links at click time with the **visit's own UTM** (kept for the browser
  session), so a sale from a pin that landed on a calculator is credited to the pin. With no
  UTM on the visit it uses `utm_source=<app>&utm_medium=app&utm_campaign=<page>`;
- tags the "Free calculator by ..." credit on embedded calculators with
  `utm_source=embed&utm_medium=referral`.

Nothing the person types (budgets, pasted messages, links being checked) is ever sent.
`track.js` is copied into each app's `lib/` by `node tools/sync-shared.mjs`; a test fails if a
copy is out of date.

## 5. Channels in reports

| UTM | Channel |
|---|---|
| source is a social platform | that platform (`pinterest`, `tiktok`, ...) |
| medium `email`, or source `newsletter` | email |
| medium `app` | apps |
| source `linkpage` | link page |
| medium `referral` or source `embed` | referral |
| medium `paid` | paid |
| no UTM | direct |

(`channelFor()` in `apps/tools/utm.mjs`.)
