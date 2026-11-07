"""Portfolio reel for the UGC service: sample ads for FICTIONAL brands.

`build_portfolio(settings, ads, out_dir)` renders each sample ad as a 9:16 MP4
(via `ugc.render_ad_video`), burns in two labels for the whole ad (top: the
AI disclosure; bottom: "Concept ad for a fictional brand · Sample"), grabs a
compressed JPEG poster, and writes a self-contained `portfolio.html` gallery
that plays the videos from `videos/<slug>.mp4` (relative path).

Layout of `out_dir` (and of `copy_to`, minus the videos, for the repo):

    portfolio.html  ads.json  posters/<slug>.jpg  videos/<slug>.mp4  videos/<slug>.srt

The ads themselves live in launch/ugc-service/portfolio/ads.json (transcribed
from SAMPLE_ADS.md). Every script is checked with `ugc.check_ad_script`: a
first-person testimonial blocks the build.
"""
from __future__ import annotations

import dataclasses
import html
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from ..schemas import AdScript
from . import ugc

FICTIONAL_LABEL = "Concept ad for a fictional brand · Sample"
SILENT_LABEL = "AI-generated · Ad"
POSTER_WIDTH = 540
POSTER_AT = 1.4  # seconds: first headline and first caption chunk are both on screen
DEFAULT_ADS = Path(__file__).resolve().parents[3] / "launch" / "ugc-service" / "portfolio" / "ads.json"


