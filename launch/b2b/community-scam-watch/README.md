# Scam Watch (large print) for libraries and senior centers

A monthly, white-label scam-awareness pack for older adults, printed and posted by public libraries,
senior centers and Area Agencies on Aging under their own name. Built from the Scam Decoded for
Seniors pack (the `/seniors/` product: golden rules, calls to hang up on, official numbers).

**$19 a month for one location, $59 for a system** (up to 10 branches, or every center in an Area
Agency on Aging region). In-person or online talks are $150 each (from the speaking kit). Annual plans
get 2 months free and include the Scam Decoded for Seniors group print license ($49 value). Two months
free for the first 3 organizations.

| File | What it is |
|---|---|
| `issues.json`, `samples/month-1..4.md` | 4 sample issues for Jan, Feb, Mar, Apr 2027: the grandchild-in-trouble call (AI voices, safe word), romance scams, fake Social Security and Medicare calls, tech-support pop-ups. |
| `brands/example.json` | **Fictional** "Sample County Library" used for the sample pack. |
| `product.json` | Labels and formats. Brand slots: `{{ORG_NAME}}`, `{{HELP_LINE}}`, `{{HELP_LINE_SHORT}}`, `{{ORG_FOOTER}}`. |
| `sales-sheet.html` | One-page sales sheet (renders to `out/sales-sheet.pdf`). |
| `COMPLIANCE_NOTE.md` | Not legal advice, sourcing, large-print standards, public-sector buying, no endorsements, what staff should and shouldn't do. |
| `COLD_EMAILS.md` | Emails for library adult-services staff, senior center directors and Area Agencies on Aging; follow-ups; replies. |
| `PROSPECTS.csv`, `PROSPECTS.md` | 30 prospects: 8 Montana Area Agencies on Aging, 10 Idaho senior centers (from the state's public list), 12 public libraries. |

Each issue builds into: a large-print handout (18 pt, front and back), a bulletin board flyer, a
1920×1080 screen slide, a Facebook post with image, a newsletter blurb (email HTML + text) and a
10-minute talk guide for a group leader.

## Different from the credit union workflow

Follow `../credit-union-alert/DELIVERY_WORKFLOW.md`, with these changes:
- **Monthly**, delivered **3 weeks** early: centers print their activity calendars and newsletters a
  month ahead.
- Plain words, short sentences, 18 pt minimum for print. Never ask readers to tap a link; give phone
  numbers and say "type the address yourself".
- Re-check the official numbers (Elder Fraud Hotline, Social Security, Medicare, FTC) every quarter.
- Good months to plan around: World Elder Abuse Awareness Day (June 15), Medicare open enrollment
  (Oct 15 to Dec 7), holiday scams (Nov to Dec), tax season (Feb to Apr).
