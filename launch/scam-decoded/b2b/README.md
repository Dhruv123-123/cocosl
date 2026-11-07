# Spot It, Stop It B2B outreach: lead list, pitches, follow-ups

Everything you need to pitch the $99 **Spot It, Stop It** scam-awareness training pack to small
businesses. **Nothing here has been sent.** You send every email yourself, by hand, from your own inbox.
The pack itself is in `products/team-training/` (zip, slides, guide, quiz, certificate, poster) and its
store listing is `products/team-training/LISTING.md`.

## What's in here

| File | What it is |
|---|---|
| `leads.csv` | 75 researched small businesses that take payments and hold customer data, in the factory's import format (`name,contact_name,email,website,niche,source,notes`). Sorted in send order. |
| `leads_research.csv` | Same leads with all the research: where the email is published, what we noticed, the scam risk to lead with, narrow-inbox and free-mail flags, the opener line, and the 3 scam tells used in the last email. |
| `pitches/NNN-name.md` | One file per lead: personalized Email 1, Follow-up 1, Follow-up 2 and planned send dates. Numbered in send order. |
| `ALL_PITCHES.md` | Every pitch in one file, for scrolling. |
| `TRACKER.csv` | Send schedule (8 new a weekday from Tue 10 Nov) with blank columns for sent dates, replies, poster sent, pack bought and outcome. Open it in Google Sheets or Excel. |
| `FOLLOW_UP_SEQUENCE.md` | The full sequence (day 0 / 4 / 9), plus what to send for every kind of reply, including "does this make us compliant?" |

## The offer

- **Email 1** gives something useful first: a free one-page "Verify before you pay" poster (the
  `Poster-Verify-Before-You-Pay.pdf` already in the pack). They reply "yes" and you attach it. No link
  in the first email, which keeps it out of spam folders and makes it feel less like a sales email.
- **Follow-up 1** is a short bump.
- **Follow-up 2** gives three scam tells for their kind of business for free, then mentions the $99 pack
  once, with a link.
- The poster reply (Branch A in `FOLLOW_UP_SEQUENCE.md`) mentions the pack once, with no pressure.

## How the leads were found

Public web search, then each business's **own website** was opened to check that it's small and
local, handles payments or personal data, and publishes a business email on its own site. The page
the email is on is in `leads_research.csv` → `email_source_url`. No scraping tools, no bought lists,
no guessed emails, and no personal addresses from anywhere else. Directory sites (Yelp, BBB, CPA
directories) were used only to find names, never as an email source. Big regional or national firms
were skipped.

**Mix:** property management 21, insurance agencies 12, accounting and tax 12, dental 10, bookkeeping
and payroll 5, veterinary 4, estate and real estate law 4, title and escrow 3, chiropractic 3, credit
union 1. Montana 44, Idaho 25, Washington 5, Oregon 1. Concentrating on a few regions makes it easier
to say "offices around Bozeman" honestly and lets word of mouth help.

Dental offices and credit unions were the hardest to find with a published email (most use only
contact forms), so there are fewer of them than planned.

## Before you send anything (one-time setup)

1. **Put the pack on sale** and paste the real link in place of `{Pack link}` everywhere
   (find-and-replace in `ALL_PITCHES.md` or each file). Use the listing in
   `products/team-training/LISTING.md`.
2. **Fill in the placeholders:** `{Your Name}`, `{Brand Name}` (Scam Decoded, or whatever name you
   settle on), `{Brand site URL}` (only used in one reply) and the footer postal address (a PO box or
   virtual mailbox is fine). The footer with an address and opt-out line is required by CAN-SPAM.
3. **Have the poster ready to attach:** `products/team-training/Poster-Verify-Before-You-Pay.pdf`.
4. Send from a normal inbox on your own domain if you can. A brand-new domain sending 20+ cold emails a
   day can land in spam, so start slower (4 a day) for the first week if the domain is new.

## Daily routine (about 30 minutes)

1. Open `TRACKER.csv` and filter `email1_planned` = today.
2. For each lead, open its pitch file, spend 60 seconds on their site to check the detail is still true,
   tweak the opener if needed, and send Email 1.
3. Send any Follow-up 1s and 2s due today, **only to people who haven't replied**.
4. Write the sent date in the tracker. Anyone who says no or stop: `do_not_contact`, never again.
5. Reply to yeses the same day using `FOLLOW_UP_SEQUENCE.md` (Branch A).

## Things to know about specific leads

- **Free-mail and ISP addresses:** 19 businesses publish a Gmail, Outlook, Mac, montana.com,
  blackfoot.net or similar address as their business email on their own site. That's fine to use.
- **Narrow inboxes:** 9 published emails are `orders@`, `leasing@`, `rentals@`, `support@`,
  `request@`, `feedback@`, `Taxes@` or `Customerservice@`. Their Email 1 already asks them to pass it
  along to whoever runs the office.
- **Named people:** where the site names an owner or the person behind the published address, the
  greeting uses their first name (or "Dr. Lastname" for clinics). Otherwise it's "Hi {business} team".
- **Odd addresses to double-check:** Marquardt Chiropractic shows an outlook.com address but its email
  link goes to a Gmail address (the list uses the Gmail one). Hyalite Family Dentistry's displayed
  Gmail is used because the link behind it is a website-template placeholder. Debbie Lattin Insurance
  publishes `spencer@letusshop.com` and McDermott Financial publishes `admin@mcdermottfinancial.com`,
  both on domains different from their websites, but those are the addresses their own sites give.
  Kootenai Title's email is hidden behind Cloudflare's spam protection on their site; the address in
  the list is what that decodes to.
- **Vocal Credit Union** got a new CEO on 1 Oct 2026 (per their site). The opener mentions it, so check
  it's still accurate.

## Rules for every message

- Don't claim the pack makes anyone compliant with any law, standard or insurance requirement. Say only
  that the attendance log and certificates help keep a record (see Branch C).
- Don't quote loss figures or "X% of businesses" stats unless you've checked the latest FBI IC3 report
  and can link it.
- Don't use fear. The emails are written to be calm and helpful; keep them that way.
- Never invent a testimonial or say other local offices use it until they actually do.

## What to expect

Honest numbers for hand-written cold email to small local offices: a 5 to 10% reply rate is a good
result, and the free poster should get more yeses than a straight sales pitch would. From 75 leads, a
realistic target is 5 to 10 replies, 4 to 8 posters sent, and 1 to 3 pack sales ($99 each) over the next
4 weeks. The real value is learning which niche says yes most, so that the next 75 can all come from it.
