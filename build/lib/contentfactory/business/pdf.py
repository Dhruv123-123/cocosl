"""HTML -> PDF via headless Chromium driven by Node + Playwright.

Optional: if node or the playwright package isn't available, `html_to_pdf`
returns False and callers keep the HTML. Set FACTORY_PDF=0 to disable.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

_SCRIPT = r"""
const { chromium } = require('playwright');
(async () => {
  const [src, out] = process.argv.slice(2);
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.goto('file://' + src, { waitUntil: 'load' });
    await page.pdf({ path: out, printBackground: true, preferCSSPageSize: true,
                     format: 'Letter', margin: { top: '0', right: '0', bottom: '0', left: '0' } });
  } finally {
    await browser.close();
  }
})().catch(e => { console.error(String(e && e.stack || e)); process.exit(1); });
"""


def _node_env() -> dict[str, str]:
    env = dict(os.environ)
    if not env.get("NODE_PATH") and shutil.which("npm"):
        try:
            root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, timeout=20).stdout.strip()
            if root:
                env["NODE_PATH"] = root
        except (OSError, subprocess.SubprocessError):
            pass
    return env


def pdf_available() -> bool:
    return os.environ.get("FACTORY_PDF", "1").lower() not in ("0", "false", "no") and bool(shutil.which("node"))


def html_to_pdf(html_path: Path, pdf_path: Path, timeout: int = 90) -> bool:
    """Print `html_path` to `pdf_path`. Returns True on success, False otherwise."""
    if not pdf_available():
        return False
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(_SCRIPT)
        script = fh.name
    try:
        proc = subprocess.run(["node", script, str(Path(html_path).resolve()), str(Path(pdf_path).resolve())],
                              capture_output=True, text=True, timeout=timeout, env=_node_env())
        return proc.returncode == 0 and pdf_path.exists() and pdf_path.stat().st_size > 0
    except (OSError, subprocess.SubprocessError):
        return False
    finally:
        Path(script).unlink(missing_ok=True)
