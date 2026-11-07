# Money Made Simple website: start here

This is the short version: what to set up once, which blanks to fill in, and when the site deploys. The
full reference is [`README.md`](README.md), and the launch order across all brands is `docs/GO_LIVE.md`.

The site is static. `site/build.py` turns `site/content/` into `site/public/`, and Netlify serves `public/`.
Nothing runs on a server.

## 1. Netlify setup (about 20 minutes, once)

1. **Create the site.** In Netlify, go to Add new site > Import from Git and pick `cocosl`. Leave every
   build field as it is: the repo's `netlify.toml` already sets base `site`, command
   `python3 build.py && python3 tools/check_site.py`, publish `public` and Python 3.12. The production
   branch is `main`.
2. **Name it.** Go to Site configuration > Site details > Change site name and use `moneymadesimple`, so
   the address is `https://moneymadesimple.netlify.app`. That address is in `site/site.json` > `url`. If you
   pick another name or a custom domain, change `url` there too. The build also reads Netlify's own `URL`.
3. **Turn on forms.** Go to Forms > Enable form detection. Until Sender is connected (see the blanks
   below), every signup lands in Netlify Forms under `lead-magnet` with a `source` field, so nobody is
   lost.
4. **Add the scheduled rebuild.** Go to Site configuration > Build & deploy > Build hooks > Add build hook
   (name it "scheduled"). Copy the URL. In GitHub, go to repo Settings > Secrets and variables > Actions >
   New repository secret, and save it as `NETLIFY_BUILD_HOOK`. Without it, articles dated in the future
   never appear, because Netlify only builds on a push.
5. **Check it.** Open the site, then `/sitemap.xml` and `/blog/`. The deploy log ends with
   `N pages checked: 0 errors`. Warnings are fine, and errors fail the deploy on purpose.

## 2. The blanks to fill in

The site builds and works with all of these empty. Each one stays hidden or falls back to something
safe until it's filled in.

| What | Where | Until it's filled in |
|---|---|---|
| Editor's real name and bio | `site.json` > `editor` (set `placeholder` to false) | The build prints a warning, and article schema names the site instead of a person |
| Contact email | `site.json` > `contact_email` (now `hello@example.com`) | The corrections note and the shop's refund lines show the example address. **Fill this in before launch.** |
| Email provider (Sender) | `site.json` > `email`: `provider`, `action`, `email_field` | Signups go to Netlify Forms. Move them to Sender by hand, or the welcome email won't send |
| Money Basics course form | `content/money-basics.md` > `sender_form` (now `REPLACE_ME`) | The page uses the normal signup form with source `money-basics-7-days` |
| Course emails in Sender | `factory sequence-export money-made-simple --sequence money-basics --for sender`, then turn the automation on in Sender | Course signups get the welcome sequence only |
| Search Console and Bing | `site.json` > `search_verification` > `google`, `bing` (the meta tag's content value) | No verification tag |
| Store links | `site.json` > `stores` > `gumroad`, `etsy` (now example and `REPLACE_ME`) and each item's `url` and `etsy_url` in `content/shop.json` | Shop buttons point at the placeholders. **Fill this in before launch.** |
| Affiliate links | `go-links.json` > each program's `affiliate_url`, then `python3 site/tools/make_go_links.py` | `/go/<slug>/` sends people to the company's normal page, with no commission |
| Free tools site | `site.json` > `apps_url` (now `https://mms-tools.netlify.app`, PR #8) | If the apps site isn't live, empty this: embedded calculators and tool cards hide themselves |
| Analytics | `site.json` > `analytics` (Plausible domain is already set) | Add the site in Plausible, or empty `plausible_domain` to turn it off |
| Sister sites on the homepage | `site.json` > `launch_stage` (now `two-brand`) and `sister_brands` | Only Scam Decoded shows. Set `launch_stage` to `brand-3` when GO_LIVE's five week-8 gates pass (around Jan 10 2027), and 1099 Money appears. Dinero Simple also needs `show: true` |
| "Email me this plan" box | `site.json` > `plan_optin` | It shows under every calculator, with source `plan-<tool>`. Set `enabled` to false to hide it. Keep the copy the same as `apps/shared/optin.js` |
| B2B pages | `site/static/business/` (PR #13) | Copied as-is. Pages with `noindex` stay out of the sitemap |

`python3 site/tools/check_site.py` after a local build lists the remaining warnings.

## 3. Deploy schedule

- **Pushes to `main` that touch `site/`** deploy straight away. Other pushes are skipped by `netlify.toml`'s
  `ignore` rule.
- **The scheduled rebuild** (`.github/workflows/netlify-rebuild.yml`) runs every day at 13:00 UTC, but
  only calls the build hook when `site/tools/due_today.py` finds something going live that day: an
  article, newsletter issue, comparison page, a landing page's `live:` date, or the Nov 1 and Jan 1
  homepage season flips.
- **What that costs:** each production deploy uses 15 of the free plan's 300 credits a month. The current
  schedule needs 8 to 13 scheduled deploys a month (13 in Nov and Dec 2026, about 8 a month from Feb to
  Aug 2027, 69 in 2027 in total), which is 120 to 195 credits. That leaves room for roughly 7 to 12 pushes
  a month. Batch your content changes into fewer pushes.
- **To deploy by hand:** go to GitHub > Actions > Website (scheduled Netlify rebuild) > Run workflow. It
  always deploys.
- **To check a day:** `python3 site/tools/due_today.py 2027-04-06` prints what goes live. To preview
  the whole site as of a date, use `BUILD_DATE=2027-04-06 python3 site/build.py`. To see every scheduled
  article, use `BLOG_SHOW_SCHEDULED=1`.
- **The articles are scheduled through Aug 26 2027.** After that, the rebuild stops finding anything
  due until new dated content is added.

## 4. Before each push

```
python3 site/build.py && python3 site/tools/check_site.py
python3 -m pytest -q tests        # from the repo root
```
