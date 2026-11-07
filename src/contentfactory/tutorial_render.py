"""`factory tutorial-render <spec.yaml>`: a screen-recorded tutorial, rendered and waiting only for your voice.

A spec (YAML) lists the beats of one tutorial: the screen footage (or a still) to show, the line to say, and
roughly how long. The footage is recorded once by a script (for the kits: the Playwright capture in the
project files), so you never have to screen-record. This command cuts it together:

    factory tutorial-render launch/ugc-service/kits-tutorials/lite-90s.yaml --footage <folder>
    -> output/tutorials/<id>/preview.mp4      silent, captions = the script, the timing to read along to
       output/tutorials/<id>/TELEPROMPTER.md  every line with its time slot (also teleprompter.txt)
       output/tutorials/<id>/RECORD.md        where to save your takes

Then record your voice, either way:

* one take per beat: voice/tutorials/<id>/beat-01.wav, beat-02.wav, ... (any length: a beat stretches to fit
  its take, holding the last frame of the footage), or
* one take for the whole thing: voice/tutorials/<id>/full.wav, read along to preview.mp4.

and run the same command again: it finds the takes and writes final.mp4 with your voice and captions timed to
it. Nothing is uploaded or posted. Footage is shown as recorded (cut and scaled, never altered). If a voice is
ever synthetic, the spec must say so (`ai_voice: true`) and the video carries an "AI voice" label throughout.
"""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .media import fonts
from .media.captions import Cue, time_segment
from .media.util import Palette, RenderOptions, ffmpeg, hex_to_rgb, probe
from .media.video import Beat, VideoSpec, assemble

TAKE_PAD = 0.45  # seconds of breathing room after each take
WPM = 150


@dataclass
class TBeat:
    say: str
    seconds: float
    footage: Path | None = None
    image: Path | None = None
    headline: str = ""


@dataclass
class TutorialSpec:
    id: str
    title: str
    size: tuple[int, int]
    palette: Palette
    watermark: str
    beats: list[TBeat] = field(default_factory=list)
    captions: bool = True
    ai_voice: bool = False


def load_spec(path: Path, footage_dir: Path | None = None) -> TutorialSpec:
    data = yaml.safe_load(Path(path).read_text()) or {}
    base = Path(footage_dir) if footage_dir else (Path(path).parent / str(data.get("footage_dir", "footage")))
    colors = [hex_to_rgb(c) for c in data.get("palette") or ["#16181d", "#f6efe6", "#c8775a"]]
    by_lum = sorted(colors, key=lambda c: sum(c))
    palette = Palette(dark=by_lum[0], light=by_lum[-1], accents=[c for c in colors if c not in (by_lum[0], by_lum[-1])]
                      or [by_lum[0]])
    beats = []
    for i, b in enumerate(data.get("beats") or [], 1):
        say = str(b.get("say", "")).strip()
        if not say:
            raise ValueError(f"beat {i}: `say` is empty")
        src = b.get("footage") or b.get("image")
        if not src:
            raise ValueError(f"beat {i}: needs `footage` (a clip) or `image` (a still)")
        words = len(say.split())
        seconds = float(b.get("seconds") or round(words / WPM * 60 + 1.0, 1))
        beats.append(TBeat(say=say, seconds=seconds, headline=str(b.get("headline", "")),
                           footage=(base / b["footage"]) if b.get("footage") else None,
                           image=(base / b["image"]) if b.get("image") else None))
    size = tuple(data.get("size") or (1920, 1080))
    return TutorialSpec(id=str(data["id"]), title=str(data.get("title", data["id"])), size=(int(size[0]), int(size[1])),
                        palette=palette, watermark=str(data.get("watermark", "")), beats=beats,
                        captions=bool(data.get("captions", True)), ai_voice=bool(data.get("ai_voice", False)))


def missing_footage(spec: TutorialSpec) -> list[str]:
    return [str(b.footage or b.image) for b in spec.beats if not (b.footage or b.image).exists()]


def voice_dir(settings, spec: TutorialSpec) -> Path:
    return Path(settings.home) / "voice" / "tutorials" / spec.id


def _takes(settings, spec: TutorialSpec) -> tuple[str, list[Path]]:
    """('beats', [one wav per beat]) | ('full', [full.wav]) | ('none', [])."""
    d = voice_dir(settings, spec)
    per = [d / f"beat-{i:02d}.wav" for i in range(1, len(spec.beats) + 1)]
    if per and all(p.exists() for p in per):
        return "beats", per
    if (d / "full.wav").exists():
        return "full", [d / "full.wav"]
    return "none", [p for p in per if p.exists()]


def _fmt(t: float) -> str:
    return f"{int(t // 60)}:{t % 60:04.1f}"


