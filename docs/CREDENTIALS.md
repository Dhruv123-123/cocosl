# Credentials and accounts: what only you can do

The software does everything else. These steps need your identity, your accounts or your signature.
Do them in this order; the first four unlock money, the rest unlock automation.

Every value goes in `.env` (copy `.env.example`). `factory status` shows what's still missing.

## 1. Get paid (30 minutes)

| Do this | Why | Where it goes |
|---|---|---|
| Create a Stripe account and finish identity + bank verification | Client invoices and product sales | `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET` (webhook to `https://<your-host>/webhooks/stripe`) |
| Create a Gumroad (or Lemon Squeezy / Stan) account, add payout details | Sell the 20-Minute Budget product today | Product URL into `brands/money-made-simple.yaml` → `products`; optional ping to `/webhooks/gumroad?secret=<GUMROAD_WEBHOOK_SECRET>` |
| PayPal Business (optional) | Some small brands prefer it | Put instructions in `FACTORY_PAYMENT_INSTRUCTIONS` |
| Tax info (W-9 in the US) in each platform | Payouts are held without it | In each platform's settings |

## 2. Your sender identity (10 minutes)

CAN-SPAM requires a real name and postal address on every outreach email. A PO box or virtual mailbox is fine.
Fill in `FACTORY_SENDER_NAME`, `FACTORY_SENDER_BUSINESS`, `FACTORY_SENDER_EMAIL`, `FACTORY_SENDER_WEBSITE`,
`FACTORY_SENDER_ADDRESS`. Send pitches yourself from that inbox; the factory only drafts them.

## 3. Affiliate programs (apply today, approval takes days)

Apply only for products you'd recommend to a friend. For the finance brand: a high-yield savings account
referral program (confirm the bank is FDIC-insured), budgeting tools, and Amazon Associates for books.
Put each approved link in the brand YAML under `affiliates` (name, url, slug, keywords), then run
`factory links sync`. Captions automatically get a disclosure; the guardrail blocks posts without one.

## 4. Writing and voice

| Value | How |
|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com → API keys. Without it the factory writes placeholder drafts. |
| Voice, free: **Kokoro** (`KOKORO_URL`) | Easiest free option and sounds natural. On your server: `docker compose --profile kokoro up -d` and set `KOKORO_URL=http://kokoro:8880`. On a laptop: `docker run -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:v0.2.4` and `KOKORO_URL=http://localhost:8880`. Pick a voice with `KOKORO_VOICE` (e.g. `af_heart`, `am_michael`, `bf_emma`). These are synthetic stock voices, so the AI-voice disclosure stays on. |
| or your own cloned voice: `ELEVENLABS_API_KEY` + `ELEVENLABS_VOICE_ID` | Clone **your own** voice (or pick a licensed library voice). Never clone someone else's. |
| or `OPENAI_API_KEY` | Uses OpenAI TTS (and gpt-image-1 for images). |
| or Kokoro (free, local, recommended) | `docker compose --profile kokoro up -d`, set `KOKORO_URL=http://localhost:8880` (or `http://kokoro:8880` inside compose). Spanish brands get a Spanish voice (`KOKORO_VOICE_ES`, default `ef_dora`). Kokoro's model and voices are Apache-2.0, so narration is safe to monetize. |
| or Piper (free, local) | `pip install piper-tts`, download a voice, set `PIPER_MODEL=/path/voice.onnx`. |
| Images: `COMFYUI_URL` or `OPENAI_API_KEY` or `REPLICATE_API_TOKEN` | Without one, the factory uses its built-in abstract art (fine for carousels). |
| Music: `FACTORY_MUSIC_DIR` | A folder of tracks you have a licence for (YouTube Audio Library, Epidemic, etc.). Keep the licences. |

After adding a voice, re-voice everything that was rendered silent in one go: `factory renderq revoice`
(add `--include-approved` for approved posts; they go back to review). With Docker the `renderer` service
picks the jobs up by itself; without it run `factory renderq run`. `factory status` shows progress.

## Running more than one brand

Each brand should post to its own accounts. App-level keys (`YT_CLIENT_ID`, `META_APP_ID`, `TIKTOK_CLIENT_KEY`...)
are shared; account tokens go under the brand's name: run the auth commands with `--brand`, e.g.
`factory auth youtube --brand tiny-histories`, and the tokens are saved as `TINY_HISTORIES__YT_REFRESH_TOKEN` etc.
Any platform key can be set per brand this way (for example `TINY_HISTORIES__IG_USER_ID`); a brand without its own key falls back to the shared one. `factory doctor` lists each brand's connections.

