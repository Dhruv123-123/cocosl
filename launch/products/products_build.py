"""Load launch/products/build.py under a unique module name.

Other folders have their own build.py (the site's, on PR #4). Importing ours as plain `build` puts it in
sys.modules["build"], and a later `import build` elsewhere then gets the wrong file. So every caller uses:

    from products_build import build as PB    # with launch/products on sys.path
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

NAME = "launch_products_build"
PATH = Path(__file__).resolve().parent / "build.py"


def load():
    if NAME not in sys.modules:
        spec = importlib.util.spec_from_file_location(NAME, PATH)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[NAME] = mod
        spec.loader.exec_module(mod)
    return sys.modules[NAME]


build = load()
