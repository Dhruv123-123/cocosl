"""The affiliate application kit builds. (The affiliate articles now live in the site PR, with their tests.)"""
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1] / "launch" / "affiliates" / "kit.py"


def test_affiliate_application_kit(tmp_path):
    subprocess.run([sys.executable, str(KIT), "--out", str(tmp_path)], check=True, capture_output=True)
    md = (tmp_path / "APPLICATIONS.md").read_text()
    for name in ("SoFi", "CIT Bank", "Rocket Money", "Aura", "FreshBooks", "Gusto", "Impact", "CJ Affiliate"):
        assert f"### {name}" in md
    rows = (tmp_path / "applications.csv").read_text().splitlines()
    assert len(rows) > 40 and all(",not applied," in r for r in rows[1:])
    assert (tmp_path / "applications.html").read_text().count("<details>") > 30
