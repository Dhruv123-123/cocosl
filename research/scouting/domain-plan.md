# Domain plan: short names to check per brand, and where renewals are cheapest

Written 2026-11-07. **Docs only. Nothing was bought.** `domains-and-names.md` already has RDAP lookups for
the exact names (all four `.com`s are taken) and five longer unregistered options per brand. This adds
**shorter names** to check. Their availability is marked **check**, because this session's network can't
reach RDAP today. Check each one in the registrar's search box before choosing.

## TL;DR

- **Register at Cloudflare Registrar.** It sells at cost with no markup, includes WHOIS privacy, and
  doesn't require Cloudflare DNS. `.com` there was **$10.46 a year** until 31 Oct. Verisign raised the
  wholesale price 7% on **1 Nov 2026** ($10.26 to $10.97), so expect about **$11.17 a year**, the same
  for first year and renewal.
- **Porkbun** ($11.81 for registration and renewal today, free WHOIS privacy) is the fallback if Cloudflare
  isn't wanted.
- **Avoid "cheap first year, expensive renewal" offers.** Namecheap is $11.48 the first year but $18.68 at
  renewal. `.co` at Porkbun is $15.76 the first year but $31.20 at renewal, so stay with `.com`.
- **Four brands × about $11.17 ≈ $45 a year.** It's the only spend in the launch plan, so it needs Dhruv's
  OK.
- **Shortest safe pick per brand, if available:** `mmsimple.com`, `decodescam.com`, `the1099.com` (likely
  taken; else `1099mo.com`), `eldinerosimple.com` (already confirmed unregistered in `domains-and-names.md`).

## 1. Short names to check

Ordered by preference within each brand. "Unregistered (RDAP)" means `domains-and-names.md` confirmed it
today. Everything else is **check**.

| Brand | Name | Length | Status | Note |
|---|---|---:|---|---|
| Money Made Simple | **mmsimple.com** | 8 | check | Short, matches the MMS initials |
| | moneysimply.com | 11 | check | Reads naturally |
| | mmsweekly.com | 9 | check | Fits the weekly newsletter |
| | mymoneymadesimple.com | 17 | **unregistered (RDAP)** | Safe fallback |
| Scam Decoded | **decodescam.com** | 10 | check | Verb-first; "decode a scam" |
| | scamdecode.com | 10 | check | One letter off the brand, so typos land here |
| | scamdecoder.com | 11 | check | `thescamdecoder.com` is taken (Sep 2026), so this may be too |
| | getscamdecoded.com | 15 | **unregistered (RDAP)** | Safe fallback |
| 1099 Money | **the1099.com** | 7 | check (likely taken) | Very short |
| | 1099mo.com | 6 | check | Short; "mo" for money |
| | ten99money.com | 10 | check | Easier to say aloud than the digits |
| | the1099money.com | 13 | **unregistered (RDAP)** | Safe fallback |
| Dinero Simple | **eldinerosimple.com** | 14 | **unregistered (RDAP)** | Natural Spanish; first choice |
| | tudinerosimple.com | 14 | check | "Your simple money" |
| | dinerosimpleusa.com | 15 | check | Signals the US-Latino audience |

**Rules for choosing:** say it aloud once and see whether someone can type it (no hyphens, and avoid
digits for spoken CTAs unless the brand is the number, as with 1099). Match the social handle to the
domain (`domains-and-names.md`). Don't buy alternates "just in case", since each one costs about $11 a year.

## 2. Renewal prices for `.com` (per year, including ICANN's $0.20)

| Registrar | First year | Renewal | WHOIS privacy | Source, date |
|---|---:|---:|---|---|
| **Cloudflare** | $10.46 → ~$11.17 from 1 Nov | same | Free | CostGoat, 20 Oct 2026; Cloudflare "at cost" |
| Dynadot | $10.88 | $10.88 | — | CostGoat, 20 Oct 2026 (before the increase) |
| **Porkbun** | **$11.81** | **$11.81** | Free | Porkbun pricing page, read today (after the increase) |
| Namecheap | $11.48 | **$18.68** | — | CostGoat, 20 Oct 2026 |
| AWS Route 53 | $16.00 | $16.00 | — | CostGoat |

Verisign's announcement starts a four-year price cycle (webhosting.today, May 2026), so renewals will
likely rise again in later years. Locking in multi-year renewals at Cloudflare or Porkbun before the next
increase is optional.

## 3. Steps once Dhruv picks (about 15 minutes)

1. Search each chosen name at Cloudflare Registrar and buy only those (auto-renew on, WHOIS privacy on).
2. Point each one at its Netlify site, and set up SPF and DKIM for the newsletter tool
   (`newsletter-tool-decision.md`).
3. Claim it in Google Search Console and Pinterest (`pinterest-seo.md`), and update `link_in_bio` in each
   brand yaml.

## Sources

[Cloudflare Registrar](https://www.cloudflare.com/products/registrar/),
[Porkbun domain pricing](https://porkbun.com/products/domains) (read 2026-11-07),
[CostGoat .com registrar comparison](https://costgoat.com/compare/domains/com) (20 Oct 2026),
[webhosting.today on Verisign's Nov 2026 increase](https://webhosting.today/2026/05/21/verisign-starts-a-four-year-com-price-cycle-the-first-7-hits-in-november/),
and `domains-and-names.md` for the RDAP results.
