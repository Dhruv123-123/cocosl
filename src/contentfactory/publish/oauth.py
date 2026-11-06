"""One-time credential setup helpers (called by `factory auth <platform>`).

Nothing here prints or logs secrets: every function returns the token data
and the CLI decides what to store (normally by writing to `.env`). URLs that
are safe to show (authorization URLs) contain no secrets.

Docs used:
- Google OAuth for installed apps (loopback + PKCE):
  https://developers.google.com/identity/protocols/oauth2/native-app
- TikTok Login Kit for desktop (PKCE, localhost redirect):
  https://developers.tiktok.com/docs/en/login-kit-desktop
- TikTok token exchange / refresh:
  https://developers.tiktok.com/doc/oauth-get-a-user-access-token
  https://developers.tiktok.com/docs/en/oauth-user-access-token-management
- Meta long-lived user/Page tokens:
  https://developers.facebook.com/documentation/facebook-login/guides/access-tokens/get-long-lived
- Instagram Login long-lived token exchange/refresh:
  https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login/business-login
- Threads long-lived tokens:
  https://developers.facebook.com/documentation/threads/get-started/long-lived-tokens
"""
from __future__ import annotations

import base64
import hashlib
import http.server
import secrets
import threading
import urllib.parse
from dataclasses import dataclass, field

import httpx

from ._http import GRAPH_API_VERSION, THREADS_API_VERSION, ApiClient

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]
TIKTOK_AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TIKTOK_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
# video.list is only needed for metrics (Display API video query).
TIKTOK_SCOPES = ["user.info.basic", "video.publish", "video.upload", "video.list"]
GRAPH = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
IG_GRAPH = "https://graph.instagram.com"
THREADS_GRAPH = "https://graph.threads.com"


# --------------------------------------------------------------------------- PKCE
def pkce_pair(encoding: str = "base64url") -> tuple[str, str]:
    """Return (code_verifier, code_challenge) for S256.

    Google uses RFC 7636 base64url. TikTok's desktop guide says the challenge
    is the *hex* SHA-256 of the verifier, so pass encoding="hex" for TikTok.
    """
    verifier = secrets.token_urlsafe(64)[:96]
    digest = hashlib.sha256(verifier.encode()).digest()
    if encoding == "hex":
        return verifier, digest.hex()
    return verifier, base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


# --------------------------------------------------------------- local callback
@dataclass
class CallbackResult:
    params: dict[str, str] = field(default_factory=dict)

    @property
    def code(self) -> str:
        return self.params.get("code", "")

    @property
    def state(self) -> str:
        return self.params.get("state", "")

    @property
    def error(self) -> str:
        return self.params.get("error", "")


class LocalCallbackServer:
    """Tiny one-shot HTTP server on 127.0.0.1 that captures the OAuth redirect.

    Usage:
        with LocalCallbackServer(port=0, path="/callback/") as srv:
            url = youtube_auth_url(client_id, srv.redirect_uri, ...)
            ... open url ...
            result = srv.wait(timeout=300)
    `port=0` picks a free port (fine for Google loopback; TikTok needs the
    exact redirect URI registered, e.g. http://127.0.0.1:8765/callback/ or a
    wildcard-port registration).
    """

    def __init__(self, port: int = 0, path: str = "/", host: str = "127.0.0.1"):
        self.path = path
        self.result = CallbackResult()
        self._event = threading.Event()
        outer = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802 - stdlib name
                parsed = urllib.parse.urlparse(self.path)
                if parsed.path.rstrip("/") != outer.path.rstrip("/"):
                    self.send_response(404)
                    self.end_headers()
                    return
                outer.result = CallbackResult(dict(urllib.parse.parse_qsl(parsed.query)))
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"<p>Authorization received. You can close this tab and return to the terminal.</p>")
                outer._event.set()

            def log_message(self, *args):  # silence: the query contains the auth code
                pass

        self._server = http.server.HTTPServer((host, port), Handler)
        self.host = host
        self.port = self._server.server_address[1]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def redirect_uri(self) -> str:
        return f"http://{self.host}:{self.port}{self.path}"

    def __enter__(self) -> "LocalCallbackServer":
        self._thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self._server.shutdown()
        self._server.server_close()

    def wait(self, timeout: float = 300) -> CallbackResult:
        if not self._event.wait(timeout):
            raise TimeoutError("No OAuth redirect received in time")
        return self.result


def _client(platform: str, transport: httpx.BaseTransport | None) -> ApiClient:
    return ApiClient(platform, transport=transport)


# ---------------------------------------------------------------------- YouTube
def youtube_auth_url(client_id: str, redirect_uri: str, state: str, code_challenge: str,
                     scopes: list[str] | None = None) -> str:
    """Google consent URL for a Desktop-app OAuth client (loopback redirect).

    `access_type=offline` + `prompt=consent` make sure a refresh token comes
    back even if the account authorized the app before.
    """
    q = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(scopes or YOUTUBE_SCOPES),
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(q)}"


