# Dry run: Money Made Simple launch week 1, from a fresh install

Run on 2026-11-07, 09:50–10:45 UTC (Day 1). Setup:
- A fresh clone of `main` (e934cbb) with all 13 PRs merged locally in GO_LIVE order: #1, #3, #2, #4, #5, #6, #8, #12, #11, #9, #10, #7, #13.
- `pip install -e ".[claude]"` in a new venv, then `factory init`, with no keys set.
- Followed `docs/GO_LIVE.md` (PR #7) Stages 0, 4 and 6, plus R3, R4, R6 and R7.
- Followed `launch/money-made-simple/LAUNCH_WEEK.md` (PR #5) for Days 1–7.

Nothing was posted (dry run, no accounts).

**Result:** the steps work end to end. Four real bugs were found and fixed on `main` (B1 to B4 below). Five places in the docs or brand files don't match each other; their owners need to fix them (D1 to D5).

## What I ran, and how long it took

| Step | Command | Time | Result |
|---|---|---|---|
| Install | `pip install -e ".[claude]"` | 1 min | ok |
| Set up | `factory init`, `factory doctor --offline` | 2 s | 0 problems, 17 warnings (see B4) |
| Launch mode | `factory launch-mode two-brand` | 0 s | ok |
| Import | `factory import launch/money-made-simple/content.json --brand money-made-simple` | **≈ 35 min** with the silent voice: about 1 min per Short or carousel, 9 min per long video | ok; my 25-min timeout cut it off at #24, and re-running picked up exactly where it stopped |
| Review | `factory review`, `review-gate`, `triage`, `today --15min` | 1–5 s each | ok: 24 in review, matching GO_LIVE R4 |
| Approve Days 1–7 | `factory approve <id> --yes-i-checked --schedule`, in LAUNCH_WEEK order | 1 s each | **calendar wrong** (B1, B2), fixed |
| Week 1 | `today --date …`, `manual`, `export-week --manual-only`, `keyword-check`, `weekly-review`, `publish` | 1–20 s | ok, see F1 to F5 |

## Bugs fixed on `main` (one commit)

**B1 · A post's platforms split across two days.** Day 2's Short went to Facebook at 19:00 on Day 1, because that evening slot was free. YouTube and Instagram had it at 12:30 on Day 2.
- Fix: scheduling now picks one local day for all of a post's platforms. The busiest platform decides the day, and the others take their first free slot that day (`scheduler.same_day_slots`).

**B2 · The plan's days couldn't be kept.** Approving in LAUNCH_WEEK order still pushed posts onto other days:
- Day 6's Short landed on Day 8, because `shorts_per_week: 5` sat under the plan's 7 a week.
- Day 3's carousel moved to Day 2 evening.

Fixes:
- A pack item can now carry `"date": "YYYY-MM-DD"`. `factory import` saves it, and re-running import adds dates to posts that are already imported.
- Scheduling uses that day's slots (Shorts at 12:30, TikTok at 18:00, carousels and long videos at 19:00) and skips the weekly format count, because the plan already set the mix. The daily cap and the per-platform weekly caps still apply.
- A date in the past is ignored, and the post takes the next free slot as before.
- `schedule --all` schedules dated posts in date order: Shorts first, then long videos, then carousels, so the Short takes the earlier slot on a shared platform.
- Checked on the dry-run calendar: with dates added, all 12 Day 1–7 posts land on their LAUNCH_WEEK day and time, including Sunday's long video at 19:00 and its pin at 11:30.

**B3 · `factory reslot` pulled posts onto earlier days.** It re-packed everything from now on, so a gap day got filled with the next day's post. Now each publication keeps its own day (or later) and only its time changes.

**B4 · Paused brands cluttered the checks.** In two-brand launch mode, `doctor` and `launch-check` still listed every placeholder and missing key for 1099 Money, Dinero Simple and Tiny Histories: 17 warnings, about 30 yellow lines. Now:
- A paused brand with nothing scheduled shows as one line: "paused (launch mode), nothing scheduled".
- A paused brand that still has posts queued is checked as before, because those posts would still go out. Launch mode only filters what you see; it doesn't stop posting.

Also on `main` already (e934cbb): `scripts/gen_commands.py` was a merge hotspot for #5, #9 and #11. It now has one command per line, and a new command needs no edit there.

## Docs and brand files that don't match (for their owners; not changed here)

- **D1 · Add dates to the MMS pack (MMS thread, PR #5).**
  - Add `"date"` to the 24 items in `launch/money-made-simple/content.json`, from the LAUNCH_WEEK table (Day 1 = 2026-11-07).
  - The mapping by position: #0 and #14 on 11-07; #6 and #23 on 11-08; #1 and #15 on 11-09; #3 on 11-10; #5 and #18 on 11-11; #8 on 11-12; #4 and #17 on 11-13; #10 on 11-14; #2, #16 and #22 on 11-15; #7 on 11-16; #9 and #19 on 11-17; #12 and #21 on 11-18; #11 on 11-19; #13 and #20 on 11-20.
  - If Day 1 slips, re-import with shifted dates, or let the past dates fall back to the next free slots.
- **D2 · Fixed times for carousels and long videos (MMS brand file).** If you approve a carousel before that day's Short, the carousel takes Instagram's 12:30 slot and the Reel moves to 19:00. The same happens with the long video on YouTube. Fix: add `"instagram:carousel": ["19:00"]` and `"youtube:long": ["19:00"]` to `platform_times` in `brands/money-made-simple.yaml`.
- **D3 · Pinterest pins: the factory and LAUNCH_WEEK disagree.**
  - The factory schedules every carousel and long video as a Pinterest pin by hand, 6 in Days 1–7, using the post's own slide.
  - LAUNCH_WEEK says the first two weeks get 4 site pins a week (the `site/pins/` images, linking to blog pages), and only once the page is live.
  - Pick one. To follow LAUNCH_WEEK, take `carousel` and `long` out of the Pinterest account's `formats` for the fortnight, or skip those packages in `factory manual`.
- **D4 · GO_LIVE R3 still uses the old titles and plan (go-live thread, PR #7).**
  - R3 points to `POSTING_PLAN.md` with the pre-SEO titles (e.g. "Feel behind on money? A 30-day reset plan", "Paid in full, score still dropped?") and times "12:30 and 19:00 ET".
  - LAUNCH_WEEK.md is now the source, with retitled posts, TikTok at 18:00 and carousels at 19:00 on Instagram.
  - Stage 4's "Post by hand from `content-factory/launch-pack/POSTING_PLAN.md`" should point to LAUNCH_WEEK.md too.
- **D5 · Two native-speaker sign-offs (Dinero Simple thread, PR #11).**
  - GO_LIVE R7 and the guardrail in `guardrails.py` ask for `factory review-language <id> --by NAME`.
  - Main's review gate asks for `factory review-gate pass <id> native_review`, and #11 now uses that.
  - A Dinero post may need both. Keep one; the review gate is the one that blocks approval.

## Friction worth knowing (no change needed)

- **F1 · The import is long.** About 35 minutes for 24 posts with the silent voice; with Kokoro, add the voice time. Start it before anything else, or use `--queue` with the renderer service. It's safe to stop and re-run.
- **F2 · Don't run two imports at once.** Both render the same unfinished post into the same `.partial` folder, and one crashes. Re-running afterwards fixes it.
- **F3 · Set the launch date.** Until a post is marked published, the weekly review and scorecard say "day ?". Set `FACTORY_LAUNCH_DATE=2026-11-07` in `.env`; the line is now in `.env.example`.
- **F4 · Export two weeks at a time.** `export-week` works in Monday–Sunday weeks, and the launch week runs Saturday to Friday, so Days 1–2 are in one zip and Days 3–9 in the next. Use `factory export-week money-made-simple --weeks 2 --manual-only`. The zip is large (about 230 MB for one week of TikTok and Pinterest packages) because it holds the video files.
- **F5 · Search-box checks show up once posts are scheduled.** After scheduling, `factory keyword-check` lists 8 Day 1–7 titles. It takes about 10 minutes with `factory keyword-check go`, and it's on the Sunday weekly review.

## Not covered

Real voice (Kokoro), real accounts, Postiz, the live site and email signup, and Gumroad. All of these need keys or accounts. The steps that depend on them are in GO_LIVE Stages 1, 3, 5 and 6.
