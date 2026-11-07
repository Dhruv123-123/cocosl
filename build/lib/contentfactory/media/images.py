"""Illustrations, one per script segment, cropped to the target aspect ratio.

Providers (settings.image_provider; "auto" tries them in this order):
  comfyui   - your own ComfyUI server (COMFYUI_URL), workflow template comfy_txt2img.json,
              checkpoint from COMFYUI_CHECKPOINT
  openai    - OpenAI Images REST (OPENAI_API_KEY), model gpt-image-1
  replicate - Replicate REST (REPLICATE_API_TOKEN), black-forest-labs/flux-schnell
  cards     - offline abstract art from the brand palette (see cards.py)

In auto mode a provider that fails is skipped for the rest of the post and the
image falls through to the next one; each result records the provider used.
"""
from __future__ import annotations

import base64
import copy
import io
import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

import httpx
from PIL import Image, ImageOps

from ..config import BrandProfile, Settings
from .cards import abstract_art
from .util import MediaError, Palette, ProviderError, seed_of

ORDER = ["comfyui", "openai", "replicate", "cards"]
TEMPLATE = Path(__file__).with_name("comfy_txt2img.json")
HTTP_TIMEOUT = httpx.Timeout(120.0, connect=10.0)
NEGATIVE = "text, letters, words, watermark, logo, signature, brand marks, real person, celebrity, deformed"


@dataclass
class ImageResult:
    path: Path
    provider: str
    tool: str
    prompt: str
    note: str = ""


def full_prompt(brand: BrandProfile, prompt: str) -> str:
    """Segment prompt + brand style + the no-text/no-logo/no-real-people rules."""
    style = brand.visual.image_style
    parts = [prompt.strip() or brand.niche]
    if style and style.lower() not in prompt.lower():
        parts.append(style)
    parts.append("original artwork, no text, no logos, no real people")
    return "; ".join(parts)