def youtube_exchange_code(client_id: str, client_secret: str, code: str, redirect_uri: str,
                          code_verifier: str, transport: httpx.BaseTransport | None = None) -> dict:
    """Exchange the auth code for tokens. Returns Google's JSON
    (`access_token`, `expires_in`, `refresh_token`, `scope`, `token_type`)."""
    return _client("youtube", transport).json("POST", GOOGLE_TOKEN_URL, what="token exchange", data={
        "client_id": client_id, "client_secret": client_secret, "code": code,
        "code_verifier": code_verifier, "grant_type": "authorization_code", "redirect_uri": redirect_uri,
    })


def youtube_refresh(client_id: str, client_secret: str, refresh_token: str,
                    transport: httpx.BaseTransport | None = None, client: ApiClient | None = None) -> dict:
    """Get a fresh access token from a stored refresh token."""
    api = client or _client("youtube", transport)
    return api.json("POST", GOOGLE_TOKEN_URL, what="token refresh", data={
        "client_id": client_id, "client_secret": client_secret,
        "grant_type": "refresh_token", "refresh_token": refresh_token,
    })


def youtube_authorize_interactive(client_id: str, client_secret: str, *, open_browser: bool = True,
                                  show=print, timeout: float = 300,
                                  transport: httpx.BaseTransport | None = None) -> dict:
    """Run the whole installed-app flow: local callback, consent URL, code
    exchange. Returns the token dict; store `refresh_token` as YT_REFRESH_TOKEN.
    `show` receives only the consent URL (no secrets)."""
    verifier, challenge = pkce_pair()
    state = secrets.token_urlsafe(16)
    with LocalCallbackServer(port=0, path="/") as srv:
        url = youtube_auth_url(client_id, srv.redirect_uri, state, challenge)
        show(f"Open this URL to authorize YouTube access:\n{url}")
        if open_browser:
            import webbrowser
            webbrowser.open(url)
        result = srv.wait(timeout)
    _check_callback(result, state)
    return youtube_exchange_code(client_id, client_secret, result.code, srv.redirect_uri, verifier, transport)


def _check_callback(result: CallbackResult, state: str) -> None:
    if result.error:
        raise RuntimeError(f"Authorization failed: {result.error} {result.params.get('error_description', '')}")
    if result.state != state:
        raise RuntimeError("OAuth state mismatch; aborting (possible CSRF)")
    if not result.code:
        raise RuntimeError("No authorization code in the redirect")


# ----------------------------------------------------------------------- TikTok
def tiktok_auth_url(client_key: str, redirect_uri: str, state: str, code_challenge: str | None = None,
                    scopes: list[str] | None = None) -> str:
    """TikTok Login Kit authorize URL. Desktop apps must send a PKCE
    challenge (hex SHA-256, see `pkce_pair("hex")`); web apps may omit it."""
    q = {
        "client_key": client_key,
        "response_type": "code",
        "scope": ",".join(scopes or TIKTOK_SCOPES),
        "redirect_uri": redirect_uri,
        "state": state,
    }
    if code_challenge:
        q.update(code_challenge=code_challenge, code_challenge_method="S256")
    return f"{TIKTOK_AUTH_URL}?{urllib.parse.urlencode(q)}"


def tiktok_exchange_code(client_key: str, client_secret: str, code: str, redirect_uri: str,
                         code_verifier: str | None = None, transport: httpx.BaseTransport | None = None) -> dict:
    """Exchange the code for `access_token` (2h), `refresh_token` (180d),
    `open_id`, `scope`. Store the access token as TIKTOK_ACCESS_TOKEN and the
    refresh token as TIKTOK_REFRESH_TOKEN."""
    data = {"client_key": client_key, "client_secret": client_secret, "code": code,
            "grant_type": "authorization_code", "redirect_uri": redirect_uri}
    if code_verifier:
        data["code_verifier"] = code_verifier
    return _tiktok_token(data, transport)


def tiktok_refresh(client_key: str, client_secret: str, refresh_token: str,
                   transport: httpx.BaseTransport | None = None) -> dict:
    """Refresh a TikTok access token. The refresh token may rotate: always
    store the returned `refresh_token`."""
    return _tiktok_token({"client_key": client_key, "client_secret": client_secret,
                          "grant_type": "refresh_token", "refresh_token": refresh_token}, transport)


