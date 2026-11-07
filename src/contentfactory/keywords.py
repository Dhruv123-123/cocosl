"""`factory keyword-check`: scouting's keyword sheets against what's scheduled, so the search-box checks get done in one sitting.

    factory keyword-check                 # titles that are scheduled (or approved) whose phrase isn't confirmed yet
    factory keyword-check --all           # every unticked row, scheduled or not
    factory keyword-check mark mms:4 yes  # confirmed in the dropdown: writes "yes" into the sheet
    factory keyword-check mark mms:4 no --use "how to freeze credit"   # a different wording came up
    factory keyword-check go              # one sitting: asks yes / no / new wording for each, in posting order

Sheets: research/scouting/keywords-*.csv (scouting, PR #2) and data/keywords/*.csv under the factory
home, or `--sheet <csv>`. The columns are scouting's: plan_day, current_title, target_phrase,
suggested_title ("keep" or a new title) and confirmed_in_autocomplete (blank until checked). A sheet's
brand comes from its `brand` column or its file name (keywords-mms-... is money-made-simple).

The check itself is by hand, as scouting's sheet says: type the first two or three words of the phrase
into YouTube's and Pinterest's search box (private window) and see whether it shows up in the dropdown.
Nothing here searches anything or changes a post: a "no --use" only notes the wording to use in the sheet.
"""
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

DONE_COL = "confirmed_in_autocomplete"
ALIASES = {"mms": "money-made-simple", "scam-decoded": "scam-decoded", "1099": "1099-money",
           "1099-money": "1099-money", "dinero": "dinero-simple", "dinero-simple": "dinero-simple"}
MATCH = 0.82
OPEN_POST = ("approved", "scheduled", "in_review", "rendered", "scripted", "blocked")


@dataclass
class Row:
    sheet: Path
    key: str           # sheet key, e.g. "mms"
    n: int             # 1-based data row in the sheet
    brand: str
    data: dict
    posts: list = field(default_factory=list)   # [{id, title, status, when}]

    @property
    def ref(self) -> str:
        return f"{self.key}:{self.n}"

    @property
    def phrase(self) -> str:
        return (self.data.get("target_phrase") or "").strip()

    @property
    def ticked(self) -> str:
        return (self.data.get(DONE_COL) or "").strip().lower()

    @property
    def suggested(self) -> str:
        s = (self.data.get("suggested_title") or "").strip()
        return "" if s.lower() in ("", "keep") else s

    @property
    def first_when(self) -> str:
        return min((p["when"] for p in self.posts if p["when"]), default="")


def _norm(t: str) -> str:
    return re.sub(r"[^a-z0-9$]+", " ", (t or "").lower()).strip()


def similar(a: str, b: str) -> float:
    a, b = _norm(a), _norm(b)
    if not a or not b:
        return 0.0
    return 1.0 if a == b else SequenceMatcher(None, a, b).ratio()


def sheet_key(path: Path) -> str:
    stem = path.stem.lower()
    stem = re.sub(r"^keywords-", "", stem)
    return re.sub(r"-first-\d+$", "", stem) or stem


def brand_for(path: Path, known: list[str], data: dict | None = None) -> str:
    if data and (data.get("brand") or "").strip():
        return data["brand"].strip()
    key = sheet_key(path)
    for k in sorted(known, key=len, reverse=True):
        if key.startswith(k):
            return k
    for alias, slug in sorted(ALIASES.items(), key=lambda x: -len(x[0])):
        if key.startswith(alias):
            return slug
    return key


def sheets(factory, extra: list[str] | None = None) -> list[Path]:
    home = Path(factory.settings.home)
    found = sorted((home / "research" / "scouting").glob("keywords-*.csv")) + sorted((home / "data" / "keywords").glob("*.csv"))
    found += [Path(p) for p in (extra or [])]
    seen, out = set(), []
    for p in found:
        r = p.resolve()
        if r not in seen and p.is_file():
            seen.add(r)
            out.append(p)
    return out


