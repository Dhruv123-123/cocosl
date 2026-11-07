"""Shared HTTP plumbing for the platform adapters.

- `ApiClient` wraps a sync `httpx.Client` (timeouts, injectable transport) and
  turns HTTP/transport failures into `PublishError` with the right
  `retryable` flag and the platform's own error message.
- `poll` is a small backoff loop with a time cap and an injectable sleep.
- `HttpPublisher` is the base class adapters subclass.

Error messages never include query strings, so tokens passed as
`access_token=` parameters can't leak into logs or the database.
"""
from __future__ import annotations

import time
from typing import Any, Callable

import httpx

from ..config import Settings
from .base import PublishError, Publisher

GRAPH_API_VERSION = "v25.0"     # Facebook/Instagram Graph API, pinned. Bump deliberately.
THREADS_API_VERSION = "v1.0"
DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
UPLOAD_TIMEOUT = httpx.Timeout(600.0, connect=15.0)

# Meta error codes that mean "slow down / try later" even though the HTTP
# status is often 400: 1 unknown, 2 service, 4 app rate limit, 17 user rate
# limit, 32 page rate limit, 341 app limit, 613 rate limit, 80001+ BUC limits.
_META_RETRYABLE_CODES = {1, 2, 4, 17, 32, 341, 613}

Sleep = Callable[[float], None]


def _error_text(resp: httpx.Response) -> tuple[str, bool | None]:
    """Extract the platform's message and an optional retryable hint."""
    try:
        body = resp.json()
    except ValueError:
        return resp.text[:500], None
    if not isinstance(body, dict):
        return str(body)[:500], None
    err = body.get("error")
    if isinstance(err, dict):
        # Meta: {error:{message,type,code,error_subcode,is_transient,error_user_msg}}
        # Google: {error:{code,message,errors:[{reason}]}}
        # TikTok: {error:{code:"spam_risk...",message,log_id}}
        msg = err.get("error_user_msg") or err.get("message") or ""
        code = err.get("code")
        sub = err.get("error_subcode")
        reasons = [e.get("reason") for e in err.get("errors", []) if isinstance(e, dict) and e.get("reason")]
        parts = [str(msg)]
        if code not in (None, ""):
            parts.append(f"code={code}")
        if sub:
            parts.append(f"subcode={sub}")
        if reasons:
            parts.append(f"reason={','.join(reasons)}")
        hint: bool | None = None
        if err.get("is_transient") is True or (isinstance(code, int) and (code in _META_RETRYABLE_CODES or 80000 <= code < 81000)):
            hint = True
        if code == "rate_limit_exceeded":
            hint = True
        return " ".join(p for p in parts if p), hint
    if isinstance(err, str):  # OAuth style {error, error_description}
        return f"{err}: {body.get('error_description', '')}".strip(": "), None
    if "message" in body:  # Postiz / generic
        return str(body["message"])[:500], None
    return str(body)[:500], None


def classify(platform: str, resp: httpx.Response, what: str = "") -> PublishError:
    msg, hint = _error_text(resp)
    status = resp.status_code
    retryable = status == 429 or status >= 500 or bool(hint)
    where = f"{resp.request.method} {resp.request.url.copy_with(query=None)}" if resp.request else what
    return PublishError(f"{platform}: HTTP {status} on {what or where}: {msg}", retryable=retryable)