def _tiktok_token(data: dict, transport: httpx.BaseTransport | None) -> dict:
    body = _client("tiktok", transport).json(
        "POST", TIKTOK_TOKEN_URL, what="token", data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    if body.get("error") and not body.get("access_token"):
        raise RuntimeError(f"TikTok token error: {body.get('error')} {body.get('error_description', '')}")
    return body


def tiktok_authorize_interactive(client_key: str, client_secret: str, *, port: int = 8765,
                                 path: str = "/callback/", open_browser: bool = True, show=print,
                                 timeout: float = 300, transport: httpx.BaseTransport | None = None) -> dict:
    """Desktop flow: register http://127.0.0.1:<port><path> as a redirect URI
    in the TikTok app's Login Kit settings first."""
    verifier, challenge = pkce_pair("hex")
    state = secrets.token_urlsafe(16)
    with LocalCallbackServer(port=port, path=path) as srv:
        url = tiktok_auth_url(client_key, srv.redirect_uri, state, challenge)
        show(f"Open this URL to authorize TikTok access:\n{url}")
        if open_browser:
            import webbrowser
            webbrowser.open(url)
        result = srv.wait(timeout)
    _check_callback(result, state)
    return tiktok_exchange_code(client_key, client_secret, result.code, srv.redirect_uri, verifier, transport)


# ------------------------------------------------------------------------- Meta
def meta_long_lived_user_token(app_id: str, app_secret: str, short_lived_token: str,
                               transport: httpx.BaseTransport | None = None) -> dict:
    """Exchange a short-lived Facebook user token (e.g. from Graph API
    Explorer) for a ~60-day one. Returns {access_token, token_type, expires_in}."""
    return _client("meta", transport).json("GET", f"{GRAPH}/oauth/access_token", what="token exchange", params={
        "grant_type": "fb_exchange_token", "client_id": app_id, "client_secret": app_secret,
        "fb_exchange_token": short_lived_token})


def meta_pages(user_token: str, transport: httpx.BaseTransport | None = None) -> list[dict]:
    """Pages the user manages, each with a Page access token (no fixed expiry
    when derived from a long-lived user token) and its linked Instagram
    professional account id if any. Use these for FB_PAGE_TOKEN, IG_USER_ID."""
    api = _client("meta", transport)
    body = api.json("GET", f"{GRAPH}/me/accounts", what="list pages", params={
        "fields": "id,name,access_token,tasks,instagram_business_account", "access_token": user_token})
    return body.get("data", [])


def meta_find_ig_user_id(page_id: str, page_token: str, transport: httpx.BaseTransport | None = None) -> str:
    """The Instagram professional account id linked to a Facebook Page."""
    body = _client("meta", transport).json("GET", f"{GRAPH}/{page_id}", what="page lookup", params={
        "fields": "instagram_business_account", "access_token": page_token})
    ig = (body.get("instagram_business_account") or {}).get("id")
    if not ig:
        raise RuntimeError("This Page has no linked Instagram professional account")
    return ig


def instagram_login_long_lived_token(app_secret: str, short_lived_token: str,
                                     transport: httpx.BaseTransport | None = None) -> dict:
    """Instagram API with Instagram Login: short-lived -> 60-day token."""
    return _client("instagram", transport).json("GET", f"{IG_GRAPH}/access_token", what="token exchange", params={
        "grant_type": "ig_exchange_token", "client_secret": app_secret, "access_token": short_lived_token})


def instagram_login_refresh_token(long_lived_token: str, transport: httpx.BaseTransport | None = None) -> dict:
    """Refresh an Instagram-Login long-lived token (must be >=24h old and unexpired)."""
    return _client("instagram", transport).json("GET", f"{IG_GRAPH}/refresh_access_token", what="token refresh", params={
        "grant_type": "ig_refresh_token", "access_token": long_lived_token})


def threads_long_lived_token(app_secret: str, short_lived_token: str,
                             transport: httpx.BaseTransport | None = None) -> dict:
    return _client("threads", transport).json("GET", f"{THREADS_GRAPH}/access_token", what="token exchange", params={
        "grant_type": "th_exchange_token", "client_secret": app_secret, "access_token": short_lived_token})


def threads_refresh_token(long_lived_token: str, transport: httpx.BaseTransport | None = None) -> dict:
    return _client("threads", transport).json("GET", f"{THREADS_GRAPH}/refresh_access_token", what="token refresh", params={
        "grant_type": "th_refresh_token", "access_token": long_lived_token})


__all__ = [
    "pkce_pair", "LocalCallbackServer", "CallbackResult", "youtube_auth_url", "youtube_exchange_code",
    "youtube_refresh", "youtube_authorize_interactive", "tiktok_auth_url", "tiktok_exchange_code",
    "tiktok_refresh", "tiktok_authorize_interactive", "meta_long_lived_user_token", "meta_pages",
    "meta_find_ig_user_id", "instagram_login_long_lived_token", "instagram_login_refresh_token",
    "threads_long_lived_token", "threads_refresh_token", "THREADS_API_VERSION",
]
