"""Dashboard access control.

* DASHBOARD_TOKEN set: every request needs the session cookie (set by /login)
  or `Authorization: Bearer <token>`.
* DASHBOARD_TOKEN unset: only direct requests from localhost are allowed
  (anything arriving through a proxy is refused), and pages show a banner.

Public routes (the business `public_router`, e.g. /go/{slug}, plus /static,
/login and /api/health) never need auth. Unsafe methods from a browser must be
same-origin, which blocks cross-site form posts against the cookie session.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import time
from collections import defaultdict, deque
from urllib.parse import quote, urlparse

from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

COOKIE = "cf_session"
LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost"}
PROXY_HEADERS = ("x-forwarded-for", "forwarded", "x-real-ip")
ALWAYS_PUBLIC = (re.compile(r"^/static/"), re.compile(r"^/go/[^/]+/?$"), re.compile(r"^/login/?$"),
                 re.compile(r"^/api/health/?$"), re.compile(r"^/favicon\.ico$"))
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def session_value(token: str) -> str:
    """Cookie value derived from the token, so the raw token is never stored in the browser."""
    return hmac.new(token.encode(), b"contentfactory-dashboard-session", hashlib.sha256).hexdigest()


def token_ok(request: Request, token: str) -> bool:
    cookie = request.cookies.get(COOKIE, "")
    if cookie and hmac.compare_digest(cookie, session_value(token)):
        return True
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        return hmac.compare_digest(header[7:].strip().encode(), token.encode())
    return False


def is_local(request: Request) -> bool:
    host = request.client.host if request.client else ""
    if any(h in request.headers for h in PROXY_HEADERS):
        return False
    return host in LOCAL_HOSTS


def safe_next(url: str | None) -> str:
    """Only allow same-site relative redirects after login."""
    if not url or not url.startswith("/") or url.startswith("//") or "\\" in url:
        return "/"
    return url


class LoginLimiter:
    """At most `limit` failed logins per client per `window` seconds."""

    def __init__(self, limit: int = 10, window: float = 600):
        self.limit, self.window = limit, window
        self.fails: dict[str, deque] = defaultdict(deque)

    def blocked(self, key: str) -> bool:
        q = self.fails[key]
        while q and time.monotonic() - q[0] > self.window:
            q.popleft()
        return len(q) >= self.limit

    def fail(self, key: str) -> None:
        self.fails[key].append(time.monotonic())


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        settings = request.app.state.factory.settings
        allowed = (token_ok(request, settings.dashboard_token) if settings.dashboard_token
                   else is_local(request))
        request.state.authed = allowed
        if self._is_public(request, path):
            return await call_next(request)
        if request.method not in SAFE_METHODS and not self._same_origin(request):
            return JSONResponse({"error": "Cross-site request refused"}, status_code=403)
        if allowed:
            return await call_next(request)
        if not settings.dashboard_token:
            return JSONResponse({"error": "DASHBOARD_TOKEN is not set, so the dashboard only answers direct "
                                          "requests from localhost. Set DASHBOARD_TOKEN before exposing it."},
                                status_code=403)
        if path.startswith("/api/") or request.method not in SAFE_METHODS:
            return JSONResponse({"error": "Authentication required: send 'Authorization: Bearer "
                                          "<DASHBOARD_TOKEN>' or log in at /login"}, status_code=401)
        target = path + (f"?{request.url.query}" if request.url.query else "")
        return RedirectResponse(f"/login?next={quote(target)}", status_code=303)

    @staticmethod
    def _is_public(request: Request, path: str) -> bool:
        if any(p.match(path) for p in ALWAYS_PUBLIC):
            return True
        return any(p.match(path) for p in getattr(request.app.state, "public_paths", []))

    @staticmethod
    def _same_origin(request: Request) -> bool:
        source = request.headers.get("origin") or request.headers.get("referer")
        if not source or source == "null":
            # Non-browser clients (curl, n8n) send neither; browsers always send Origin on POST.
            return source != "null"
        return urlparse(source).netloc == request.headers.get("host", "")