def generate_images(settings: Settings, brand: BrandProfile, prompts: list[str], size: tuple[int, int],
                    aspect: str, out_dir: Path, family: str = "") -> list[ImageResult]:
    """Create one PNG per prompt at exactly `size` (cover-cropped)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    wanted = (settings.image_provider or "auto").lower()
    if wanted != "auto" and wanted not in ORDER:
        raise MediaError(f"Unknown image provider '{wanted}'. Use one of: auto, {', '.join(ORDER)}")
    candidates = ORDER if wanted == "auto" else [wanted]
    providers = [PROVIDERS[n](settings, brand) for n in candidates]
    dead: dict[str, str] = {}
    results = []
    for i, raw in enumerate(prompts):
        prompt = full_prompt(brand, raw)
        path = out_dir / f"image-{i:02d}.png"
        results.append(_one(providers, wanted == "auto", dead, prompt, size, aspect, path, family))
    return results


def _one(providers, auto: bool, dead: dict, prompt: str, size, aspect: str, path: Path, family: str) -> ImageResult:
    for p in providers:
        if p.name in dead or (auto and not p.available()):
            continue
        try:
            img = p.generate(prompt, size, aspect, family)
            fitted = ImageOps.fit(img.convert("RGB"), size, Image.LANCZOS, centering=(0.5, 0.45))
            fitted.save(path, compress_level=3)
            note = "; ".join(f"{k} failed: {v}" for k, v in dead.items())
            return ImageResult(path, p.name, p.tool, prompt, note)
        except (ProviderError, httpx.HTTPError, OSError, ValueError, KeyError) as e:
            if not auto:
                raise ProviderError(f"Image provider '{p.name}' failed: {e}") from e
            dead[p.name] = str(e)[:200]
    raise ProviderError("No image provider succeeded: " + "; ".join(f"{k}: {v}" for k, v in dead.items()))


# ---------------------------------------------------------------- providers
class ImageProvider:
    name = ""
    tool = ""

    def __init__(self, settings: Settings, brand: BrandProfile):
        self.settings, self.brand = settings, brand

    def available(self) -> bool:
        return True

    def generate(self, prompt: str, size: tuple[int, int], aspect: str, family: str) -> Image.Image:
        raise NotImplementedError


class ComfyUI(ImageProvider):
    name = "comfyui"
    tool = "comfyui"
    LATENT = {"9:16": (768, 1344), "16:9": (1344, 768), "4:5": (896, 1152), "1:1": (1024, 1024)}

    def available(self) -> bool:
        return bool(os.environ.get("COMFYUI_URL"))

    def workflow(self, prompt: str, aspect: str) -> dict:
        wf = copy.deepcopy(json.loads(TEMPLATE.read_text()))
        width, height = self.LATENT.get(aspect, (1024, 1024))
        wf["3"]["inputs"]["seed"] = seed_of(prompt) % (2**32)
        wf["4"]["inputs"]["ckpt_name"] = os.environ.get("COMFYUI_CHECKPOINT", wf["4"]["inputs"]["ckpt_name"])
        wf["5"]["inputs"].update(width=width, height=height)
        wf["6"]["inputs"]["text"] = prompt
        wf["7"]["inputs"]["text"] = NEGATIVE
        return wf

    def generate(self, prompt, size, aspect, family):
        base = os.environ.get("COMFYUI_URL", "").rstrip("/")
        if not base:
            raise ProviderError("ComfyUI needs COMFYUI_URL (e.g. http://127.0.0.1:8188)")
        poll_limit = float(os.environ.get("COMFYUI_TIMEOUT", "300"))
        with httpx.Client(base_url=base, timeout=HTTP_TIMEOUT) as client:
            resp = client.post("/prompt", json={"prompt": self.workflow(prompt, aspect), "client_id": uuid.uuid4().hex})
            _check(resp, "ComfyUI /prompt")
            prompt_id = resp.json()["prompt_id"]
            deadline = time.monotonic() + poll_limit
            while time.monotonic() < deadline:
                hist = client.get(f"/history/{prompt_id}")
                _check(hist, "ComfyUI /history")
                entry = hist.json().get(prompt_id)
                if entry and entry.get("outputs"):
                    for node in entry["outputs"].values():
                        for im in node.get("images", []):
                            view = client.get("/view", params={"filename": im["filename"],
                                                               "subfolder": im.get("subfolder", ""),
                                                               "type": im.get("type", "output")})
                            _check(view, "ComfyUI /view")
                            return Image.open(io.BytesIO(view.content))
                    raise ProviderError("ComfyUI finished without an image output")
                time.sleep(1.5)
        raise ProviderError(f"ComfyUI did not finish within {poll_limit:.0f}s")


class OpenAIImages(ImageProvider):
    name = "openai"
    tool = "openai:gpt-image-1"
    SIZES = {"9:16": "1024x1536", "4:5": "1024x1536", "16:9": "1536x1024", "1:1": "1024x1024"}

    def available(self) -> bool:
        return bool(os.environ.get("OPENAI_API_KEY"))

    def generate(self, prompt, size, aspect, family):
        key = os.environ.get("OPENAI_API_KEY", "")
        if not key:
            raise ProviderError("OpenAI Images needs OPENAI_API_KEY")
        body = {"model": "gpt-image-1", "prompt": prompt, "n": 1, "size": self.SIZES.get(aspect, "1024x1024"),
                "quality": os.environ.get("OPENAI_IMAGE_QUALITY", "medium")}
        resp = httpx.post("https://api.openai.com/v1/images/generations", json=body,
                          headers={"Authorization": f"Bearer {key}"}, timeout=HTTP_TIMEOUT)
        _check(resp, "OpenAI Images")
        item = resp.json()["data"][0]
        if item.get("b64_json"):
            return Image.open(io.BytesIO(base64.b64decode(item["b64_json"])))
        return _download(item["url"])


class Replicate(ImageProvider):
    name = "replicate"
    tool = "replicate:black-forest-labs/flux-schnell"
    URL = "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"

    def available(self) -> bool:
        return bool(os.environ.get("REPLICATE_API_TOKEN"))

    def generate(self, prompt, size, aspect, family):
        token = os.environ.get("REPLICATE_API_TOKEN", "")
        if not token:
            raise ProviderError("Replicate needs REPLICATE_API_TOKEN")
        headers = {"Authorization": f"Bearer {token}", "Prefer": "wait"}
        body = {"input": {"prompt": prompt, "aspect_ratio": aspect, "output_format": "png", "num_outputs": 1}}
        resp = httpx.post(self.URL, json=body, headers=headers, timeout=HTTP_TIMEOUT)
        _check(resp, "Replicate")
        pred = resp.json()
        deadline = time.monotonic() + 180
        while pred.get("status") not in ("succeeded", "failed", "canceled") and time.monotonic() < deadline:
            time.sleep(1.5)
            poll = httpx.get(pred["urls"]["get"], headers={"Authorization": f"Bearer {token}"}, timeout=HTTP_TIMEOUT)
            _check(poll, "Replicate poll")
            pred = poll.json()
        if pred.get("status") != "succeeded":
            raise ProviderError(f"Replicate prediction {pred.get('status')}: {pred.get('error')}")
        output = pred.get("output")
        url = output[0] if isinstance(output, list) else output
        return _download(url)


class Cards(ImageProvider):
    name = "cards"
    tool = "pillow-cards"

    def generate(self, prompt, size, aspect, family):
        return abstract_art(Palette.from_brand(self.brand), size, prompt, family)


PROVIDERS = {"comfyui": ComfyUI, "openai": OpenAIImages, "replicate": Replicate, "cards": Cards}


def _check(resp: httpx.Response, what: str) -> None:
    if resp.status_code >= 400:
        raise ProviderError(f"{what} HTTP {resp.status_code}: {resp.text[:300]}")


def _download(url: str) -> Image.Image:
    resp = httpx.get(url, timeout=HTTP_TIMEOUT, follow_redirects=True)
    _check(resp, "image download")
    return Image.open(io.BytesIO(resp.content))
