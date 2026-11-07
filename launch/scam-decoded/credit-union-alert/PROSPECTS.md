# 30 prospect credit unions

`PROSPECTS.csv` lists 30 community credit unions in Montana (10), Idaho (8), Oregon (6) and
Washington (6), in send order. Same region as the Spot It, Stop It outreach, so "credit unions around
Great Falls" is an honest line and word of mouth can help.

## How they were picked (public information only)

- **Source:** NCUA 5300 call report data for **Q2 2026 (June 30, 2026)**, the public quarterly filing
  every federally insured credit union makes, read through BankRegReports' state lists. Each row's
  `data_source` gives the page. NCUA's own site wasn't reachable from this session; the charter number
  lets you check any row on NCUA's Credit Union Locator.
- **Size:** $77M to $465M in assets. Big enough to pay $49 to $149 a month, small enough that most
  have no one writing weekly fraud content.
- **Left out:** credit unions over $500M (they usually have marketing teams), employee-only and union
  credit unions (narrow membership; a weaker fit for lobby and social), and **Vocal Credit Union**
  (already in the Spot It, Stop It list; don't pitch it two offers at once).
- No scraping, no bought lists, no personal data. Notes come from public news releases and profiles;
  each one says what to double-check.

## Columns

| Column | Meaning |
|---|---|
| `send_order` | Montana first (closest to the other outreach), then Idaho, Oregon, Washington; smaller first within each state. |
| `ncua_charter` | NCUA charter number. Look it up on NCUA's Credit Union Locator to get the official website. |
| `total_assets_usd_m_q2_2026`, `members_q2_2026` | From the call report. |
| `suggested_tier` | Essentials under $100M, Standard $100M to $500M. Offer Plus where two or more listed credit unions share a town (Great Falls, Pocatello), because local exclusivity matters there. |
| `website`, `contact_route` | **Blank on purpose: fill these in by hand** from each credit union's own site (see below). |
| `notes` | Personalization hooks and things to check before writing. |

## Filling in website and contact (about 3 minutes each)

1. Search the charter number on NCUA's Credit Union Locator, or search the name and city, and open
   the credit union's **own** website.
2. Look at the About, Leadership, Contact and News pages. Copy, in this order: a named marketing or
   member experience contact with a published email; the CEO's published email; a general email;
   the contact form URL.
3. Write where you found it in `contact_route` (for example `info@... from /contact`).
4. Find one true, recent thing for `{Personal line}` in the email: a merger, a new branch, a fraud
   warning on their site, a community event. Skip the line if there's nothing real.

Expect a lot of contact forms. That's normal for credit unions; use the contact-form version in
`COLD_EMAILS.md`.
