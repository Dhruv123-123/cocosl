# Domains, handles and name conflicts for the four brands

Checked 2026-11-07. Domains were looked up one by one in Verisign's public RDAP service for `.com`
(`rdap.verisign.com/com/v1/domain/<name>`). A registered name returns a record; an unregistered one
returns "not found". **"Not found" only means nobody had registered it at the moment of the lookup.** It
isn't a reservation, so register the ones you want soon. Social handles couldn't be checked from here
without logging in or scraping, which we don't do, so the handle plan below has fallbacks to try in each
sign-up screen.

## TL;DR

- **Use "Scam Decoded", not "Scam Shield".** "SCAMSHIELD" is a live US trademark owned by **T-Mobile
  USA** (Reg. 6,437,351, registered 3 Aug 2021, classes 9 and 38, for its anti-scam call-blocking app),
  and Singapore's government runs a ScamShield app too. An anti-scam brand with the same name as T-Mobile's
  anti-scam product is the conflict to avoid.
- **The four exact `.com` names are all taken**: moneymadesimple.com (since 2002), scamdecoded.com (May
  2026), 1099money.com (Sept 2026), dinerosimple.com (2020). Each brand has five unregistered alternatives below.
- **Two recent registrations might be ours.** `1099money.com` (registered 10 Sep 2026 at Cloudflare) and
  `getmoneymadesimple.com` (29 Jun 2026 at Cloudflare). If Dhruv registered either, use it.
- **"Money Made Simple" is a crowded name.** There are at least three podcasts with that name (one by New
  Zealand's Simplicity fund, "The Money Made Simple Show", one on iHeart) and a 24-year-old .com. It works as
  a content brand but will be hard to own or trademark. Worth deciding before buying a domain and
  printing it on products.

## Domains checked

### Money Made Simple

| Domain | Status (2026-11-07) |
|---|---|
| moneymadesimple.com | Taken: registered 19 Apr 2002, GoDaddy, expires 19 Apr 2027 |
| getmoneymadesimple.com | Taken: 29 Jun 2026, Cloudflare (**check whether it's Dhruv's**) |
| moneymadesimplehq.com | Taken: 18 Mar 2025, GoDaddy |
| themoneymadesimple.com | Taken: 8 Sep 2025, GoDaddy |
| **mymoneymadesimple.com** | Not registered (first choice) |
| **readmoneymadesimple.com** | Not registered (fits a newsletter) |
| **joinmoneymadesimple.com** | Not registered |
| **moneymadesimpleweekly.com** | Not registered (matches "one money move a week") |
| **moneymadesimpleco.com** | Not registered |

### Scam Decoded (and Scam Shield)

| Domain | Status |
|---|---|
| scamdecoded.com | Taken: 24 May 2026 via NameBright/DropCatch (a drop-catching registrar, so possibly for resale; ask the registrar for a price before choosing an alternative) |
| thescamdecoder.com | Taken: 29 Sep 2026, Cloudflare |
| scamshield.com | Taken: 30 Apr 2001, DreamHost |
| scamshieldhq.com | Taken: 9 Apr 2026, GoDaddy |
| **getscamdecoded.com** | Not registered (first choice) |
| **scamdecodedhq.com** | Not registered |
| **joinscamdecoded.com** | Not registered |
| **scamdecodedweekly.com** | Not registered (matches the weekly Scam Alert) |
| **decodethescam.com** | Not registered (an alternative name, if wanted) |

### 1099 Money

| Domain | Status |
|---|---|
| 1099money.com | Taken: 10 Sep 2026, Cloudflare (**check whether it's Dhruv's**; the repo mentions `1099money.co`) |
| **the1099money.com** | Not registered (first choice) |
| **get1099money.com** | Not registered |
| **my1099money.com** | Not registered |
| **1099moneyhq.com** | Not registered |
| **1099moneyweekly.com** | Not registered |

### Dinero Simple

| Domain | Status |
|---|---|
| dinerosimple.com | Taken: 4 Oct 2020, NameBright, expires 4 Oct 2027 |
| **eldinerosimple.com** | Not registered (first choice: natural Spanish) |
| **midinerosimple.com** | Not registered |
| **holadinerosimple.com** | Not registered |
| **dinerosimplehq.com** | Not registered |
| **dinerosimpleus.com** | Not registered (signals the US-Latino audience) |

**Before buying:** check each one again at the registrar's checkout, then register through the same
account (Cloudflare Registrar sells at cost), turn on auto-renew and WHOIS privacy, and point it at the
Netlify site. Search Console, the Pinterest domain claim and the Kit sending domain all need the final
domain, so this comes first (see `pinterest-seo.md` and `newsletter.md`).

## Handles to reserve

Use one handle across every platform, so the bio link, watermark and spoken CTA can all say the same
thing. Try these in order in each platform's sign-up screen (Instagram, TikTok, YouTube, Threads,
Pinterest, X, Facebook Page), and reserve the first one that's free **on all of them**:

| Brand | 1st choice | Fallbacks |
|---|---|---|
| Money Made Simple | `@moneymadesimple` | `@mymoneymadesimple` · `@moneymadesimple.hq` · `@moneymadesimplehq` |
| Scam Decoded | `@scamdecoded` | `@getscamdecoded` · `@scamdecoded.hq` · `@scamdecodedhq` |
| 1099 Money | `@1099money` | `@the1099money` · `@1099money.hq` · `@1099moneyhq` |
| Dinero Simple | `@dinerosimple` | `@eldinerosimple` · `@midinerosimple` · `@dinerosimple.us` |

Notes:
- **TikTok accounts must be personal, not Business**, to stay eligible for Creator Rewards
  (`tiktok-instagram-monetization.md`).
- **Instagram and Threads share a handle**, so reserve them together.
- If the domain and handle can't match exactly, match the handle to the **domain** (`getscamdecoded.com`
  ↔ `@getscamdecoded`). People type what they hear.
- Don't register handles we won't use for months. Inactive accounts can be reclaimed by the platforms, and
  YouTube removes monetization from channels idle for 6+ months.

## Name conflicts to avoid

| Name | Conflict | Risk | What to do |
|---|---|---|---|
| **Scam Shield** | US trademark **SCAMSHIELD**, T-Mobile USA, live, Reg. 6,437,351 (classes 9, 38) for its anti-scam app ([Markinton record](https://markinton.com/trademark/scamshield-90056826), [T-Mobile Scam Shield](https://www.t-mobile.com/scamshield)). Also Singapore's government ScamShield app | **High.** Same field (stopping scam calls and texts), a famous owner | **Don't use it.** Use Scam Decoded, and rename the `scamshield.netlify.app` site |
| **Scam Decoded** | No brand found with this name. Meta ran a "Decode Scam 2025" campaign in Vietnam, and the "Decode Global" investment scam appears in search results | Low. Different name, but watch for confusion with the scam site | OK to use. Add "Scam Decoded" to the about page early so searches find us first |
| **Money Made Simple** | Several podcasts with that name ([Simplicity NZ](https://simplicity.kiwi/learn/podcast), "The Money Made Simple Show", an iHeart show), moneymadesimple.com since 2002, and a "WE MAKE MONEY SIMPLE" US trademark record ([Gleanmark](https://gleanmark.com/trademark/uspto-86571476)) | **Medium.** Not one owner to fear, but too common to own, and a bank or podcast could object to a product with the same name | OK as a content brand. Don't file a trademark on it, and consider a more distinctive name for the paid products |
| **1099 Money** | "1099" is an IRS form number, so the name is descriptive; no brand found using "1099 Money" | Low for conflict, but weak to protect | Never imply IRS affiliation: no IRS logo, eagle or "official" wording. The site already says it isn't tax advice |
| **Dinero Simple** | dinerosimple.com has been registered since 2020; no active brand found in search | Low-medium | Check what dinerosimple.com shows before launch. If it's an active finance site, prefer a more distinct domain (`eldinerosimple.com`) |

**How to check properly before spending money on a name:** search the USPTO trademark database
(tmsearch.uspto.gov) for each name in classes 9 (apps), 16 (printed guides), 35 (advertising and
business), 36 (financial information) and 41 (education). It wasn't reachable from here. Anything live in
class 36 or 41 with a near-identical name is a stop. For a brand that will sell products, an hour with a
trademark attorney costs less than a rename.

## Open questions for Dhruv

1. Did you register `1099money.com` or `getmoneymadesimple.com`?
2. Confirm "Scam Decoded" as the final name, given the T-Mobile mark. The site, Kit account and handles
   can then be set up under it.
3. Keep "Money Made Simple", or pick something more distinctive before buying the domain?
