# Reviewer workflow: from the PDF to the review gate

How a native-speaker review (and an attorney review) turns into posts the pipeline will publish. The reviewer works
only on paper (the numbered PDF). Dhruv makes the fixes and records each pass in the factory's review gate. Nothing
from Dinero Simple can be approved, scheduled or exported until its gate is passed. The brand sets
`review_stages: [native_review]`, and items flagged ATTORNEY REVIEW also need `legal_review`.

## The short version

1. **Reviewer:** marks every row in `Lean-Revision-Espanol-Nativo.pdf` **OK** or **Cambiar** (with the fix), and
   flags facts.
2. **Dhruv:** makes the fixes in the source files and rebuilds. Then he imports the lean pack and records a pass for
   every post whose rows are all OK.
3. **Dhruv:** ticks the facts and approves. Only then can a post be scheduled.

## 1. Reviewer: marking the PDF

Every row has a number (N-012.2 is entry 12, row 2) and two boxes.

| Mark | Means | Counts as |
|---|---|---|
| ☑ **OK** | Reads naturally for a US Latino reader, tú register, nothing to change | pass for that row |
| ☑ **Cambiar** + the new wording in the comment column | Needs a change; the reviewer writes it | pass once Dhruv applies it word for word |
| **FLAG** + why | A number, date, rule or claim that looks wrong. The reviewer doesn't rewrite facts | **fail** until the fact-check settles it |
| *(blank)* | Not reviewed | **fail**: not reviewed is never a pass |

Repeated lines (R-1, R-2, …) are reviewed once at the front; their mark applies everywhere they appear.

The reviewer's own rules (the same as the paid test):
- tú, never usted or vosotros;
- US Latino words (celular, cuenta de cheques, renta);
- on-screen text stays short (12 words at most);
- `{placeholders}` stay as they are.

The attorney marks `Lean-Attorney-Review-Packet.pdf` the same way. The "standard lines" at the front (S-1, S-2,
…) are approved once and cover every piece that uses them.

## 2. Dhruv: fixes first, then import

Make the fixes **before** importing, so the posts in the factory already carry the reviewed text:

1. Apply each Cambiar in its source file:
   - posts: `launch/dinero-simple/src/*.py`, using the title shown in the PDF;
   - site pages: `sites/dinero-simple/content/`;
   - emails: `brands/sequences/dinero-simple.yaml`;
   - Kit guide: `launch/dinero-simple/products/`.
2. Rebuild:
   - the month builders you touched;
   - then `python3 launch/dinero-simple/lean/lean_launch.py`;
   - then `python3 launch/dinero-simple/review/build_packets.py --pdf`.
3. For any row you weren't sure how to apply, send the reviewer that page again. It takes 10 minutes and they
   confirm it.
4. Import the lean posts:

```
factory import launch/dinero-simple/content-lean.json --brand dinero-simple
factory review-gate list --status native_review --brand dinero-simple
```

Every lean post now shows `native_review`. Items flagged ATTORNEY REVIEW would also show `legal_review`, but the
lean posts have none.

## 3. Dhruv: record the passes

**A post passes native review** when every row of its entry is OK, or is Cambiar and applied word for word. It
also needs no open FLAG and no blank row.

Record each pass with the reviewer's name, so the record says who read it:

```
factory review-gate pass 42 native_review --by "Ana López (native reviewer)" --note "packet N-012: 2 changes applied"
factory review-gate pass 42 legal_review  --by "J. Ruiz, Esq. (immigration attorney)" --note "A-001 OK"
```

**Or use the dashboard's fast review** (`/review/fast?brand=dinero-simple`), one post at a time:

| Key | Does |
|---|---|
| **N** | native review passed |
| **L** | legal review passed |
| **1**–**9** | tick claim N as fact-checked |
| **C** | tick all claims |
| **E** | edit the caption |
| **A** | approve (and schedule); works only once every review it needs is passed |
| **R** | reject (asks why) |
| **J** / **K** | next / previous |
| **?** | help |

The N and L buttons record the reviewer as "dashboard". For an audit trail with the reviewer's name, use the
`--by` command above. Use the dashboard for speed on posts whose rows are all OK.

**A post fails** when it has any open FLAG, any blank row, or a Cambiar you couldn't apply. Leave it in
`native_review`. If it needs a real rewrite, send it back, and it returns to draft with its passed reviews cleared:

```
factory review-gate send-back 42 --note "N-012.3: hook needs rewriting"
```

## 4. Things that aren't posts

The welcome emails, site pages, the freebie, the Kit guide and the printable aren't in the review gate. Their
gates are these:
- **Site pages and products:** a page goes live only when its name comes out of the `site.json` hold. The lean
  pages are already out; everything else stays held until reviewed.
- **Welcome emails:** load them into Sender only after their rows (and the attorney's rows for days 3 and 5) are
  all OK.
- **Freebie, Kit guide, printable:** rebuild the PDF after the fixes, then upload.

Keep the marked PDFs. They are the record of who reviewed what.

## 5. What "done" looks like for the lean launch

- Every lean post shows `approved` in `factory review-gate list --brand dinero-simple`.
- The lean site pages, the emails, the freebie, the Kit and the printable have every row OK.
- The attorney's two lean rows and the standard lines are OK.
- Then follow `lean/LEAN_LAUNCH.md` → Go-live order.
