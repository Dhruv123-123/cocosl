"""Media production: voice, images, video, carousels, thumbnails.

Public entry point: `render_post(settings, brand, post) -> assets dict`.

The assets dict shape (stored in posts.assets) is:
{
  "video": "relative/path.mp4" | None,      # short/long formats
  "audio": "relative/path.wav" | None,
  "captions_srt": "relative/path.srt" | None,
  "images": ["relative/path.png", ...],     # one per segment
  "slides": ["relative/path.png", ...],     # carousel/image formats (final composited slides)
  "thumbnail": "relative/path.png" | None,
  "duration": float,                        # seconds, video formats only
  "provenance": [ {"path": str, "source": "generated|rendered|own|licensed", "tool": str, "prompt": str, "license": str} ],
}
Paths are relative to settings.output_dir so the folder can be moved or served.
"""
from __future__ import annotations

from .render import render_post  # noqa: F401
