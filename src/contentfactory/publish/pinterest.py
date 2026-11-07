"""Pinterest: post-by-hand for now (MANUAL_PLATFORMS includes pinterest).

Pins go through Pinterest's own scheduler: the factory writes a package per pin (2:3 pin image, title,
description, link with UTM tags, board, time) under output/manual/, and you schedule them in Pinterest
in a batch. This class exists so scheduling and the media check know the platform; it never uploads.
"""
from __future__ import annotations

from .base import PublishError, Publisher, PublishRequest, PublishResult


class PinterestPublisher(Publisher):
    platform = "pinterest"
    required_env: list[str] = []

    def supports(self, fmt: str) -> bool:
        return fmt in ("short", "mid", "long", "carousel", "image")

    def publish(self, req: PublishRequest) -> PublishResult:
        raise PublishError("Pinterest is post-by-hand: use the package in output/manual (factory manual).")
