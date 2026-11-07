# Scam Watch (large print) for libraries and senior centers

A monthly, white-label scam-awareness pack for older adults, printed and posted by public libraries,
senior centers and Area Agencies on Aging under their own name. Built from the Scam Decoded for
Seniors pack (the `/seniors/` product: golden rules, calls to hang up on, official numbers).

**$19 a month for one location; $49 for 2 to 4 locations; $12 a location for 5 to 20 (10 locations is
$120); quote from $250 for 21+ or a whole Area Agency on Aging region.** A local credit union can also
**sponsor** it: $99 a month covers up to 5 libraries or centers, marked "brought to you by [credit
union]" (sold with the Weekly Scam Alert). In-person or online talks are $150 each (from the speaking kit).
**Spanish add-on** (`es/`, issues 1 to 3, pending native review): proposed at **+$10 a month a location**, or included at no
charge in a credit-union-sponsored plan. The sponsored samples are `brands/cu-sponsored.json` (English) and
`es/brands/cu-sponsored.json` (Spanish). Pricing follows the scouting note `research/scouting/b2b-library-tier-note.md` (PR #2): pitch the $19
plan to programming or outreach budgets, because small libraries' e-resource budgets are tiny. Annual plans
get 2 months free and include the Scam Decoded for Seniors group print license ($49 value). Two months
free for the first 3 organizations.

| File | What it is |
|---|---|
| `issues.json`, `samples/month-1..12.md` | 12 issues, Jan to Dec 2027. May to Dec: "you've won" prizes, utility shutoff threats, package texts, "free" tests and your Medicare number, disaster charity scams, Medicare open enrollment calls, gift card scams, "bank fraud department" calls. Jan to Apr: the grandchild-in-trouble call (AI voices, safe word), romance scams, fake Social Security and Medicare calls, tech-support pop-ups. |
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
