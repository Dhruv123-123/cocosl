"""launch/products/build.py must never sit in sys.modules as plain `build`: other folders (the site, PR #4) have
their own build.py, and whichever loads first would win for every later `import build`."""
import sys
from pathlib import Path

LAUNCH = Path(__file__).resolve().parents[1] / "launch"
for sub in ("products", "etsy", "templates", "brandshop"):
    sys.path.insert(0, str(LAUNCH / sub))


def test_products_build_loads_under_a_unique_name():
    import build_brandshop  # noqa: F401
    import build_etsy  # noqa: F401
    import build_templates  # noqa: F401
    import products_build
    assert products_build.build.__name__ == "launch_products_build"
    assert callable(products_build.build.recalc_check)
    b = sys.modules.get("build")
    assert b is None or Path(getattr(b, "__file__", "")).resolve() != (LAUNCH / "products" / "build.py").resolve()
