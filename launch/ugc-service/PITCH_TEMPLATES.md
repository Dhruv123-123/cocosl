# Pitch templates

Send these **yourself, one at a time, from your own inbox**, after looking at the lead's store. Personalise
the `{curly}` parts every time. The first line must prove you actually looked at their business. A pitch
that could have gone to anyone gets ignored (and gets you flagged as spam).

## Rules (read once)

- **Volume:** 10–20 a day, by hand. No mass-mailing tools, no purchased lists, no scraped emails.
- **Only business contact details they published** (contact page, store footer, "wholesale/press" email).
  Never guess personal emails.
- **CAN-SPAM** (US) requires: no misleading subject or "From", your real name, a valid postal address,
  a clear way to opt out, and honouring opt-outs within 10 business days. Use the footer below every time.
- **Outside the US** (UK/EU/Canada) rules for cold B2B email are stricter. Email only generic business
  addresses (hello@, info@, wholesale@), keep it relevant to their business, and always include the opt-out.
  For Canada (CASL), only email addresses that are conspicuously published, with no "no unsolicited email"
  notice, and keep the message relevant to their business role.
- **One follow-up per thread is normal, two is the max.** If they say no or ask you to stop: stop,
  and mark them `do_not_contact` in `leads.csv` notes.
- **Never claim results you don't have.** No "I've helped 50 brands", no ROAS numbers, no client names
  until you have real, permitted ones.
