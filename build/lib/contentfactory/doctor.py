"""`factory doctor`: check that this install can actually make and post content.

Each check is ok / warn / fail with a one-line fix. Nothing is posted; the
voice test writes one short WAV to a temp folder. `--online` also checks that
your public media URL and Kokoro server answer.
"""
from __future__ import annotations

import os
import shutil
import sqlite3
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .pipeline import Factory


@dataclass
class Result:
    name: str
    level: str  # ok | warn | fail
    message: str


def _ffmpeg() -> Result:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        return Result("ffmpeg", "fail", "ffmpeg/ffprobe not on PATH: brew install ffmpeg (or apt install ffmpeg)")
    try:
        out = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True, timeout=20).stdout
    except Exception as e:
        return Result("ffmpeg", "fail", f"ffmpeg won't run: {e}")
    if "libx264" not in out:
        return Result("ffmpeg", "warn", "ffmpeg has no libx264 encoder; install a full build for platform-friendly MP4s")
    return Result("ffmpeg", "ok", "ffmpeg with libx264")


def _storage(f: Factory) -> list[Result]:
    res = []
    try:
        f.db.scalar("SELECT 1")
        mode = f.db.scalar("PRAGMA journal_mode")
        res.append(Result("database", "ok", f"{f.settings.db_path} ({mode})"))
    except sqlite3.Error as e:
        res.append(Result("database", "fail", f"can't use {f.settings.db_path}: {e}"))
    out = f.settings.output_dir
    try:
        out.mkdir(parents=True, exist_ok=True)
        probe = out / ".doctor"
        probe.write_text("ok")
        probe.unlink()
        free_gb = shutil.disk_usage(out).free / 1e9
        res.append(Result("output", "ok" if free_gb > 5 else "warn",
                          f"{out} writable, {free_gb:.1f} GB free" + ("" if free_gb > 5 else " (videos need room)")))
    except OSError as e:
        res.append(Result("output", "fail", f"can't write to {out}: {e}"))
    return res


def _brands(f: Factory) -> list[Result]:
    try:
        brands = f.brands()
    except Exception as e:
        return [Result("brands", "fail", f"a brand file doesn't load: {e}")]
    if not brands:
        return [Result("brands", "fail", "no brands: copy brands/_template.yaml to brands/<slug>.yaml")]
    res = [Result("brands", "ok", ", ".join(brands))]
    for slug, b in brands.items():
        if not any(a.enabled for a in b.accounts):
            res.append(Result(f"brand {slug}", "warn", "no enabled accounts, so nothing can be scheduled"))
        if not b.require_human_review:
            res.append(Result(f"brand {slug}", "warn", "require_human_review is off: clean posts approve themselves"))
    return res


def _llm(f: Factory) -> Result:
    if f.llm.provider == "offline":
        return Result("writing", "warn", "offline placeholder drafts: set ANTHROPIC_API_KEY for real scripts")
    return Result("writing", "ok", f"Claude ({f.settings.anthropic_model})")


def _voice(f: Factory) -> Result:
    from .media import tts
    brand = next(iter(f.brands().values()), None)
    if brand is None:
        return Result("voice", "warn", "skipped (no brand)")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            r = tts.synthesize_segments(f.settings, brand, ["This is a quick voice check."], Path(tmp))
        except Exception as e:
            return Result("voice", "fail", f"no voice works: {e}")
    if r.provider == "silent":
        return Result("voice", "warn", "silent placeholder voice: set KOKORO_URL (free) or ELEVENLABS_*/OPENAI_API_KEY"
                      + (f" ({'; '.join(r.notes)[:160]})" if r.notes else ""))
    return Result("voice", "ok", f"{r.tool} ({r.durations[0]:.1f}s test clip)")


def _publishing(f: Factory, online: bool) -> list[Result]:
    from .publish import credential_status
    res = [Result("dry run", "ok" if f.settings.dry_run else "warn",
                  "ON: nothing is posted" if f.settings.dry_run else "OFF: approved posts go live on schedule")]
    used = {a.platform for b in f.brands().values() for a in b.accounts if a.enabled}
    multi = len(f.brands()) > 1
    for slug, b in f.brands().items():
        status = credential_status(f.settings.for_brand(slug))
        for platform in sorted({a.platform for a in b.accounts if a.enabled}):
            missing = status.get(platform, [])
            name = f"{slug}/{platform}" if multi else platform
            res.append(Result(name, "ok" if not missing else ("warn" if f.settings.dry_run else "fail"),
                              "connected" if not missing else f"missing {', '.join(missing)} (docs/CREDENTIALS.md)"))
    base = f.settings.public_media_base_url
    if used & {"instagram", "threads"}:
        if not base:
            res.append(Result("media URL", "warn" if f.settings.dry_run else "fail",
                              "PUBLIC_MEDIA_BASE_URL not set: Instagram/Threads fetch media from a public HTTPS URL"))
        elif not base.startswith("https://"):
            res.append(Result("media URL", "fail", f"PUBLIC_MEDIA_BASE_URL must be HTTPS ({base})"))
        elif online:
            import httpx
            try:
                code = httpx.get(base.rstrip("/") + "/", timeout=10, follow_redirects=True).status_code
                res.append(Result("media URL", "ok" if code < 500 else "warn", f"{base} answers ({code})"))
            except Exception as e:
                res.append(Result("media URL", "fail", f"{base} unreachable: {e}"))
    return res


def _worker(f: Factory) -> Result:
    from .health import system_status
    st = system_status(f)
    hb = st["worker"]["heartbeat"]
    if not hb:
        return Result("worker", "warn", "not running: docker compose up -d (or python -m contentfactory.worker)")
    mins = st["worker"]["minutes_since"] or 0
    return Result("worker", "ok" if mins < 15 else "fail", f"last tick {mins:.0f} min ago")


def run_checks(f: Factory, online: bool = False, voice: bool = True) -> list[Result]:
    out = [_ffmpeg(), *_storage(f), *_brands(f), _llm(f)]
    if voice:
        out.append(_voice(f))
    out += _publishing(f, online)
    out.append(_worker(f))
    if online and os.environ.get("KOKORO_URL"):
        import httpx
        url = os.environ["KOKORO_URL"].rstrip("/")
        try:
            code = httpx.get(f"{url}/v1/audio/voices", timeout=10).status_code
            out.append(Result("kokoro", "ok" if code == 200 else "warn", f"{url} answers ({code})"))
        except Exception as e:
            out.append(Result("kokoro", "fail", f"{url} unreachable: {e}"))
    return out


def register(sub, factory_fn) -> None:
    s = sub.add_parser("doctor", help="check this install can make and post content (posts nothing)")
    s.add_argument("--online", action="store_true", help="also check the media URL and Kokoro server answer")
    s.add_argument("--no-voice", action="store_true", help="skip the voice test clip")

    def run(a):
        results = run_checks(factory_fn(a), online=a.online, voice=not a.no_voice)
        mark = {"ok": "ok  ", "warn": "WARN", "fail": "FAIL"}
        for r in results:
            print(f"[{mark[r.level]}] {r.name:12s} {r.message}")
        fails = sum(r.level == "fail" for r in results)
        warns = sum(r.level == "warn" for r in results)
        print(f"\n{fails} problem(s), {warns} warning(s)")
        if fails:
            raise SystemExit(1)
    s.set_defaults(func=run)
