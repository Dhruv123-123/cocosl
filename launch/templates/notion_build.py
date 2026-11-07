"""Build a Notion template in your workspace through the Notion API, so you don't have to click it together.

One-time setup (2 minutes):
  1. notion.so/profile/integrations > New integration > "Money Made Simple builder" (Internal). Copy the secret.
  2. In Notion, create an empty page (e.g. "Templates"). Click ••• > Connections > add your integration.
  3. export NOTION_TOKEN=<the secret>   (never commit it, never paste it into a chat)

Build:
  python launch/templates/notion_build.py notion-budget --parent "<link to the empty page>"
  python launch/templates/notion_build.py all --parent "<link>"          # all five
  python launch/templates/notion_build.py notion-budget --dry-run         # print the API calls, touch nothing

The API builds the pages, databases, properties, formulas, relations and example rows. Views (sorts, filters,
groups, footer totals) and the dollar format on formula columns can't be set through the API: BUILD.md lists
those clicks for each template (about 5 minutes).
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import notion_spec as N  # noqa: E402

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"
LINKS = Path(__file__).resolve().parent / "links.json"
BASIC = {"title", "number", "select", "date", "checkbox", "rich_text", "url"}


class NotionAPI:
    def __init__(self, token: str, pause: float = 0.35):
        self.token, self.pause = token, pause

    def call(self, method: str, path: str, body: dict | None = None) -> dict:
        data = json.dumps(body).encode() if body is not None else None
        for attempt in range(6):
            req = urllib.request.Request(API + path, data=data, method=method, headers={
                "Authorization": f"Bearer {self.token}", "Notion-Version": VERSION, "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    time.sleep(self.pause)
                    return json.loads(resp.read())
            except urllib.error.HTTPError as e:
                detail = e.read().decode(errors="replace")
                if e.code in (429, 500, 502, 503, 504) and attempt < 5:
                    time.sleep(float(e.headers.get("Retry-After") or 2 ** attempt))
                    continue
                raise SystemExit(f"Notion API {method} {path} failed ({e.code}): {detail}") from None
        raise SystemExit("Notion API kept failing; try again in a minute.")


class DryRun:
    """Stands in for the API: records every call and invents ids. Used by --dry-run and the tests."""

    def __init__(self):
        self.calls: list[tuple[str, str, dict | None]] = []
        self._ids = itertools.count(1)

    def call(self, method, path, body=None):
        self.calls.append((method, path, body))
        new_id = f"{next(self._ids):032x}"
        out = {"id": new_id, "url": f"https://www.notion.so/{new_id}"}
        if method == "PATCH" and path.startswith("/databases/") and body:
            out["properties"] = {}
            for name, cfg in body.get("properties", {}).items():
                if "relation" in cfg:
                    out["properties"][name] = {"relation": {"dual_property": {"synced_property_name": f"Related to {name}"}}}
        return out


def _text(s: str, **ann) -> dict:
    t = {"type": "text", "text": {"content": s}}
    if ann.get("url"):
        t["text"]["link"] = {"url": ann.pop("url")}
    if ann:
        t["annotations"] = ann
    return t


def _block(item: tuple, links: dict) -> dict:
    kind = item[0]
    if kind == "h2":
        return {"type": "heading_2", "heading_2": {"rich_text": [_text(item[1])]}}
    if kind == "p":
        return {"type": "paragraph", "paragraph": {"rich_text": [_text(item[1])]}}
    if kind == "small":
        return {"type": "paragraph", "paragraph": {"rich_text": [_text(item[1], italic=True, color="gray")]}}
    if kind == "callout":
        return {"type": "callout", "callout": {"rich_text": [_text(item[2])], "icon": {"type": "emoji", "emoji": item[1]},
                                               "color": "gray_background"}}
    if kind == "todo":
        return {"type": "to_do", "to_do": {"rich_text": [_text(item[1])], "checked": False}}
    if kind == "bullet":
        return {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [_text(item[1])]}}
    if kind == "divider":
        return {"type": "divider", "divider": {}}
    if kind == "link":
        url = links.get(item[2], "")
        if url and not url.startswith("TODO"):
            return {"type": "paragraph", "paragraph": {"rich_text": [_text("→ " + item[1], bold=True, url=url)]}}
        return {"type": "paragraph", "paragraph": {"rich_text": [_text(f"→ {item[1]} [add the {item[2]} link]", bold=True)]}}
    raise ValueError(kind)


def _basic_schema(db: dict) -> dict:
    props = {}
    for name, kind, cfg in db["props"]:
        if kind not in BASIC:
            continue
        if kind == "number":
            props[name] = {"number": {"format": cfg.get("format", "number")}}
        elif kind == "select":
            props[name] = {"select": {"options": [{"name": o, "color": N.GROUP_COLORS.get(o, "default")}
                                                  for o in cfg["options"]]}}
        else:
            props[name] = {kind: {}}
    return props


def _value(kind: str, v):
    if kind == "title":
        return {"title": [_text(str(v))]}
    if kind == "number":
        return {"number": v}
    if kind == "select":
        return {"select": {"name": v}}
    if kind == "date":
        return {"date": {"start": v.isoformat()}}
    if kind == "checkbox":
        return {"checkbox": bool(v)}
    if kind == "rich_text":
        return {"rich_text": [_text(v)] if v else []}
    raise ValueError(kind)


def page_id(link: str) -> str:
    m = re.findall(r"[0-9a-f]{32}", link.replace("-", "").lower())
    if not m:
        raise SystemExit(f"Couldn't find a page id in {link!r}. Paste the page's link (••• > Copy link).")
    return m[-1]


def build(api, t: dict, parent: str, links: dict, today: date, log=print) -> dict:
    """Builds template t under the parent page. Returns {"page": id, "url": ..., "dbs": {key: id}}."""
    page = api.call("POST", "/pages", {"parent": {"page_id": parent}, "icon": {"type": "emoji", "emoji": t["icon"]},
                                       "properties": {"title": {"title": [_text(t["name"].replace(" (free)", ""))]}}})
    pid = page["id"]
    log(f"  page: {t['name']}")
    dbs, buf = {}, []
    by_key = {d["key"]: d for d in t["dbs"]}

    def flush():
        while buf:
            chunk = buf[:100]
            del buf[:100]
            api.call("PATCH", f"/blocks/{pid}/children", {"children": chunk})

    for item in t["layout"]:
        if item[0] == "db":
            flush()
            d = by_key[item[1]]
            res = api.call("POST", "/databases", {"parent": {"type": "page_id", "page_id": pid}, "is_inline": True,
                                                  "icon": {"type": "emoji", "emoji": d["icon"]},
                                                  "title": [_text(d["title"])], "properties": _basic_schema(d)})
            dbs[d["key"]] = res["id"]
            log(f"  database: {d['title']}")
        elif item[0] == "children":
            flush()
            for child in t.get("children", []):
                build(api, child, pid, links, today, log)
        else:
            buf.append(_block(item, links))
    flush()

    for d in t["dbs"]:                                    # relations, then rename the synced side
        for name, kind, cfg in d["props"]:
            if kind != "relation":
                continue
            res = api.call("PATCH", f"/databases/{dbs[d['key']]}", {"properties": {name: {"relation": {
                "database_id": dbs[cfg["db"]], "type": "dual_property", "dual_property": {}}}}})
            synced = res["properties"][name]["relation"]["dual_property"]["synced_property_name"]
            if synced != cfg["reverse"]:
                api.call("PATCH", f"/databases/{dbs[cfg['db']]}", {"properties": {synced: {"name": cfg["reverse"]}}})
    for d in t["dbs"]:                                    # formulas, in the order listed (later ones use earlier ones)
        for name, kind, cfg in d["props"]:
            if kind == "formula":
                api.call("PATCH", f"/databases/{dbs[d['key']]}", {"properties": {name: {"formula": {"expression": cfg["expr"]}}}})
    log("  properties + formulas done")

    row_ids: dict[tuple[str, str], str] = {}
    ordered = sorted(t["dbs"], key=lambda d: any(k == "relation" for _, k, _ in d["props"]))
    for d in ordered:                                     # rows: relation targets first
        kinds = {n: (k, c) for n, k, c in d["props"]}
        for r in d["rows"]:
            props = {}
            for name, v in r.items():
                k, c = kinds[name]
                if k == "relation":
                    props[name] = {"relation": [{"id": row_ids[(c["db"], v)]}]} if v else {"relation": []}
                elif k == "date":
                    props[name] = _value(k, N.resolve_date(v, today))
                else:
                    props[name] = _value(k, v)
            res = api.call("POST", "/pages", {"parent": {"database_id": dbs[d["key"]]}, "properties": props})
            row_ids[(d["key"], r["Name"])] = res["id"]
        log(f"  {len(d['rows'])} example rows in {d['title']}")
    return {"page": pid, "url": page.get("url"), "dbs": dbs}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("template", choices=list(N.TEMPLATES) + ["all"])
    ap.add_argument("--parent", help="link to (or id of) the empty Notion page shared with your integration")
    ap.add_argument("--dry-run", action="store_true", help="print the API calls instead of making them")
    a = ap.parse_args()
    links = json.loads(LINKS.read_text()) if LINKS.exists() else {}
    if a.dry_run:
        api = DryRun()
        parent = "0" * 32
    else:
        token = os.environ.get("NOTION_TOKEN")
        if not token or not a.parent:
            raise SystemExit("Set NOTION_TOKEN and pass --parent (see the top of this file).")
        api, parent = NotionAPI(token), page_id(a.parent)
    slugs = list(N.TEMPLATES) if a.template == "all" else [a.template]
    for slug in slugs:
        print(f"Building {N.TEMPLATES[slug]['name']} ...")
        out = build(api, N.TEMPLATES[slug], parent, links, date.today())
        print(f"Done: {out['url']}")
        print("Next: add the views in BUILD.md, then Share > Publish > allow 'Duplicate as template'.\n")
    if a.dry_run:
        for method, path, body in api.calls:
            print(method, path, json.dumps(body)[:200] if body else "")
        print(f"\n{len(api.calls)} API calls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