# --------------------------------------------------------------------------- data
def load_ads(path: str | Path = DEFAULT_ADS) -> list[dict]:
    """Read ads.json ({"ads": [...]}) and validate each script as an AdScript."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [_entry(a) for a in (data["ads"] if isinstance(data, dict) else data)]


def _entry(raw: dict) -> dict:
    entry = dict(raw)
    if not entry.get("slug") or not entry.get("brand"):
        raise ValueError("Each portfolio ad needs a slug and a brand")
    script = entry["script"]
    entry["script"] = script if isinstance(script, AdScript) else AdScript.model_validate(script)
    return entry


def check_portfolio_ads(ads: list[dict]) -> list[str]:
    """Problems that block the build: testimonial language or a missing AI label."""
    problems = []
    for a in ads:
        for c in ugc.check_ad_script(a["script"]):
            if c.level == "block":
                problems.append(f"{a['slug']}: {c.message}")
        if "ai" not in a["script"].on_screen_disclosure.lower():
            problems.append(f"{a['slug']}: on_screen_disclosure must say the ad is AI-generated")
    return problems


def disclosure_label(settings, entry: dict) -> str:
    """Top label burned in for the whole ad. A silent render has no voice or
    presenter yet, so it gets the generic label rather than claiming one."""
    if str(getattr(settings, "tts_provider", "")).lower() == "silent":
        return SILENT_LABEL
    return entry["script"].on_screen_disclosure


# --------------------------------------------------------------------------- render
def _brand_dict(entry: dict, label: str) -> dict:
    return {"name": entry["brand"], "slug": "portfolio-" + entry["slug"], "niche": entry.get("category", ""),
            "palette": entry.get("palette") or None, "visual": {"watermark": ""},
            "ai_disclosure": entry["script"].on_screen_disclosure, "cta": entry["script"].cta}


def _pill(img, text: str, size: int, center_x: int | None, left: int, top: int) -> None:
    from PIL import ImageDraw

    from ..media import fonts
    font = fonts.load(fonts.font_path("Inter", "semibold"), size)
    tw = int(font.getlength(text))
    pad_x, pill_h = int(size * 0.9), int(size * 1.95)
    x0 = center_x - tw // 2 - pad_x if center_x is not None else left
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, top, x0 + tw + 2 * pad_x, top + pill_h), radius=pill_h // 2, fill=(0, 0, 0, 170))
    d.text((x0 + pad_x + tw // 2, top + pill_h // 2), text, font=font, fill=(255, 255, 255, 245), anchor="mm")


def _label_png(path: Path, top_text: str, bottom_text: str, size: tuple[int, int] = (1080, 1920)) -> None:
    """Transparent overlay: AI label top-left (above the headline card), fictional-brand
    label bottom-centre (below the captions). Both stay on screen for the whole ad."""
    from PIL import Image
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    _pill(img, top_text, 34, None, 56, 86)
    _pill(img, bottom_text, 34, w // 2, 0, h - 262)
    img.save(path)


def _web_x264(settings) -> list[str]:
    """Smaller files for a web gallery: the cards art has film grain that x264 spends bits on."""
    from ..media.util import RenderOptions
    from ..media.video import x264_args
    opts = RenderOptions.from_settings(settings)
    return x264_args(dataclasses.replace(opts, crf=max(opts.crf, 27), preset="slow"))


def render_portfolio_ad(settings, entry: dict, out_dir: Path, work_root: Path) -> dict:
    """Render one ad into out_dir/videos/<slug>.mp4 and out_dir/posters/<slug>.jpg."""
    from ..media.util import ffmpeg, probe

    slug = entry["slug"]
    work_settings = dataclasses.replace(settings, output_dir=work_root)
    label = disclosure_label(settings, entry)
    assets = ugc.render_ad_video(work_settings, _brand_dict(entry, label), entry["script"],
                                 output_subdir=f"portfolio/{slug}", headline_disclosure=False)
    raw = work_root / assets["video"]
    overlay = work_root / f"{slug}-label.png"
    _label_png(overlay, label, FICTIONAL_LABEL)
    videos, posters = out_dir / "videos", out_dir / "posters"
    videos.mkdir(parents=True, exist_ok=True)
    posters.mkdir(parents=True, exist_ok=True)
    labelled = work_root / f"{slug}.mp4"
    ffmpeg(["-i", str(raw), "-loop", "1", "-i", str(overlay),
            "-filter_complex", "[0:v][1:v]overlay=0:0:shortest=1:format=auto,format=yuv420p[v]",
            "-map", "[v]", "-map", "0:a?", *_web_x264(settings),
            "-c:a", "copy", "-movflags", "+faststart", str(labelled)])
    poster = work_root / f"{slug}.jpg"
    ffmpeg(["-ss", f"{POSTER_AT:.2f}", "-i", str(labelled), "-frames:v", "1",
            "-vf", f"scale={POSTER_WIDTH}:-2:flags=lanczos", "-q:v", "6", str(poster)])
    shutil.copyfile(labelled, videos / f"{slug}.mp4")
    if assets.get("captions_srt"):
        shutil.copyfile(work_root / assets["captions_srt"], videos / f"{slug}.srt")
    shutil.copyfile(poster, posters / f"{slug}.jpg")
    info = probe(labelled)
    return {"video": f"videos/{slug}.mp4", "poster": f"posters/{slug}.jpg", "captions": f"videos/{slug}.srt",
            "duration": round(info["duration"], 1), "width": info["width"], "height": info["height"],
            "label": label, "bytes": labelled.stat().st_size}


def build_portfolio(settings, ads: list[dict] | str | Path | None, out_dir: str | Path, *,
                    copy_to: str | Path | None = None, render: bool = True, studio: dict | None = None) -> dict:
    """Render every sample ad and write the gallery.

    `ads`: entries from `load_ads` (or a path to ads.json; None = the repo's).
    `out_dir`: where videos, posters and portfolio.html go.
    `copy_to`: optional second folder (e.g. the repo) that gets portfolio.html,
    ads.json and posters but NOT the videos. `render=False` rebuilds the page
    from posters/videos already in out_dir."""
    entries = load_ads(ads if isinstance(ads, (str, Path)) else DEFAULT_ADS) if not isinstance(ads, list) \
        else [_entry(a) for a in ads]
    problems = check_portfolio_ads(entries)
    if problems:
        raise ugc.TestimonialError("Portfolio blocked: " + "; ".join(problems))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    media: dict[str, dict] = {}
    manifest = out / "media.json"
    if not render and manifest.exists():
        media = json.loads(manifest.read_text(encoding="utf-8"))
    if render:
        with tempfile.TemporaryDirectory(prefix="portfolio-") as tmp:  # render locally, copy finished files
            for e in entries:
                media[e["slug"]] = render_portfolio_ad(settings, e, out, Path(tmp))
        manifest.write_text(json.dumps(media, indent=2), encoding="utf-8")
    page = portfolio_html(entries, media, studio=studio)
    (out / "portfolio.html").write_text(page, encoding="utf-8")
    (out / "ads.json").write_text(_ads_json(entries), encoding="utf-8")
    result: dict[str, Any] = {"out_dir": str(out), "html": str(out / "portfolio.html"), "ads": media}
    if copy_to:
        dest = Path(copy_to)
        (dest / "posters").mkdir(parents=True, exist_ok=True)
        for e in entries:
            src = out / "posters" / f"{e['slug']}.jpg"
            if src.exists():
                shutil.copyfile(src, dest / "posters" / src.name)
        (dest / "portfolio.html").write_text(page, encoding="utf-8")
        (dest / "media.json").write_text(json.dumps(media, indent=2), encoding="utf-8")
        if not (dest / "ads.json").exists():  # never overwrite a hand-edited source file
            (dest / "ads.json").write_text(_ads_json(entries), encoding="utf-8")
        result["copied_to"] = str(dest)
    return result


def _ads_json(entries: list[dict]) -> str:
    rows = [{**e, "script": e["script"].model_dump()} for e in entries]
    return json.dumps({"note": "Portfolio sample ads for FICTIONAL brands. See SAMPLE_ADS.md.", "ads": rows},
                      indent=2, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------- html
def _e(text: Any) -> str:
    return html.escape(str(text or ""), quote=True)


def _card(entry: dict, m: dict) -> str:
    s: AdScript = entry["script"]
    slug = entry["slug"]
    video = m.get("video") or f"videos/{slug}.mp4"
    poster = m.get("poster") or f"posters/{slug}.jpg"
    dur = f"{m['duration']:.0f}s" if m.get("duration") else ""
    beats = "".join(f"<tr><td>{_e(seg.heading)}</td><td>{_e(seg.narration)}</td><td>{_e(seg.on_screen_text)}</td></tr>"
                    for seg in s.segments)
    hooks = "".join(f"<li><b>{chr(66 + i)}</b> {_e(v)}</li>" for i, v in enumerate(s.variations))
    return f"""
<article class="ad" id="{_e(slug)}">
  <div class="frame">
    <video controls playsinline preload="none" poster="{_e(poster)}" aria-label="Sample ad for {_e(entry['brand'])}">
      <source src="{_e(video)}" type="video/mp4">
    </video>
    <div class="missing" hidden><img src="{_e(poster)}" alt="Poster frame of the {_e(entry['brand'])} sample ad"><p>Video file not uploaded next to this page yet. Copy the <code>videos/</code> folder here.</p></div>
  </div>
  <div class="meta">
    <div class="row"><span class="pill">{_e(entry.get('category'))}</span><span class="pill">{_e(entry.get('style'))}</span>{f'<span class="pill">{dur}</span>' if dur else ''}</div>
    <h3>{_e(entry['brand'])}</h3>
    <p class="muted">{_e(s.concept)}</p>
    <p class="hook"><b>A</b> {_e(s.hook)}</p>
    <ul class="hooks">{hooks}</ul>
    <details><summary>Script and on-screen text</summary>
      <table><tr><th>Beat</th><th>Voice</th><th>On screen</th></tr>{beats}</table>
    </details>
    <p class="fine">Fictional brand and price ({_e(entry.get('fictional_price'))}). Label on screen: “{_e(m.get('label') or s.on_screen_disclosure)}” + “{_e(FICTIONAL_LABEL)}”.</p>
  </div>
</article>"""


def portfolio_html(entries: list[dict], media: dict[str, dict] | None = None, studio: dict | None = None) -> str:
    """Mobile-first gallery page in the style of launch/ugc-service/index.html."""
    media = media or {}
    st = {"name": "Your Studio Name", "email": "hello@yourdomain.com", "site": "../index.html", **(studio or {})}
    cards = "".join(_card(e, media.get(e["slug"], {})) for e in entries)
    return _PAGE.replace("{{CARDS}}", cards).replace("{{COUNT}}", str(len(entries))) \
        .replace("{{STUDIO_JSON}}", json.dumps(st)).replace("{{FICTIONAL}}", _e(FICTIONAL_LABEL))


_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sample Ads Portfolio</title>
<meta name="description" content="Sample vertical video ads for fictional brands, made with clearly labeled AI.">
<meta name="robots" content="noindex">
<!--
  HOW TO HOST: this page plays videos from ./videos/<slug>.mp4 (relative path).
  The repo copy keeps only posters (videos are too big for git). Rendered videos live in
  /mnt/project-files/content-factory/ugc-portfolio/videos/ ; copy that folder next to this file
  (or upload the whole ugc-portfolio folder) before sharing the link. Rebuild: `factory portfolio build`.
-->
<script>
  /* EDIT THESE (same values as index.html) */
  const STUDIO = {{STUDIO_JSON}};
</script>
<style>
  :root{
    --bg:#0c0f14; --bg2:#121722; --card:#161c29; --line:#263044; --text:#eef1f7; --muted:#9aa5bb;
    --accent:#7cf0c5; --accent2:#ffcf5c; --accent-ink:#06261a; --radius:18px;
  }
  @media (prefers-color-scheme: light){
    :root:not([data-theme="dark"]){
      --bg:#f7f6f2; --bg2:#ffffff; --card:#ffffff; --line:#e3e0d6; --text:#121722; --muted:#5b6476;
      --accent:#0f9d6e; --accent2:#b77900; --accent-ink:#ffffff;
    }
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 "Inter",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;-webkit-font-smoothing:antialiased}
  a{color:inherit}
  .wrap{max-width:1080px;margin:0 auto;padding:0 16px}
  h1,h2,h3{line-height:1.12;margin:0 0 .5em;letter-spacing:-.02em}
  h1{font-size:clamp(2rem,6.5vw,3.2rem);font-weight:850}
  h3{font-size:1.25rem;font-weight:780;margin-top:8px}
  p{margin:0 0 .9em}
  .muted{color:var(--muted)}
  .eyebrow{display:inline-block;font-size:.78rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin-bottom:12px}
  nav{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--bg) 86%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
  nav .wrap{display:flex;align-items:center;justify-content:space-between;height:60px;gap:12px}
  .logo{font-weight:850;letter-spacing:-.02em;text-decoration:none;display:flex;align-items:center;gap:8px}
  .logo i{width:22px;height:22px;border-radius:7px;background:linear-gradient(135deg,var(--accent),var(--accent2));display:inline-block}
  .btn{display:inline-flex;align-items:center;justify-content:center;padding:10px 18px;border-radius:999px;font-weight:700;text-decoration:none;border:1.5px solid var(--accent);font-size:.92rem;white-space:nowrap}
  .btn.primary{background:var(--accent);color:var(--accent-ink)}
  header{padding:40px 0 8px}
  .notice{background:linear-gradient(135deg,color-mix(in srgb,var(--accent) 14%,var(--card)),var(--card));border:1px solid var(--line);border-radius:var(--radius);padding:18px 20px;margin:18px 0 8px}
  .notice ul{margin:0;padding-left:20px}
  .notice li{margin-bottom:6px}
  .grid{display:grid;gap:22px;padding:24px 0 40px}
  @media(min-width:700px){.grid{grid-template-columns:1fr 1fr}}
  @media(min-width:1020px){.grid{grid-template-columns:1fr 1fr 1fr}}
  .ad{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;display:flex;flex-direction:column}
  .frame{aspect-ratio:9/16;background:#000;position:relative;max-height:78vh}
  .frame video,.frame img{width:100%;height:100%;object-fit:cover;display:block}
  .missing{position:absolute;inset:0}
  .missing p{position:absolute;left:12px;right:12px;bottom:12px;margin:0;background:rgba(0,0,0,.72);color:#fff;font-size:.85rem;padding:10px 12px;border-radius:12px}
  .meta{padding:16px 18px 18px}
  .row{display:flex;flex-wrap:wrap;gap:6px}
  .pill{border:1px solid var(--line);border-radius:999px;padding:2px 10px;font-size:.78rem;color:var(--muted)}
  .hook{font-weight:700;margin-bottom:6px}
  .hook b,.hooks b{display:inline-grid;place-items:center;width:22px;height:22px;border-radius:7px;background:color-mix(in srgb,var(--accent) 18%,transparent);color:var(--accent);font-size:.78rem;margin-right:6px}
  .hooks{list-style:none;padding:0;margin:0 0 10px;font-size:.93rem;color:var(--muted)}
  .hooks li{margin-bottom:6px}
  details{border-top:1px solid var(--line);padding-top:10px;margin-top:6px}
  summary{cursor:pointer;font-weight:700;font-size:.92rem}
  table{width:100%;border-collapse:collapse;font-size:.82rem;margin-top:8px}
  th,td{text-align:left;padding:6px 4px;border-bottom:1px solid var(--line);vertical-align:top}
  th{color:var(--muted);font-weight:600}
  .fine{font-size:.78rem;color:var(--muted);margin:10px 0 0}
  code{font-size:.85em}
  footer{border-top:1px solid var(--line);padding:28px 0 44px;font-size:.88rem;color:var(--muted)}
</style>
</head>
<body>
<nav><div class="wrap">
  <a class="logo" data-site href="../index.html"><i></i><span data-studio="name">Your Studio Name</span></a>
  <a class="btn primary" data-mail href="mailto:hello@yourdomain.com">Get a free sample</a>
</div></nav>

<header class="wrap">
  <span class="eyebrow">Portfolio · {{COUNT}} sample ads</span>
  <h1>Sample ads for brands that don’t exist.</h1>
  <p class="muted" style="max-width:62ch">Every brand, product and price on this page is <strong>fictional</strong>. These are concept ads made to show the format: vertical 9:16, a hook in the first three seconds, burned-in captions, one clear call to action, and hook variants (A/B/C) for testing.</p>
  <div class="notice">
    <ul>
      <li><strong>AI-made and labeled.</strong> Each video carries an on-screen “AI-generated” label for its full length, plus “{{FICTIONAL}}”.</li>
      <li><strong>No fake reviews.</strong> Scripts are spokesperson and demo style. Nobody claims to have bought or used anything.</li>
      <li><strong>These are caption-led cuts</strong> with generated abstract visuals. Ads for a real client use your own product photos or footage, an AI voice or presenter, and licensed music.</li>
    </ul>
  </div>
</header>

<main class="wrap"><div class="grid">{{CARDS}}</div></main>

<footer><div class="wrap">
  <p><strong data-studio="name">Your Studio Name</strong> · <a data-mail href="mailto:hello@yourdomain.com">hello@yourdomain.com</a> · <a data-site href="../index.html">Packages and pricing</a></p>
  <p>All brands shown are fictional; any resemblance to a real business is unintended. All ads we produce use AI-generated visuals, presenters and/or voices and are labeled as such.</p>
</div></footer>
<script>
  (function(){
    document.title = STUDIO.name + " · Sample ads";
    document.querySelectorAll('[data-studio]').forEach(function(el){ el.textContent = STUDIO[el.getAttribute('data-studio')] || ''; });
    document.querySelectorAll('[data-mail]').forEach(function(el){ el.href = 'mailto:' + STUDIO.email + '?subject=' + encodeURIComponent('Free sample ad'); if (el.tagName === 'A' && el.textContent.indexOf('@') > -1) el.textContent = STUDIO.email; });
    document.querySelectorAll('[data-site]').forEach(function(el){ if (STUDIO.site) el.href = STUDIO.site; });
    document.querySelectorAll('.ad').forEach(function(card){
      var v = card.querySelector('video'), s = card.querySelector('source'), miss = card.querySelector('.missing');
      function fail(){ v.hidden = true; miss.hidden = false; }
      s.addEventListener('error', fail);
      v.addEventListener('error', fail);
      v.addEventListener('play', function(){ document.querySelectorAll('video').forEach(function(o){ if (o !== v) o.pause(); }); });
    });
  })();
</script>
</body>
</html>
"""