class ApiClient:
    """Thin httpx wrapper that raises PublishError on any failure."""

    def __init__(self, platform: str, transport: httpx.BaseTransport | None = None,
                 client: httpx.Client | None = None, timeout: httpx.Timeout = DEFAULT_TIMEOUT):
        self.platform = platform
        self._given = client
        self._transport, self._timeout = transport, timeout
        self._made: httpx.Client | None = None

    @property
    def _client(self) -> httpx.Client:
        """Built on first use: a publisher made only to check its credentials (the dashboard does that
        for every platform on each page load) never pays for loading the TLS certificates."""
        if self._given is not None:
            return self._given
        if self._made is None:
            self._made = httpx.Client(transport=self._transport, timeout=self._timeout, follow_redirects=False)
        return self._made

    def request(self, method: str, url: str, *, what: str = "", ok: tuple[int, ...] = (),
                **kwargs: Any) -> httpx.Response:
        """Send a request. 2xx (or any status in `ok`) is returned; anything
        else raises PublishError (retryable for 429/5xx/timeouts)."""
        try:
            resp = self._client.request(method, url, **kwargs)
        except httpx.TimeoutException as e:
            raise PublishError(f"{self.platform}: timeout on {what or method}: {type(e).__name__}", retryable=True) from None
        except httpx.TransportError as e:
            raise PublishError(f"{self.platform}: network error on {what or method}: {type(e).__name__}", retryable=True) from None
        if resp.is_success or resp.status_code in ok:
            return resp
        raise classify(self.platform, resp, what)

    def json(self, method: str, url: str, *, what: str = "", **kwargs: Any) -> dict:
        resp = self.request(method, url, what=what, **kwargs)
        try:
            data = resp.json()
        except ValueError:
            raise PublishError(f"{self.platform}: non-JSON response on {what or method}", retryable=True) from None
        return data if isinstance(data, dict) else {"data": data}

    def close(self) -> None:
        if self._given is not None or self._made is not None:
            self._client.close()


def poll(check: Callable[[], tuple[bool, Any]], *, platform: str, what: str, sleep: Sleep,
         first_wait: float = 3.0, max_interval: float = 30.0, max_wait: float = 300.0,
         factor: float = 1.6) -> Any:
    """Call `check()` until it returns (True, value); exponential backoff,
    raising a retryable PublishError when `max_wait` seconds are used up."""
    waited, interval = 0.0, first_wait
    while True:
        done, value = check()
        if done:
            return value
        if waited >= max_wait:
            raise PublishError(f"{platform}: gave up waiting for {what} after {int(waited)}s", retryable=True)
        step = min(interval, max_interval, max(max_wait - waited, 0.01))
        sleep(step)
        waited += step
        interval *= factor


class HttpPublisher(Publisher):
    """Publisher with an ApiClient. Pass `transport` (e.g. httpx.MockTransport)
    or a ready `client` in tests, and `sleep` to skip real waiting."""

    def __init__(self, settings: Settings, *, transport: httpx.BaseTransport | None = None,
                 client: httpx.Client | None = None, sleep: Sleep = time.sleep):
        super().__init__(settings)
        self.http = ApiClient(self.platform, transport=transport, client=client)
        self.upload_http = ApiClient(self.platform, transport=transport, client=client, timeout=UPLOAD_TIMEOUT)
        self.sleep = sleep

    def env_float(self, key: str, default: float) -> float:
        try:
            return float(self.settings.env(key) or default)
        except ValueError:
            return default

    def require_format(self, fmt: str) -> None:
        if not self.supports(fmt):
            raise PublishError(f"{self.platform}: format '{fmt}' is not supported", retryable=False)


def public_url(req_urls: dict[str, str], path) -> str | None:
    """Look up the public HTTPS URL for a local file (exact str(path) key)."""
    return req_urls.get(str(path)) if path is not None else None


def probe_video(path) -> dict | None:
    """Width/height/duration via ffprobe, or None if ffprobe is missing or the
    file can't be read (callers then skip the check rather than fail)."""
    import json
    import shutil
    import subprocess
    if not shutil.which("ffprobe"):
        return None
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=width,height:format=duration", "-of", "json", str(path)],
            capture_output=True, text=True, timeout=30, check=True).stdout
        data = json.loads(out)
        stream = (data.get("streams") or [{}])[0]
        return {"width": int(stream["width"]), "height": int(stream["height"]),
                "duration": float((data.get("format") or {}).get("duration") or 0)}
    except Exception:
        return None


def guess_video_mime(path) -> str:
    suffix = str(path).lower().rsplit(".", 1)[-1]
    return {"mp4": "video/mp4", "mov": "video/quicktime", "webm": "video/webm"}.get(suffix, "video/mp4")
