"""Brand kit: profile picture, YouTube banner/watermark, Instagram highlight
covers, a style sheet and platform bios for each brand.

    from contentfactory.brandkit import build_brand_kit
    paths = build_brand_kit(settings, brand)   # -> output/<slug>/brand-kit/...
"""
from .kit import build_brand_kit, kit_dir

__all__ = ["build_brand_kit", "kit_dir"]
