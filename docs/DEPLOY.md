# Deploying

You need a small Linux server ($5-10/month: Hetzner, DigitalOcean, Lightsail) with Docker, and a domain.

1. `git clone` this repo onto the server and `cp .env.example .env`. Fill in at least `DASHBOARD_TOKEN`,
   `ANTHROPIC_API_KEY`, `FUNNEL_PUBLIC_URL=https://studio.yourdomain.com`,
   `PUBLIC_MEDIA_BASE_URL=https://media.yourdomain.com`, `FACTORY_LINK_BASE_URL=https://studio.yourdomain.com`.
2. Point `studio.` and `media.` DNS records at the server and edit the domains in `deploy/Caddyfile`.
3. `docker compose -f docker-compose.yml -f deploy/docker-compose.caddy.yml up -d`
4. Open `https://studio.yourdomain.com`, log in with `DASHBOARD_TOKEN`.
5. Connect platforms from your laptop (the OAuth helpers open a local browser):
   `factory auth youtube`, `factory auth tiktok`, `factory auth meta --token ...`, then copy the new lines
   from your local `.env` to the server's `.env` and `docker compose restart`.
6. Set the Stripe webhook to `https://studio.yourdomain.com/webhooks/stripe` (events: checkout.session.completed,
   charge.succeeded) and the Gumroad ping to `https://studio.yourdomain.com/webhooks/gumroad?secret=<GUMROAD_PING_SECRET>`.
7. Put `https://studio.yourdomain.com/l/<brand>` in each profile's link in bio.

Backups: everything lives in `data/` (SQLite + rendered media). A nightly `tar czf` of it to cloud storage is enough.

No server yet? Everything also runs on a laptop: `factory serve` and `python -m contentfactory.worker`.
The static link page (`factory linkpage <brand>`) and the ad-studio site (`launch/ugc-service/index.html`)
can be hosted free on Netlify Drop or GitHub Pages; only signups and webhooks need the server.