def _label(spec: TutorialSpec, work: Path) -> Path | None:
    """A transparent PNG with the AI voice label, when the voice is synthetic."""
    if not spec.ai_voice:
        return None
    from PIL import Image, ImageDraw
    w, h = spec.size
    img = Image.new("RGBA", spec.size, (0, 0, 0, 0))
    font = fonts.load(fonts.font_path("Inter", "semibold"), max(24, h // 36))
    d = ImageDraw.Draw(img)
    text = "AI voice"
    tw = d.textlength(text, font=font)
    d.rounded_rectangle((40, h - 40 - font.size * 1.8, 40 + tw + font.size * 1.2, h - 40), radius=12, fill=(0, 0, 0, 170))
    d.text((40 + font.size * 0.6, h - 40 - font.size * 1.45), text, font=font, fill=(255, 255, 255, 255))
    out = work / "ai-label.png"
    img.save(out)
    return out


def render(factory, spec_path: Path, footage_dir: Path | None = None, out_dir: Path | None = None,
           fast: bool = False) -> dict:
    settings = factory.settings
    spec = load_spec(spec_path, footage_dir)
    miss = missing_footage(spec)
    if miss:
        raise FileNotFoundError("missing footage: " + ", ".join(miss))
    out = Path(out_dir or Path(settings.output_dir) / "tutorials" / spec.id)
    out.mkdir(parents=True, exist_ok=True)
    work = out / "_work"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir()
    mode, takes = _takes(settings, spec)

    # timeline: per-beat takes stretch their beat; otherwise the planned seconds
    durs = [b.seconds for b in spec.beats]
    if mode == "beats":
        durs = [max(b.seconds, probe(t)["duration"] + TAKE_PAD) for b, t in zip(spec.beats, takes)]
    starts, t = [], 0.0
    for d in durs:
        starts.append(t)
        t += d
    total = t

    opts = RenderOptions(fps=30, preset="veryfast" if fast else "medium", crf=23 if fast else 20, workers=4)
    vspec = VideoSpec(fmt="long" if spec.size[0] > spec.size[1] else "short", size=spec.size, palette=spec.palette,
                      font_family="Inter", watermark=spec.watermark, options=opts,
                      look={"captions": "box", "motion": "cuts"})
    beats = [Beat(image=(b.image or b.footage), headline=b.headline, start=s, duration=d, clip=b.footage,
                  still=b.footage is None) for b, s, d in zip(spec.beats, starts, durs)]
    cues: list[Cue] = []
    if spec.captions:
        for b, s, d in zip(spec.beats, starts, durs):
            cues += time_segment(b.say, s + 0.15, max(0.5, d - TAKE_PAD))

    if mode == "beats":
        from .media.tts import concat_narration
        narration, voiced, name = work / "narration.wav", True, "final.mp4"
        concat_narration(takes, durs, narration)
    elif mode == "full":
        narration, voiced, name = takes[0], True, "final.mp4"
    else:
        narration, voiced, name = work / "silence.wav", False, "preview.mp4"
        ffmpeg(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{total:.3f}", str(narration)])
    target = out / name
    assemble(vspec, beats, cues, narration, target, work, voiced=voiced)
    label = _label(spec, work)
    if label:
        tmp = work / "labelled.mp4"
        ffmpeg(["-i", str(target), "-i", str(label), "-filter_complex", "[0:v][1:v]overlay=0:0,format=yuv420p[v]",
                "-map", "[v]", "-map", "0:a", "-c:a", "copy", "-c:v", "libx264", "-preset", opts.preset,
                "-crf", str(opts.crf), "-movflags", "+faststart", str(tmp)])
        tmp.replace(target)

    rows = [(i, s, d, b) for i, (b, s, d) in enumerate(zip(spec.beats, starts, durs), 1)]
    vd = voice_dir(settings, spec)
    try:
        vd = vd.relative_to(Path(settings.home))  # shown as voice/tutorials/<id>/ (relative to the factory folder)
    except ValueError:
        pass
    prompt = [f"# {spec.title}: teleprompter", "",
              f"Read along to `preview.mp4` ({_fmt(total)} long). Each line has its time slot; a pause between "
              "lines is fine.", "", "| # | Time | Say |", "|---|---|---|"]
    prompt += [f"| {i} | {_fmt(s)}–{_fmt(s + d)} | {b.say} |" for i, s, d, b in rows]
    (out / "TELEPROMPTER.md").write_text("\n".join(prompt) + "\n")
    (out / "teleprompter.txt").write_text("\n\n".join(f"{i}. {b.say}" for i, _, _, b in rows) + "\n")
    rec = [f"# Record the voiceover for {spec.title}", "",
           "Your own voice. Quiet room, phone or USB mic about a hand's width away, read each line as written "
           "(the captions show these words).", "",
           "**Either** one file per line (easiest to redo a single line):", ""]
    rec += [f"- `{vd / f'beat-{i:02d}.wav'}`: \"{b.say}\"" for i, _, _, b in rows]
    rec += ["", f"**Or** one take of the whole script, read along to preview.mp4: `{vd / 'full.wav'}`", "",
            f"Then run `factory tutorial-render {spec_path}` again (same --footage). It writes final.mp4 next to "
            "this file. WAV, any sample rate. If you ever use a synthetic voice instead, set `ai_voice: true` in "
            "the spec so the video is labelled \"AI voice\" throughout."]
    (out / "RECORD.md").write_text("\n".join(rec) + "\n")
    info = {"id": spec.id, "file": str(target), "mode": mode, "seconds": round(total, 2), "beats": len(rows),
            "takes_found": len(takes) if mode != "none" else len(takes)}
    (out / "render.json").write_text(json.dumps(info, indent=2))
    if not opts.keep_work:
        shutil.rmtree(work, ignore_errors=True)
    return info


def register(sub, factory_fn) -> None:
    s = sub.add_parser("tutorial-render", help="render a screen-recorded tutorial from a spec; add your voice later")
    s.add_argument("spec", type=Path)
    s.add_argument("--footage", type=Path, default=None, help="folder with the spec's footage (default: next to the spec)")
    s.add_argument("--out", type=Path, default=None)
    s.add_argument("--fast", action="store_true", help="quicker, lower-quality encode for checking")

    def cmd(a):
        info = render(factory_fn(a), a.spec, a.footage, a.out, fast=a.fast)
        print(json.dumps(info, indent=2))
    s.set_defaults(func=cmd)