def read(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        return list(rd.fieldnames or []), [dict(r) for r in rd]


def load(factory, extra: list[str] | None = None) -> list[Row]:
    """Every sheet row, with the posts whose title matches its current or suggested title."""
    known = list(factory.brands())
    rows: list[Row] = []
    for p in sheets(factory, extra):
        _, data = read(p)
        for n, d in enumerate(data, 1):
            rows.append(Row(p, sheet_key(p), n, brand_for(p, known, d), d))
    by_brand: dict[str, list[dict]] = {}
    for r in rows:
        if r.brand not in by_brand:
            posts = factory.db.query(
                f"SELECT id, title, status FROM posts WHERE brand = ? AND status IN ({','.join('?' * len(OPEN_POST))})",
                [r.brand, *OPEN_POST])
            when = {x["post_id"]: x["w"] for x in factory.db.query(
                "SELECT p.post_id, MIN(p.scheduled_at) AS w FROM publications p JOIN posts s ON s.id = p.post_id "
                "WHERE s.brand = ? AND p.status IN ('queued', 'manual', 'dry_run') GROUP BY p.post_id", [r.brand])}
            by_brand[r.brand] = [{**p, "when": when.get(p["id"], "")} for p in posts]
        for p in by_brand[r.brand]:
            score = max(similar(p["title"], r.data.get("current_title", "")), similar(p["title"], r.suggested))
            if score >= MATCH:
                r.posts.append({**p, "score": round(score, 2),
                                "retitled": bool(r.suggested) and similar(p["title"], r.suggested) >= MATCH})
    return rows


def todo(rows: list[Row], everything: bool = False) -> list[Row]:
    """Unticked rows; by default only those with a scheduled or approved post, soonest first."""
    out = [r for r in rows if not r.ticked and r.phrase]
    if not everything:
        out = [r for r in out if any(p["when"] or p["status"] in ("approved", "scheduled") for p in r.posts)]
    return sorted(out, key=lambda r: (r.first_when or "9999", r.brand, r.n))


def probe(phrase: str) -> str:
    """The first two or three words to type into the search box."""
    words = phrase.split("/")[0].split()
    return " ".join(words[:3] if len(words) > 3 else words[:2] if len(words) == 3 else words)


def mark(factory, ref: str, answer: str, use: str = "", extra: list[str] | None = None) -> Row:
    answer = answer.strip().lower()
    if answer not in ("yes", "no"):
        raise ValueError("Answer yes or no")
    key, _, n = ref.partition(":")
    for p in sheets(factory, extra):
        if sheet_key(p) != key:
            continue
        fields, data = read(p)
        i = int(n) - 1
        if not 0 <= i < len(data):
            raise KeyError(f"{p.name} has {len(data)} rows; no row {n}")
        if DONE_COL not in fields:
            fields.append(DONE_COL)
        data[i][DONE_COL] = answer if not use else f"{answer}; use: {use.strip()}"
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(data)
        p.write_text(buf.getvalue(), encoding="utf-8")
        factory.db.log("keywords.mark", "sheet", 0, {"sheet": p.name, "row": int(n), "answer": data[i][DONE_COL]})
        return Row(p, key, int(n), brand_for(p, list(factory.brands()), data[i]), data[i])
    raise KeyError(f"No keyword sheet '{key}' (sheets: {', '.join(sheet_key(p) for p in sheets(factory, extra)) or 'none found'})")


def to_text(rows: list[Row], all_rows: list[Row], everything: bool = False) -> str:
    if not all_rows:
        return ("No keyword sheets found. They're scouting's research/scouting/keywords-*.csv (PR #2): merge it, "
                "or copy the CSVs into data/keywords/.\n")
    done = sum(1 for r in all_rows if r.ticked)
    out = [f"Search-box check: {len(rows)} to do" + ("" if everything else " for scheduled titles")
           + f" · {done} of {len(all_rows)} rows done across {len({r.sheet for r in all_rows})} sheet(s)",
           "Type the words in quotes into YouTube's and Pinterest's search box (private window). "
           "In the dropdown? `factory keyword-check mark <ref> yes`. Different wording? "
           "`... mark <ref> no --use \"<wording>\"`. Or do them all with `factory keyword-check go`.", ""]
    for r in rows:
        when = r.first_when[:16].replace("T", " ") if r.first_when else "not scheduled"
        out.append(f"{r.ref:9s} [{r.brand}] {when} · type \"{probe(r.phrase)}\" → want \"{r.phrase}\"")
        for p in r.posts[:2]:
            note = "" if not r.suggested else (" · retitled" if p["retitled"] else f" · title not updated yet: \"{r.suggested}\"")
            out.append(f"          #{p['id']} {p['title'][:70]}{note}")
        if not r.posts:
            out.append(f"          (no post matches \"{(r.data.get('current_title') or '')[:60]}\")")
    if not rows:
        out.append("Nothing waiting: every scheduled title's phrase is checked." if not everything else "Every row is checked.")
    return "\n".join(out) + "\n"


def register(sub, factory_fn) -> None:
    s = sub.add_parser("keyword-check", help="scheduled titles whose search phrase isn't confirmed in the search box yet "
                                             "(scouting's keyword sheets); mark them yes/no")
    s.add_argument("action", nargs="?", default="list", choices=["list", "mark", "go"])
    s.add_argument("ref", nargs="?", default="", help="for mark: the row, e.g. mms:4")
    s.add_argument("answer", nargs="?", default="", help="for mark: yes or no")
    s.add_argument("--use", default="", help="the wording the dropdown showed instead")
    s.add_argument("--all", action="store_true", help="every unticked row, not only scheduled titles")
    s.add_argument("--sheet", action="append", default=[], help="another keyword CSV (repeatable)")

    def cmd(a):
        f = factory_fn(a)
        if a.action == "mark":
            if not a.ref or not a.answer:
                raise SystemExit("usage: factory keyword-check mark <ref> yes|no [--use \"wording\"]")
            r = mark(f, a.ref, a.answer, a.use, a.sheet)
            print(f"{r.ref}: {r.data[DONE_COL]} ({r.sheet.name})")
            return
        all_rows = load(f, a.sheet)
        rows = todo(all_rows, a.all)
        if a.action == "list":
            print(to_text(rows, all_rows, a.all), end="")
            return
        if not rows:
            print(to_text(rows, all_rows, a.all), end="")
            return
        print(f"{len(rows)} to check. For each: y = in the dropdown, n = not there, or type the wording that "
              "showed instead. Enter skips, q stops.\n")
        n_done = 0
        for r in rows:
            post = f" (#{r.posts[0]['id']} {r.posts[0]['title'][:50]})" if r.posts else ""
            try:
                ans = input(f"{r.ref} type \"{probe(r.phrase)}\", want \"{r.phrase}\"{post}: ").strip()
            except EOFError:
                break
            if ans.lower() == "q":
                break
            if not ans:
                continue
            if ans.lower() in ("y", "yes"):
                mark(f, r.ref, "yes", "", a.sheet)
            elif ans.lower() in ("n", "no"):
                mark(f, r.ref, "no", "", a.sheet)
            else:
                mark(f, r.ref, "no", ans, a.sheet)
            n_done += 1
        print(f"\n{n_done} marked. {len(rows) - n_done} left.")
    s.set_defaults(func=cmd)