- Subject lines: plain, specific, lowercase-ish. No "RE:" or "FWD:" on a first email (that's deceptive).

## Compliance footer (paste under every email)

```
--
{Your Name} · {Studio Name}
{Street address or PO box / registered mailbox}, {City, Postcode}, {Country}
Not interested? Reply "no thanks" and I won't email again.
```

A PO box or a registered virtual mailbox (e.g. a UPS Store box) is fine if you don't want to use your home address.

---

## Email 1: The free sample (default, best reply rate)

**Subject:** quick video idea for {product name}

```
Hi {first name},

{One genuine, specific line about their store, e.g. "The refillable glass version of your
{product} is a really smart answer to the plastic bottle problem."}

I make short vertical video ads for small brands, using AI presenters (always labeled as AI,
spokesperson and demo style, never fake customer reviews). They're a cheap way to test a lot of
hooks on TikTok, Reels and Shorts before paying for big shoots.

Would it be useful if I made one free 20-second sample ad for {product name}, from your
existing product photos? No cost and no obligation. If it's not useful, just say so.

Thanks,
{Your Name}
{Studio site URL}

{footer}
```

## Email 2: The "I noticed your ads" angle (for brands visible in the Meta Ad Library)

**Subject:** more hook variations for {brand}'s ads?

```
Hi {first name},

I saw {brand} is running ads for {product} at the moment (the one opening with
"{their current first line/hook}").

Brands that test lots of hooks usually find winners faster, but shooting 10 versions is
expensive. I make AI-presented vertical ads (clearly labeled as AI, no fake reviews) where
each ad comes with 3 different opening hooks to test against each other.

My Growth pack is 8 ads x 3 hooks for $449, delivered in 10 days. Happy to make one free
sample with 2 hook variations first, so you can judge the quality before spending anything.

Worth a look?

{Your Name}
{Studio site URL}

{footer}
```

## Email 3: Local business (cafe, gym, salon, clinic, trades)

**Subject:** short video ads for {business name}

```
Hi {first name or "there"},

I'm {Your Name}, based in {your city/area}. I came across {business name} {where: on Google
Maps / walking past on {street} / on Instagram} and liked {specific thing: the seasonal menu,
the before/after work on your page, your class schedule}.

I make short vertical videos for local businesses to use on Instagram, Facebook and TikTok,
for things like {relevant example: a new menu launch, a membership offer, booking reminders}.
They use an AI presenter and voice (clearly labeled as AI), plus your own photos, so there's
no filming day and no cost for actors.

Four videos are $249. Or I can make one free sample about {specific offer/service} so you
can see what it would look like. Want me to?

{Your Name}
{phone, optional}

{footer}
```

---

## Follow-up 1 (send 4–5 days later, same thread)

**Subject:** (reply in the same thread, keep original subject)

```
Hi {first name},

Just bumping this in case it got buried. Happy to make that free sample ad for
{product name}; it takes me about a day and there's no catch.

If now isn't the right time, no problem at all.

{Your Name}

{footer}
```

## Follow-up 2 (final, 7–10 days after follow-up 1)

```
Hi {first name},

Last note from me on this. I went ahead and wrote a 3-line hook idea for {product name}
in case it's useful for your own content, whether or not we work together:

  1. "{hook idea 1, e.g. 'Your water bottle shouldn't smell like last week.'}"
  2. "{hook idea 2}"
  3. "{hook idea 3}"

If you'd ever like those made into labeled AI video ads, just reply. Otherwise I won't
email again.

{Your Name}

{footer}
```

---

## Instagram DM (manual, from your studio account)

Send only to business accounts, only after you've looked at their recent posts, max ~10 a day.
Instagram restricts accounts that send many similar DMs quickly. Vary the first line every time, and
never use automation tools.

```
Hi! Love {specific post/product, e.g. "the colour-changing mugs in your latest reel"}.

I make short AI-presented video ads for small brands (labeled as AI, demo style, no fake
reviews). Would a free 20-second sample for {product} be useful? Totally fine if not!
```

If they reply yes: ask for the best email and which product, then move to email. If no reply, don't
follow up by DM more than once.

---

## The free sample ad playbook

**Why it works:** a small brand owner can't judge "AI video ads" in the abstract. They can judge a
20-second ad of their own product in 5 seconds. It turns a cold pitch into a show-and-tell.

**How to do it without losing your week**

1. **Only for qualified leads** (score 4+ in `LEAD_CRITERIA.md`). Max 3 samples a week, and only
   after they say yes. Don't make samples "on spec" for people who haven't replied; it's slow and it
   can read as pushy.
2. **Use their public assets**: product page photos and copy. Don't use their customer reviews or
   UGC in the ad, and don't use any person's face from their site.
3. **Make it in under 90 minutes**: one script (spokesperson or demo, never "I bought this"),
   one hook, 15–20s, captions, on-screen "AI-generated presenter" label, and a corner "SAMPLE" watermark.
   The factory can draft it: `business/ugc.py` writes a compliant script from a brief.
4. **Deliver as a private, unlisted link** (Google Drive / Vimeo / Loom) with this note:

```
Hi {first name}, here's the sample for {product}: {link}

It's yours to keep for organic posts. If you'd like a version for paid ads or more like it:
- Starter: 4 ads for $249 (7 days)
- Growth: 8 ads x 3 hooks for $449 (10 days), best if you're running paid social
The sample's value ($62) comes off either package if you order in the next 30 days.

Happy to tweak the hook or angle first if you'd like to see a different approach.

{Your Name}
```

5. **One follow-up 3 days later** if no reply. Then let it go.

## Reply snippets

**"How much?"** → "Starter is 4 ads for $249, Growth is 8 ads with 3 hook versions each for $449.
Full details: {site}#pricing. Happy to do a free sample first."

**"Is it AI? Will people know?"** → "Yes, and yes, on purpose: each ad has an on-screen AI label, and I
recommend ticking the platform's AI-content label too. They work as spokesperson/demo ads, not fake
customer reviews, which keeps them within ad policies and FTC rules."

**"Can the presenter say they love it / use it?"** → "I can't do that one: an AI presenter claiming to use
a product would be a fake testimonial. What works just as well is the presenter showing and explaining the
product, plus real review quotes from your customers shown as text, if you have permission to use them."

**"Send me examples"** → link your portfolio of the 5 sample ads (fictional brands, see `SAMPLE_ADS.md`)
and offer the free sample.
