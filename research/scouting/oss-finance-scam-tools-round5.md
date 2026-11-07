# Open-source round 5: MIT and Apache tools for money and scam awareness that we could adapt or credit

Written 2026-11-07. **Docs only. Nothing was forked, copied or installed.** This round ran 32 GitHub
repository searches through the official search API. Licences come from GitHub's licence detection on each
repo, plus the README where data terms matter. Star counts and last-push dates are from 7 Nov 2026.

The finance apps (Actual, ezBookkeeping, Mintable, Ocular, ExpenseOwl, open-social-security,
Toolkit for YNAB and others) are already screened in `forkable-finance-apps.md`, and the tax libraries in
`oss-landscape.md`. **This round adds the scam-awareness side, which those files didn't cover, plus seven
finance projects they missed.**

## TL;DR

1. **The best find for Scam Decoded is a phishing-domain list to back up the link checker.**
   Phishing.Database (MIT, 1,636 stars, updated Oct 2026) and DestroyList (MIT, 1,992 stars, updated
   7 Nov 2026) are both free domain lists with a false-positive process. Our link checker
   (`scam-checker/link/` on PR #8) only uses look-alike rules today. Adding a list match ("this exact
   domain has been reported as phishing") would make it stronger. **The catch is size and privacy:** don't
   send the user's link to an API. Ship a hashed, trimmed list with the page, or check against a weekly
   snapshot.
2. **pyWhat (MIT, 7,343 stars) is the pattern library to borrow ideas from** for the "Is this a scam?"
   checker. It recognises crypto wallet addresses, phone numbers, URLs, card-number formats and more in
   pasted text. Our checker could flag "this message contains a Bitcoin address" the same way. pyWhat is
   Python, so port the patterns we need to JavaScript, and keep the MIT notice.
3. **Two finance projects are worth a credit link rather than code:** cFIREsim-open (Apache-2.0), a
   historical retirement simulator, and druce/swr (MIT), safe-withdrawal-rate research code. They fit a
   future "Can I retire early?" explainer. Don't fork either: cFIREsim-open was last pushed in 2022.
4. **Avoid one trap:** PolicyEngine's TAXSIM emulator is MIT, but the engine it runs on, `policyengine-us`, is
   **AGPL-3.0**. Hosting a tax calculator on it would put our site under the AGPL. Our hard-coded 2026
   tables (PR #8) don't have that problem.
5. **Content we can quote freely is the US government's.** FTC and CFPB consumer pages are federal works,
   which generally aren't copyrighted (images and logos aside; check each page's notice). That's a better
   "credit and adapt" source for Scam Decoded than any repo.

## 1. Scam awareness: tools and data

| Repo | Licence | Stars / last push | What it is | How we'd use it | Notes |
|---|---|---|---|---|---|
| [Phishing-Database/Phishing.Database](https://github.com/Phishing-Database/Phishing.Database) | MIT | 1,636 / 2 Oct 2026 | Phishing domains and URLs, retested regularly with PyFunceble | A weekly snapshot as a "reported phishing domain" check in the link checker | Keep the MIT notice. False positives go through its issues. The README doesn't separate data terms from code |
| [phishdestroy/destroylist](https://github.com/phishdestroy/destroylist) | MIT | 1,992 / 7 Nov 2026 | A phishing and scam domain blocklist (205K+ entries) with a free API and CDN copies | The same use, or a second list to cross-check | Calls itself "non-commercial volunteer"; the licence is MIT, but **email them before using it in a product**. Appeals form for false positives. Don't call the API with user links |
| [elliotwutingfeng/GlobalAntiScamOrg-blocklist](https://github.com/elliotwutingfeng/GlobalAntiScamOrg-blocklist) | BSD-3-Clause (code) | 33 / 30 Oct 2026 | Scam URLs compiled by the Global Anti Scam Organization, as text | **Don't use the data yet.** The data is GASO's, the repo isn't affiliated with GASO, and its terms aren't stated | Ask GASO first |
| [bee-san/pyWhat](https://github.com/bee-san/pyWhat) | MIT | 7,343 / 5 Nov 2026 | Identifies wallet addresses, emails, IPs, phone numbers and more in text | Port the relevant patterns to the JS checker ("contains a crypto address", "contains a short link") | Python. Port selectively, with the MIT notice in a new `apps/THIRD_PARTY.md` (PR #8 has no notices file yet) |
| [deFr0ggy/NightOwl](https://github.com/deFr0ggy/NightOwl) | MIT | 62 / Oct 2023 | An offline phishing email analyzer "for non-techies" | Ideas for a future "Check this email" page: header and link checks shown in plain language | Stale. Ideas only, no code |
| [mochabyte0x/Elyzer](https://github.com/mochabyte0x/Elyzer) | MIT | 51 / Jun 2026 | An email header analyzer that flags spoofing | The same idea: paste the headers, and see whether the sender's domain matches | Small project. Port the logic, not the code |
| [PAST2212/domainthreat](https://github.com/PAST2212/domainthreat) | MIT | 66 / Oct 2025 | Watches newly registered domains for brand impersonation | Research input for Scam Decoded: "fake [bank] sites registered this week" posts | Needs a feed of new registrations. Use it for content research, not as a product |
| [urldna/urldna](https://github.com/urldna/urldna) | MIT | 81 / Nov 2025 | A self-hosted website scanner (screenshots, page details) | Behind-the-scenes research when writing scam posts | Don't host it publicly: scanning user links is a security and abuse risk |
| [sublime-security/sublime-platform](https://github.com/sublime-security/sublime-platform) | MIT | 277 / 5 Nov 2026 | Email security (BEC and phishing detection) for up to 100 mailboxes | Inspiration for the B2B Vendor Payment Check (bank-change fraud). Its detection rules are in a separate repo with its own licence | Too heavy to run. Read the rule ideas only, after checking the rules repo's licence |
| [SagarBiswas-MultiHAT/PhishGuard-AI](https://github.com/SagarBiswas-MultiHAT/PhishGuard-AI) | MIT | 28 / Oct 2026 | A web game that trains people to spot phishing emails | A format idea for the Scam Decoded `/quiz/` (timed rounds, explained answers) | Ours already exists. Borrow the format, not the code |
| [spmedia/Crypto-Scam-and-Crypto-Phishing-Threat-Intel-Feed](https://github.com/spmedia/Crypto-Scam-and-Crypto-Phishing-Threat-Intel-Feed) | MIT | 75 / 6 Nov 2026 | A daily feed of crypto scam and phishing sites | Research for the pig-butchering and fake-exchange posts | Content research only |

**Left out:** stale lists (discord-phishing-links, last push Mar 2024; EtherScamDB, 2022); anything with
no licence (openphish/public_feed shows no licence, so the default is "all rights reserved"); and anything
that attacks scam sites (spam-flooding scripts), which isn't something we'd ever publish or link.

## 2. Finance: seven projects the earlier screens missed

| Repo | Licence | Stars / last push | What it is | Use |
|---|---|---|---|---|
| [boknows/cFIREsim-open](https://github.com/boknows/cFIREsim-open) | Apache-2.0 | 157 / Apr 2022 | A historical retirement simulator (a JS rewrite of cFIREsim) | Credit link in a FIRE explainer. Don't fork (stale) |
| [druce/swr](https://github.com/druce/swr) | MIT | 37 / Apr 2021 | Safe-withdrawal-rate research with flexible schedules | A source to cite on "is 4% safe?", with the notebook as the citation |
| [zebangeth/rent-or-buy.homes](https://github.com/zebangeth/rent-or-buy.homes) | MIT | 229 / Sep 2026 | A rent-vs-buy web app | Check our PR #8 rent-vs-buy calculator's maths against it. Credit it if we adopt anything |
| [jpederson/Accrue.js](https://github.com/jpederson/Accrue.js) | MIT | 110 / Feb 2025 | Loan and interest calculator plugin (jQuery) | Nothing to adopt; our calculators are dependency-free. A test oracle for amortization numbers |
| [zhiyingzzhou/renewlet](https://github.com/zhiyingzzhou/renewlet) | MIT | 308 / 7 Nov 2026 | A self-hosted subscription tracker with renewal reminders | Feature ideas for the subscription audit's "remind me before it renews" step (`product-ideas-round2.md`) |
| [Pool-Of-Tears/GreenStash](https://github.com/Pool-Of-Tears/GreenStash) | MIT | 792 / Aug 2026 | An Android savings-goals app | Ideas for sinking-funds features. Android only, so ideas only |
| [hisabi-app/hisabi](https://github.com/hisabi-app/hisabi) | MIT | 460 / Sep 2026 | A finance tracker that parses bank SMS messages | The SMS-parsing idea could help the dashboard spreadsheet maker read pasted text alerts |

**Trap:** [PolicyEngine/policyengine-taxsim](https://github.com/PolicyEngine/policyengine-taxsim) is MIT, but it
runs on `policyengine-us`, which is **AGPL-3.0**. Fine for research, but not inside a hosted product.

## 3. How to credit and adapt (the rules)

1. **Ideas aren't covered by copyright; code is.** If we only take an idea (a quiz format, a header check),
   no notice is needed. A thank-you link is still good practice.
2. **Any MIT or BSD code or data we copy** goes in `apps/THIRD_PARTY.md` (to be created) with the copyright line and
   licence text. That's the MIT and BSD condition.
3. **Apache-2.0** also needs any NOTICE file carried over, and a note on what we changed.
4. **Blocklist data:** state the source and date on the page ("domain list: Phishing.Database, updated
   weekly"). Explain that a domain *not* on the list isn't proof it's safe. Give users a way to report a
   false positive.
5. **Never imply endorsement.** "Uses data from X", never "X-approved". The same goes for the FTC: "Source:
   FTC", never an FTC logo.

## Sources

GitHub search API (`search/repositories`, 32 queries, 7 Nov 2026) for names, licences, stars and dates.
READMEs read for data terms:
[Phishing.Database](https://github.com/Phishing-Database/Phishing.Database),
[DestroyList](https://github.com/phishdestroy/destroylist),
[GlobalAntiScamOrg-blocklist](https://github.com/elliotwutingfeng/GlobalAntiScamOrg-blocklist),
[sublime-platform](https://github.com/sublime-security/sublime-platform).
Licences were detected by GitHub; re-read each LICENSE file before copying anything.
