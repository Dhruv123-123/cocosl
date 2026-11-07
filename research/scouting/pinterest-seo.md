# Pinterest and Google search: what works, the AI rules, and an audit of the Money Made Simple site

Researched 2026-11-07. Google's own Search Central pages are the primary source for the search rules.
Pinterest facts come from TechCrunch and Tailwind (a Pinterest scheduling partner). The site audit was
measured on the built site from PR #4 (branch `claude/project-thread-yrzol5`, commit `f5a22d5`).

## TL;DR

1. **The salary and debt-payoff pages are the site's biggest search risk.** 30 of the 55 data-driven
   pages share about 99% of their wording with a sibling page; only the numbers change. The numbers are
   real and useful, but Google judges "many pages... no matter how it's created". Merge them down and
   give each surviving page something of its own (fixes below).
2. **The 32 articles and 8 comparisons are fine on originality** (66-82% of each page's wording is unique
   to it) and already do what Google asks: sources, a human review line, honest "how we review" notes.
   Two things to change: all 40 are dated the same day, and 12 are titled "review" but are based on
   published features rather than testing.
3. **Pinterest suits this niche well, but only with fresh pins.** That means 1-3 new pin designs a
   day, standard pins with a link (video pins get more impressions but far fewer clicks), and rich pins,
   which the site already supports. Pinterest labels AI images "AI modified" from metadata and
   classifiers, and lets viewers see fewer of them in some categories. Finance isn't one of the named
   categories, and there's no evidence that labelled pins are pushed down otherwise.
4. **Get a real domain before investing in search.** The site is on `moneymadesimple.netlify.app`, and
   anything that builds up there (links, Pinterest domain claim, Search Console history) doesn't move with
   a later domain change.

## 1. Google's rules (as of November 2026)

