# Kit sales funnel: free Lite, then 3 emails, then the bundle

Nothing here sends anything. Dhruv builds the automation in Sender by hand and turns it on.

## The path

```
Pin / TikTok / tutorial video
        │
        ▼
Free Listing Video Maker Lite   (Gumroad, $0+, or the Sender signup form on the studio site)
        │  email address
        ▼
Day 0  "Your free Listing Video Maker Lite"         → the download + a 10-minute first video
Day 2  "3 things that make a silent listing video work" → tips, then the full Listing Video Kit ($19)
Day 5  "The bundle: listing videos, pins and holiday sale graphics" → Small Shop Bundle ($35, vs $49 separately)
        │
        ▼
Bundle buyers: Gumroad's own receipt and refund flow (30 days, no questions)
```

Three emails, then nothing more from this sequence. Anyone who wants more joins a newsletter separately. Every email has a one-click unsubscribe (Sender adds it).

## Files

| File | What it is |
|---|---|
| `brands/sequences/small-shop-kits.yaml` | The 3 emails, in the factory's Sender sequence format (`day_offset`, `subject`, `preheader`, `body_markdown`, `cta_url_key`, `cta_label`) |
| `brands/small-shop-kits.yaml` | A minimal brand file so the factory can render the emails. It sits here, not in `brands/`, so the daily worker never runs it as a content channel (`cadence.paused: true`, `welcome_via: sender`) |
| `../../../tests/test_kits_funnel.py` | Checks the copy validates, exports to 3 emails, shows $35 vs $49, and has no discount block |

## Export for Sender

From the repo root:

```bash
FACTORY_BRANDS=launch/ugc-service/kits-funnel/brands factory sequence-check small-shop-kits
FACTORY_BRANDS=launch/ugc-service/kits-funnel/brands factory sequence-export small-shop-kits --for sender
```

That writes `output/sequences/small-shop-kits/<date>-sender/` with `01-day0/`, `02-day2/`, `03-day5/` (each: `subject.txt`, `body.html`, `email.txt`, `DELAY.txt`) and a `CHECKLIST.md` that walks through building the automation. Delays come out as 0, 2 and 3 days.

## Before you export for real

1. Replace `YOURNAME` (your Gumroad username) and `YOUR-STUDIO-SITE` in both YAML files. Check with `grep -rn "YOUR" launch/ugc-service/kits-funnel/brands`.
2. Replace `[Your Name]` in the sign-off.
3. Check `vars.price` (35) matches the bundle's real Gumroad price, and that "$49 separately" is still true ($19 + $15 + $15). If you change kit prices, change both.

## How people get into the sequence

Pick one; both end in the same Sender group.

- **Sender signup form (recommended).** Put a Sender form on the studio site's kits section: "Get the free Lite maker by email". The form adds people to a group called `Kits Lite`; the automation's trigger is "Subscriber joins group: Kits Lite". Use Sender's double opt-in.
- **Gumroad.** Gumroad keeps the email of everyone who downloads the free Lite. Gumroad doesn't push them to Sender by itself, so either export the customer list from Gumroad now and then and import it into the `Kits Lite` group, or skip Sender and paste the same three emails into a **Gumroad Workflow** for the Lite product (same delays). Only import people who agreed to get emails from you, and check Gumroad's current terms on using customer emails before you do.

Don't do both for the same person, or they get every email twice.

## Optional: a real subscriber offer

The copy has no discount. If you want one, make it real: create an offer code on the bundle in Gumroad (for example `KITS5`, $5 off) with a real end date, then add one line to the day-5 email inside `{if launch}...{/if}` and fill `launch_price`, `launch_code` and `launch_ends` under `vars:`. The factory then exports two versions of that email (with and without the code); swap to the no-code one the day it ends. Never show a "was" price the bundle didn't actually sell at.

## What to watch (after 2 to 4 weeks)

| Number | Where | Rough guide |
|---|---|---|
| Lite downloads per week | Gumroad | Grows with pins and tutorials |
| Email open rate | Sender | Below 30% on day 0: check the sender domain setup |
| Clicks on email 3 | Sender | The bundle button is the one that matters |
| Bundle sales from the sequence | Gumroad (UTM `kits-welcome-sequence`) | Divide by Lite downloads that month |
| Refunds | Gumroad | Above 5%: fix the listing or the kit, not the emails |

## Rules this copy follows

- Real prices only. No fake "was" prices, no countdowns that reset, no made-up scarcity.
- No testimonials, ratings, sales counts or income claims.
- The kits frame the seller's own photos and never change the product; the emails say so.
- "Etsy", "Shopify" and "Gumroad" appear only as descriptions; the footer says the kits aren't affiliated.
- Footer: "Drafted with AI help, edited by a person."
