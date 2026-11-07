# Deploying

You need a small Linux server ($5-10/month: Hetzner, DigitalOcean, Lightsail) with Docker, and a domain.

1. `git clone` this repo onto the server and `cp .env.example .env`. Fill in at least `DASHBOARD_TOKEN`,
   `ANTHROPIC_API_KEY`, `FUNNEL_PUBLIC_URL=https://studio.yourdomain.com`,
   `PUBLIC_MEDIA_BASE_URL=https://media.yourdomain.com`, `FACTORY_LINK_BASE_URL=https://studio.yourdomain.com`.
2. Point `studio.` and `media.` DNS records at the server and edit the domains in `deploy/Caddyfile`.
3. `docker compose -f docker-compose.yml -f deploy/docker-compose.caddy.yml --profile kokoro up -d`
   (drop `--profile kokoro` if you use ElevenLabs/OpenAI for voice; with it, set `KOKORO_URL=http://kokoro:8880`).
   This starts the dashboard, the worker (each brand's daily run on its own clock, publishing every 10 min),
   the renderer (videos render in the background) and the free Kokoro voice. Rendering a big backlog?
   `docker compose up -d --scale renderer=2`: jobs are claimed atomically, so two renderers never take the same one.
4. Open `https://studio.yourdomain.com`, log in with `DASHBOARD_TOKEN`.
5. Connect platforms from your laptop (the OAuth helpers open a local browser):
   `factory auth youtube`, `factory auth tiktok`, `factory auth meta --token ...`, then copy the new lines
   from your local `.env` to the server's `.env` and `docker compose restart`.
6. Set the Stripe webhook to `https://studio.yourdomain.com/webhooks/stripe` (events: checkout.session.completed,
   charge.succeeded) and the Gumroad ping to `https://studio.yourdomain.com/webhooks/gumroad?secret=<GUMROAD_PING_SECRET>`.
7. Put `https://studio.yourdomain.com/l/<brand>` in each profile's link in bio.

Health: `docker compose exec app factory status` (or `GET /api/status` with your token) shows the worker's
last tick, the publishing and render queues, and anything that needs you, such as an upload that was
interrupted (marked `needs_check` and never retried automatically, so nothing posts twice).

Backups: set `BACKUP_DIR=/data/backups` (or a mounted bucket) and the worker takes a consistent database backup every day, keeping 14 (`factory backup` does one now). Rendered media in `data/output` can be re-rendered, but sync it to cloud storage too if you want instant restores.

No server yet? Everything also runs on a laptop: `factory serve`, `python -m contentfactory.worker` and
`python -m contentfactory.renderq` (or leave `RENDER_QUEUE` unset to render inline).
The static link page (`factory linkpage <brand>`) and the ad-studio site (`launch/ugc-service/index.html`)
can be hosted free on Netlify Drop or GitHub Pages; only signups and webhooks need the server.