| Rule | What Google says | Source |
|---|---|---|
| **Scaled content abuse** | "Many pages are generated for the primary purpose of manipulating search rankings and not helping users... large amounts of unoriginal content that provides little to no value to users, **no matter how it's created**." Examples: generative AI making many pages "without adding value"; scraping or auto-translating; stitching pages together; "many pages where the content makes little or no sense to a reader but contains search keywords". If you host it, "exclude it from Search" | [Spam policies, updated 28 Aug 2026](https://developers.google.com/search/docs/essentials/spam-policies) |
| **Thin affiliation** | Affiliate pages with descriptions "copied directly from the original merchant without any original content". Good affiliate pages offer "additional information about price, original product reviews, rigorous testing and ratings, navigation of products or categories, and product comparisons" | same |
| **Using AI** | Fine "when researching a topic, and to add structure to original content". Using it to "generate many pages without adding value for users may violate" the scaled-content policy. "Manually factcheck and review all AI-generated content", including titles, meta descriptions, structured data and alt text. Consider saying how content was made. Ecommerce AI images need IPTC `DigitalSourceType: TrainedAlgorithmicMedia` metadata | [Using generative AI content, updated 1 Oct 2026](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content) |
| **Timeline** | Scaled-content policy introduced 5 Mar 2024; raters given a scaled-content section in Jan 2025; spam policies page revised 28 Aug 2026; a spam update started 24 Sep 2026; manual fact-check guidance for AI content added 1 Oct 2026 | [PPC Land](https://ppc.land/scaled-content-abuse/) |

## 2. Audit of the Money Made Simple site (PR #4)

### How it was measured

I extracted each page's main text from `site/public/`, dropped the digits, and compared every page
against the others in its section using 5-word sequences. "Unique share" is the fraction of a page's
5-word sequences that appear on no other page in that section. Dropping the digits is deliberate: it
shows how much of the *wording* is the same once the numbers are set aside, which is what a template
check looks at.

| Section | Pages | Words (median) | Wording shared with the closest sibling | Unique share (median) | Verdict |
|---|---|---|---|---|---|
| `/budget/<salary>-salary/` | 20 | 955 | median 81%, up to **100%** (e.g. $75k vs $80k, $130k vs $200k) | **1%** | **High risk** |
| `/debt-payoff/<amount>-debt/` | 10 | 724 | median 81%, up to 99% | **1%** | **High risk** |
| `/cost-of-living/<city>/` | 25 | 707 | median 65%, up to 75% | 16% | Medium |
| `/blog/` (32 articles + 4 topic pages) | 36 | 880 | median 8%, highest 21% (Ally vs CIT reviews) | 66% | Low |
| `/compare/` | 8 | 909 | about 10% | 82% | Low |

Re-run it any time with `python research/scouting/site_audit.py site/public budget cost-of-living
debt-payoff blog compare` after building the site. The 4 tiny `/blog/` pages (12-15 words, skipped by the
script) are old URLs that redirect to `/compare/`, with `noindex` and a
canonical tag. That's correct.

### What's good already

- **The numbers are real and checkable.** Every salary page computes federal, state and city tax from
  `content/data/tax_rules.json` and compares HUD rents from `cities.json`. That's "additional
  information" a reader can't get from the template alone, which is the defence against "little to no value".
- **Each page has a short band-specific paragraph** (e.g. at $75k, "the risk shifts... to lifestyle creep").
- **Trust signals Google asks for:** a sources list on every article, a "Reviewed by a human editor"
  line, an About page that says how AI is used ("A human chooses every topic, checks every number... and
  approves each article"), affiliate links labelled and routed through `/go/`, a disclosures page.
- **Honest review notes:** `aura-review.md` says "We haven't been paid for this review and haven't
  tested the service." That's true, and better than pretending.

### Risks, most important first

1. **Near-duplicate salary and debt pages.** 30 pages whose wording is 99% shared with a sibling is
   the textbook pattern of a template filled from a spreadsheet. The value is in the numbers, but 20
   salary bands, several only $5k apart, is more pages than readers need.
2. **"Review" titles without testing.** 12 posts are called "review" (`acorns-review`, `aura-review`,
   `ynab-review`...) but say they're based on published features and pricing (5 of them also say plainly
   that we didn't test the product). Google contrasts thin affiliate pages
   with "original product reviews, rigorous testing and ratings". The honesty note protects trust, but
   the title promises something the page doesn't do.
3. **All 40 articles and comparisons carry the same date (2026-11-07)**, and all of them plus 55 data
   pages go live at once on a new site. Publishing ~100 URLs on day one isn't against a rule, but it's
   what a scaled site looks like from outside.
4. **The author is the organisation.** Article JSON-LD says `"author": {"@type": "Organization"}`. For
   money topics, a named, real editor with a short, truthful bio (no invented credentials) is stronger.
5. **"Reviewed by a human editor" has to stay true.** Google's 1 Oct 2026 guidance asks for a manual fact-check of
   AI content, titles and metadata included. If that line is printed on pages nobody reviewed, it
   turns a strength into a liability.

### Fixes

1. **Merge the salary pages from 20 to 8 bands** ($30k, $40k, $50k, $60k, $75k, $100k, $150k, $200k), and
   301-redirect the rest to the nearest band. Keep the calculator (`/budget/`) for any exact number. Give
   each surviving page one section of its own: a worked example at that income (rent and car choices,
   for instance) written by hand, not by template.
2. **Merge the 10 debt-payoff pages into one calculator page** with three worked examples ($5k, $15k,
   $30k), and redirect the others to it. 99% shared wording across 10 pages is the clearest risk on the site.
3. **City pages:** keep all 25 (16% unique, real HUD data), but add one local fact to each that the
   template can't produce: the state's renter credit, the city tax, or the transit pass price, with a source.
4. **Rename the untested "reviews"**, e.g. "YNAB: what you get, what it costs, and who should pay". Or
   actually test them: sign up for the free trials and add screenshots and what happened. Then "review"
   is earned.
5. **Stagger publishing.** Give the blog the same future-date rule the newsletter already has
   (`build.py` only publishes issues dated on or before the build date). Release 3-5 articles a week, and
   set `date` to the real publish day.
6. **Name the editor.** Add a person page (`/about/editor/`) and point article `author` to it. Only true
   statements; no credentials we don't have.
7. **Pages that can't be improved:** set `noindex` rather than delete them, as Google suggests ("exclude
   it from Search").

These are all site changes on the PR #4 branch, so they're for the site thread to make. This file only
records the audit.

## 3. Pinterest

### What works now

| Topic | Finding | Source |
|---|---|---|
| **Fresh pins** | "1-3 Fresh Pins daily" for creators with a content system; new accounts 3-5 a week. A fresh pin includes a "new image design, even for existing blog content". Repeating the same image and title "can trigger spam filters"; keep repins under 30% of activity, and the same pin on at most 10 boards, 2-3 days apart | [Tailwind](https://www.tailwindapp.com/blog/pinterest-posting-frequency/amp?p=13593) (2025, a Pinterest marketing partner) |
| **Standard vs video pins** | Video ("Idea") pins: ~3x more impressions, 45% more saves, but far fewer outbound clicks. Standard pins: 2.5x higher click-through to the website | [TryMyPost, 29 Apr 2026](https://www.trymypost.com/blog/pinterest-idea-pins-vs-standard-pins-strategy-2026) (a scheduler's blog; treat the ratios as directional) |
| **Rich pins** | The site already emits Open Graph `article:*` and `product:*` tags plus `pinterest-rich-pin`; claim the domain in Pinterest and rich pins apply automatically | `site/README.md` (PR #4) |

**For finance, in practice:** the pins that fit our content are tall (2:3, 1000×1500) standard pins with a
link to one article or calculator. Pin types: the checklist (the 7-Day Reset), the worked number ("$75k
salary: $5,133 a month take-home"), and before/after comparisons (avalanche vs snowball: $106). That
last part is our judgement from the carousel evidence in `instagram-formats.md`, not a Pinterest
study. Video pins are for reach; standard pins are for traffic. Use standard for most.

**Cadence for us:** start at one fresh pin a day per brand (new accounts are told 3-5 a week, so
start there for two weeks), each a new design for an existing URL. The salary, city and calculator pages
can each carry several pin designs, which is a far better use of them than more near-duplicate pages.

### AI pins

- Since 30 Apr 2025, Pinterest shows an **"AI modified"** tag on close-up image pins. It reads image
  metadata and runs its own classifiers for images without markers. Creators can appeal wrong labels.
- Viewers get a **"see fewer"** option on AI pins in categories prone to it, named as **beauty and art**,
  with more categories later. Choosing it tells Pinterest to show *that viewer* less AI content. Pinterest
  didn't say the label itself reduces distribution.
  ([TechCrunch](https://techcrunch.com/2025/04/30/pinterest-launches-new-tools-to-fight-ai-slop))

**What this means for us:** text-and-chart pins drawn by our own renderer (`media/carousel.py`,
`media/charts.py`) aren't AI-generated images, so they shouldn't be labelled. Pins using FLUX or
ComfyUI art may be, from embedded metadata, and that's fine. Don't strip the metadata to dodge the label.
Google asks for IPTC `TrainedAlgorithmicMedia` on AI images, and stripping it would contradict our own
disclosure rules.

### How to post

The factory has no Pinterest publisher. Two options: Postiz (already the factory's scheduler path,
`publish/postiz.py`; check that its Pinterest provider is enabled on your instance), or Pinterest API v5
directly, which needs an approved app. A 2:3 pin is one more layout for `media/carousel.py`: a single
tall slide with the headline, one number, and the brand.

## Open questions

- Does Dhruv want to merge the salary and debt pages (fixes 1-2)? It removes 22 URLs, and the site
  thread should do it before the site is submitted to Search Console.
- Which custom domain should the site use? This needs settling before the Pinterest domain claim and
  Search Console setup, since neither carries over cleanly to a new domain.
