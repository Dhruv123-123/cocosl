# Dinero Simple: channel-name reservation checklist (for an April 2027 YouTube start)

**Dhruv does every step here; nothing has been reserved or created.** This follows scouting's memos on PR #2:
`spanish-youtube-timing.md` and `domains-and-names.md`. The plan is to reserve the name now, for free, upload
nothing, and post first in **April 2027**, after the lean review. April is Financial Literacy Month, and late
April to 10 May is the Mother's Day remittance season.

## Timeline

| When | Step | Done |
|---|---|---|
| **Now (Nov–Dec 2026)** | Check the name (below), register the domain, reserve the **YouTube** handle and set up the channel page. Upload nothing | ☐ |
| **Jan 2027** | Paid 2-hour reviewer test (`reviewer/`). Reserve the other platforms' handles **now, not earlier** (see "Don't reserve too early") | ☐ |
| **Feb–Mar 2027** | Lean review (native + attorney), fixes, import, gate passes (`reviewer/WORKFLOW.md`) | ☐ |
| **Late Mar 2027** | Go-live check (bottom of this page) | ☐ |
| **Apr 2027** | First uploads from `POSTING_PLAN_LEAN.md` | ☐ |

## 1. Check the name first (30 minutes)

- ☐ Look at what **dinerosimple.com** shows. It was registered in 2020 and expires on 4 Oct 2027. If it's an
  active finance site, use a more distinct domain and handle (the alternatives are below).
- ☐ Search **tmsearch.uspto.gov** for "Dinero Simple" in classes 9, 16, 35, 36 and 41. A live mark in class 36 or 41
  with a near-identical name is a stop. Then ask the coordinator for a rename study.
- ☐ Search YouTube, TikTok and Instagram for "Dinero Simple" to see if an active creator already uses it.

## 2. Domain

- ☐ Register **eldinerosimple.com**, the first choice and natural Spanish. Alternatives: midinerosimple.com,
  dinerosimpleus.com, holadinerosimple.com, dinerosimplehq.com. Re-check availability at checkout. They were all
  free on 2026-11-07.
- ☐ Use Cloudflare Registrar (sold at cost), with auto-renew and WHOIS privacy on.
- ☐ Point it at the Netlify site, and set `url` in `sites/dinero-simple/site.json`.

## 3. Handle: one handle everywhere

Try these in order, and take the first one that is free **on all** the platforms you'll use:

1. `@dinerosimple`
2. `@eldinerosimple` (matches the domain above; if you take this domain, prefer this handle)
3. `@midinerosimple`
4. `@dinerosimple.us`

If the domain and the handle can't match, **match the handle to the domain**, because people type what they hear.
The brand files say `@dinerosimple`. If you take another handle, tell the thread so `brands/dinero-simple.yaml`
and the site's `socials` get updated.

## 4. YouTube channel (now)

- ☐ Create the channel as a **Brand Account** under Dhruv's Google account, so a reviewer or helper can be added as
  a manager later without sharing a password. Turn on 2-step verification.
- ☐ Channel name **Dinero Simple**; handle from step 3.
- ☐ Studio → Settings → Channel → Basic info:
  - country **United States**;
  - channel language **Spanish (Latin America)**, or **Spanish** if that isn't offered.
- ☐ Studio → Settings → Upload defaults:
  - video language Spanish;
  - title and description language Spanish;
  - category Education.
- ☐ Turn on the altered or synthetic content setting where YouTube offers it as a default, to match the brand's AI
  disclosure.
- ☐ Verify the phone number. This unlocks custom thumbnails and uploads over 15 minutes.
- ☐ Description:
  - use `bios.youtube_about` in `brands/dinero-simple.yaml`, **after** native review;
  - until then, leave it blank or one neutral line: "Dinero Simple: finanzas personales en español. Muy pronto."
- ☐ Branding: avatar and banner from the brand kit, project files `content-factory/dinero-simple/brand-kit/`.
- ☐ Links: the site, once its domain is live. No affiliate links.
- ☐ Comments → Settings → hold potentially inappropriate comments for review. Add blocked words for the scam
  patterns this audience gets: "CPN", "número nuevo", "whatsapp +", "inversión garantizada", "notario".
- ☐ Automatic dubbing: check the Studio setting, and turn it **off** for this channel. Its videos are already in
  Spanish.
- ☐ **Upload nothing.** No trailer and no test video until the go-live check below passes.

## 5. Other platforms (January, not now)

- ☐ **TikTok:** a personal account, **not Business**, to stay eligible for Creator Rewards.
- ☐ **Instagram + Threads:** they share one handle, so reserve both together.
- ☐ **Facebook Page:** Reels go here (the brand's platform plan).
- ☐ **Pinterest** (optional): claim the domain once it's live.
- ☐ **WhatsApp Channel:** create it only when you'll post in it (`WHATSAPP_CHANNEL.md`).

**Don't reserve too early.** Platforms can reclaim inactive accounts, and YouTube takes monetization away from
channels that have been idle for 6 or more months. Reserving YouTube in November and posting in April stays under
that. Reserve the rest in January so no account sits empty for long.

## 6. Go-live check (late March 2027)

- ☐ The native reviewer has signed off the lean set, and every lean post shows `approved` in the review gate
  (`reviewer/WORKFLOW.md`).
- ☐ The attorney has approved the standard lines and the two lean email rows.
- ☐ Someone fluent in Spanish can answer comments for **15 minutes a day**. No machine-translated replies to people
  asking about their own money or status.
- ☐ Kokoro's Spanish voice is set (`ef_dora` or `em_alex`), never the English voice.
- ☐ Every video carries the Spanish AI disclosure line.
- ☐ The channel description and bio are the reviewed versions.
- ☐ The site is live with the hold on, and the freebie and the Kit work end to end.
