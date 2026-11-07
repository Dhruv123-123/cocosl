"""`factory auth ...`: one-time platform connection. Tokens go into .env."""
from __future__ import annotations

import sys
import time


def _need(settings, *keys):
    missing = [k for k in keys if not settings.env(k)]
    if missing:
        sys.exit(f"Set {', '.join(missing)} in .env first (see docs/CREDENTIALS.md)")


def cmd_auth(args, factory_fn):
    from . import oauth
    from .tokens import write_env
    f = factory_fn(args)
    s = f.settings
    if getattr(args, "brand", None):
        f.brand(args.brand)  # must exist
        s = s.for_brand(args.brand)
    env = s.home / ".env"
    _write = write_env

    def write_env(path, values):  # noqa: F811 - per-brand names when --brand is given
        _write(path, {s.env_key(k, write_scoped=bool(s.brand_scope)): v for k, v in values.items()})
    if args.platform == "youtube":
        _need(s, "YT_CLIENT_ID", "YT_CLIENT_SECRET")
        tok = oauth.youtube_authorize_interactive(s.env("YT_CLIENT_ID"), s.env("YT_CLIENT_SECRET"),
                                                  open_browser=not args.no_browser)
        if not tok.get("refresh_token"):
            sys.exit("Google returned no refresh token. Remove the app's access at myaccount.google.com/permissions and retry.")
        write_env(env, {"YT_REFRESH_TOKEN": tok["refresh_token"]})
        print("YouTube connected. YT_REFRESH_TOKEN saved to .env")
    elif args.platform == "tiktok":
        _need(s, "TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET")
        tok = oauth.tiktok_authorize_interactive(s.env("TIKTOK_CLIENT_KEY"), s.env("TIKTOK_CLIENT_SECRET"),
                                                 port=args.port, open_browser=not args.no_browser)
        write_env(env, {"TIKTOK_ACCESS_TOKEN": tok["access_token"], "TIKTOK_REFRESH_TOKEN": tok["refresh_token"],
                        "TIKTOK_TOKEN_EXPIRES_AT": str(int(time.time() + int(tok.get("expires_in", 7200))))})
        print("TikTok connected. Tokens saved to .env (they refresh automatically before publishing)")
    elif args.platform == "meta":
        _need(s, "META_APP_ID", "META_APP_SECRET")
        if not args.token:
            sys.exit("Pass --token <short-lived user token> from Graph API Explorer (see docs/CREDENTIALS.md)")
        long = oauth.meta_long_lived_user_token(s.env("META_APP_ID"), s.env("META_APP_SECRET"), args.token)
        pages = oauth.meta_pages(long["access_token"])
        if not pages:
            sys.exit("No Facebook Pages found for this user. Create a Page and link your Instagram account to it.")
        page = next((p for p in pages if p["id"] == args.page), None) if args.page else pages[0]
        if page is None:
            sys.exit(f"Page {args.page} not found. Pages: " + ", ".join(f"{p['id']} ({p['name']})" for p in pages))
        values = {"FB_PAGE_ID": page["id"], "FB_PAGE_TOKEN": page["access_token"],
                  "IG_ACCESS_TOKEN": page["access_token"]}
        ig = (page.get("instagram_business_account") or {}).get("id")
        if ig:
            values["IG_USER_ID"] = ig
        write_env(env, values)
        print(f"Connected Page '{page['name']}'" + (f" and Instagram account {ig}" if ig else
              " (no Instagram account linked to this Page)"))
        if len(pages) > 1 and not args.page:
            print("Other pages: " + ", ".join(f"{p['id']} ({p['name']})" for p in pages[1:]) + " (use --page)")
    elif args.platform == "threads":
        _need(s, "META_APP_SECRET")
        if not (args.token and args.user_id):
            sys.exit("Pass --token <short-lived Threads token> and --user-id <Threads user id>")
        d = oauth.threads_long_lived_token(s.env("META_APP_SECRET"), args.token)
        write_env(env, {"THREADS_ACCESS_TOKEN": d["access_token"], "THREADS_USER_ID": args.user_id,
                        "THREADS_TOKEN_EXPIRES_AT": str(int(time.time() + int(d.get("expires_in", 0))))})
        print("Threads connected.")


def register(sub, factory_fn) -> None:
    s = sub.add_parser("auth", help="connect a platform account (writes tokens to .env)")
    s.add_argument("platform", choices=["youtube", "tiktok", "meta", "threads"])
    s.add_argument("--token", help="short-lived token (meta/threads)")
    s.add_argument("--page", help="Facebook Page id (meta)")
    s.add_argument("--brand", help="save tokens for this brand only (e.g. a second brand's own accounts)")
    s.add_argument("--user-id", help="Threads user id")
    s.add_argument("--port", type=int, default=8765, help="local callback port (tiktok)")
    s.add_argument("--no-browser", action="store_true")
    s.set_defaults(func=lambda a: cmd_auth(a, factory_fn))