## 5. Social accounts (create these by hand, one per platform for the brand)

Create the Instagram, YouTube and TikTok accounts yourself with the handle in the brand YAML.
Switch Instagram to a **Professional (Creator or Business)** account and link it to a Facebook Page.
Upload the brand kit (`output/<brand>/brand-kit/`): profile picture, banner, bios.

## 6. Platform API access

### Meta: Instagram, Facebook Page, Threads
1. developers.facebook.com → Create app → use case "Manage everything on your Page" / Facebook Login for Business. Add the Instagram product (and the Threads use case for Threads).
2. Permissions: `instagram_basic`, `instagram_content_publish`, `instagram_manage_insights`, `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `read_insights`, `instagram_manage_comments` (comment inbox; App Review for Advanced Access); Threads: `threads_basic`, `threads_content_publish`, `threads_manage_insights`.
3. Your own accounts work in Development mode (add yourself as an app role / Threads tester). No App Review is needed for your own accounts.
4. In Graph API Explorer, generate a user token with those permissions, then:
   `factory auth meta --token <short-lived-token>` → writes `FB_PAGE_ID`, `FB_PAGE_TOKEN`, `IG_USER_ID`, `IG_ACCESS_TOKEN`.
5. `META_APP_ID`, `META_APP_SECRET` from the app's Basic settings.
6. Instagram fetches media from a public HTTPS URL: serve `output/` (the `media` service in docker-compose behind Caddy or a Cloudflare Tunnel) and set `PUBLIC_MEDIA_BASE_URL`.

Limits: Instagram 100 API posts per 24h, Facebook Reels 30 per 24h, Threads 250 per 24h. The brand cadence caps are far lower.

### YouTube
1. console.cloud.google.com → new project → enable **YouTube Data API v3**.
2. OAuth consent screen (External), add yourself as a test user, scopes `youtube.upload`, `youtube.readonly`, `youtube.force-ssl` (needed to send comment replies from the inbox; re-run `factory auth youtube` if you connected before).
3. Credentials → OAuth client ID → **Desktop app** → `YT_CLIENT_ID`, `YT_CLIENT_SECRET`.
4. `factory auth youtube` → browser consent → writes `YT_REFRESH_TOKEN`.
5. While the consent screen is in "Testing", refresh tokens expire after 7 days. Publish the app (Google verification for sensitive scopes) for permanent tokens, or re-run step 4 weekly.
6. Verify your channel (phone) to enable custom thumbnails. Uploads default to private (`YT_PRIVACY=private`) so you flip them public after a last look.

### TikTok
1. developers.tiktok.com → create app → add **Login Kit** and **Content Posting API** (Direct Post).
2. Scopes: `user.info.basic`, `video.publish`, `video.upload`, `video.list`.
3. Register redirect URI `http://127.0.0.1:8765/callback/`. `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`.
4. `factory auth tiktok` → writes tokens; they refresh automatically before each publish.
5. **Until TikTok audits your app, every API post is private (SELF_ONLY).** Submit the audit from the developer portal. Until then, download the rendered video from the dashboard and post it from the TikTok app with the "AI-generated" label switched on.

### Postiz (optional alternative)
Self-host Postiz, connect the channels in its UI, create a Public API key: `POSTIZ_URL`, `POSTIZ_API_KEY`, `POSTIZ_INTEGRATION_IDS`.

## 7. Email list
`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` from any transactional email provider
(Postmark, Resend, Amazon SES), with SPF/DKIM set on your domain. Or export subscribers to Beehiiv/ConvertKit.
`BUSINESS_ADDRESS` is printed in every newsletter (CAN-SPAM).

## 8. Hosting (for the dashboard, link page and webhooks)
Any $5-10/month VPS with Docker: `docker compose up -d`. Put Caddy or a Cloudflare Tunnel in front for HTTPS.
Set `DASHBOARD_TOKEN` first. Point a domain at it for `/l/<brand>` (link in bio), `/go/<slug>` (tracked links),
`/webhooks/*` and media.

## 9. Flip the switch
Keep `FACTORY_DRY_RUN=1` until `factory status` shows the platforms ready and one manual test post looks right.
Then set `FACTORY_DRY_RUN=0`.
