# Text-us scam check: setup

People forward a suspicious text (or paste an email) to a phone number and get a short verdict
back, using the same checks as the website. The code is done and tested
(`sms/sms.mjs`, `netlify/functions/sms.mjs`, `test/sms.test.js`). What's left is accounts and
settings. Nothing here sends a message until you connect a number.

Prices and registration rules change: check the items marked **verify** on Twilio's pages.

## What it does

- Checks every request really comes from Twilio (signature check with your auth token).
- Replies in plain text that fits in two SMS segments, without emoji, so each reply costs at
  most 2 segments.
- High risk: "HIGH RISK: this looks like a scam (fake delivery notice). Red flags: ... Don't tap
  links, reply or call back..."
- Nothing found: "No common scam signs found. That isn't proof it's safe..." It never says a
  message is safe.
- 5 free checks per number per month (change with `SMS_FREE_CHECKS`). After that it replies
  with your family-plan link. Numbers in `SMS_UNLIMITED_NUMBERS` never run out.
- HELP gets a help reply. Pictures get "we can only read text". STOP, START and HELP opt-outs
  are also handled by Twilio itself (Advanced Opt-Out, on by default).
- **Privacy:** message text is checked in memory and never stored or logged. Usage counts are
  stored under a salted hash of the phone number, not the number, and expire after about 40 days.

## Steps

1. **Twilio account** (twilio.com). Upgrade from trial so you can text any number.
2. **Get a number and register it.** US carriers block unregistered business texting:
   - **Toll-free number** (simplest for this): submit toll-free verification in the Twilio
     console. Use case: "customer care / account notifications: users text us a message, we reply
     with an automated scam-risk check." Opt-in: the user texts us first.
   - Or a local 10-digit number with **A2P 10DLC** brand + campaign registration (there are
     one-time and monthly registration fees; **verify**).
   Expect a few days to a few weeks for approval. Budget roughly $1 to $2 a month per number plus
   about a cent per segment each way, plus carrier fees (**verify** current pricing).
3. **Shared usage counter (free):** create a free Redis database at upstash.com and copy its REST
   URL and token. Without it the counts live in the function's memory and reset whenever it
   restarts, which is fine for testing but not live.
4. **Netlify environment variables** (Site settings > Environment variables) on the site that
   serves `scam-checker` (or the all-in-one `apps` site):

   | Variable | Value |
   |---|---|
   | `TWILIO_AUTH_TOKEN` | Twilio console > Account info > Auth token |
   | `SMS_HASH_SALT` | Any long random string. Don't change it later, or counts reset |
   | `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN` | From step 3 |
   | `SMS_UPGRADE_URL` | Optional: your family plan checkout link |
   | `SMS_CHECKER_URL` | Optional: short link to the web checker, added to replies |
   | `SMS_UNLIMITED_NUMBERS` | Optional: family-plan numbers, comma-separated, like `+15551234567` |
   | `SMS_FREE_CHECKS` | Optional: free checks per month (default 5) |
   | `TWILIO_WEBHOOK_URL` | Only if the signature check fails behind a custom domain: the exact URL set in Twilio |

5. **Point the number at the function:** Twilio console > Phone Numbers > your number >
   Messaging > "A message comes in" > Webhook, HTTP POST,
   `https://YOUR-SITE/api/sms`.
6. **Test:** text the number a known scam (for example a fake USPS "package held" text). You
   should get a HIGH RISK reply within a few seconds. Then text "hi" and check you get the
   "no common scam signs" reply.

## Family plan

The simplest version: sell a $3/month "Scam Shield family plan" on Gumroad or a Stripe Payment
Link, ask for the phone numbers at checkout, and add them to `SMS_UNLIMITED_NUMBERS`. If it
sells, the next step is to read active subscriptions from Gumroad/Stripe automatically, like the
budget app's license check does.

## Wording rules

The replies never say a message is safe or certain to be a scam ("looks like", "scam signs",
"isn't proof it's safe"). Keep it that way if you edit `verdictText` in `sms/sms.mjs`.
