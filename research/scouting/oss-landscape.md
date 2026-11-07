# Open-source landscape, round 3: money apps, tax engines, and where video, caption and TTS stand

Pulled 2026-11-07 from GitHub's search API (stars, licence and last push are as of today). Licence texts
were read from each repo's `LICENSE` file where GitHub's SPDX field said `NOASSERTION`. This round adds the
**money** side: budgeting apps, tax and finance libraries, and freelancer tools. It also re-checks the video,
caption and TTS picks from `github-repos.md` against what `main` has since built.

**Licence rules** (same as `github-repos.md`):
- **MIT, BSD, Apache, CC0:** fine to use and modify commercially.
- **CC BY:** fine with credit.
- **GPL:** call it as a separate program and never copy its code in.
- **AGPL:** run it unmodified as its own service only, and never vendor it into cocosl (cocosl is MIT).
- **Elastic License 2.0 (ELv2):** self-hosting for yourself is fine, but you can't offer it to others
  as a hosted service.

## 1. Budgeting and personal-finance apps

| Repo | Stars | Licence | Last push | What it is | Use for us |
|---|---|---|---|---|---|
| **actualbudget/actual** | 30.1K | **MIT** | 2026-11-06 | Local-first envelope budgeting app with sync, bank import, and an official Node API (`@actual-app/api`) | **Content and a product bonus, not code.** MIT means we could ship an "Actual Budget starter file" (categories and rules matching The 20-Minute Budget) as a free bonus, and make "set up a free budget app in 15 minutes" videos showing the real app on screen. That screen footage is also the original element YouTube wants |
| **firefly-iii/firefly-iii** | 25.1K | **AGPL-3.0** | 2026-11-07 | Self-hosted double-entry finance manager with rules, budgets and reports | **Content only.** A good "free, private alternative" topic for MMS. Never vendor it, and only run it unmodified if we ever host a demo |
| maybe-finance/maybe | 54.2K | AGPL-3.0 | **archived** (Jul 2025) | Former all-in-one finance app | **Avoid.** Archived. Mention only as history |
| we-promise/sure | 10.8K | AGPL-3.0 | 2026-11-07 | Community fork that continues Maybe | Watch. Same AGPL limits |
| **ellite/Wallos** | 8.8K | GPL-3.0 | 2026-11-01 | Self-hosted subscription tracker | **Content.** It fits the Bill Cut Kit exactly ("find every repeating charge"). It's a free tool to recommend alongside our kit. GPL, so we link to it rather than copying it |
| beancount/fava | 2.6K | MIT | 2026-11-03 | Web UI for plain-text accounting (Beancount) | Skip. Too technical for our audience |
| budgetzero/budgetzero | 657 | AGPL-3.0 | 2026-11-07 | Zero-based budgeting web app | Skip. Small, AGPL |

**Takeaway:** we shouldn't build a budgeting app. Two mature free ones exist: Actual (MIT) and Firefly III
(AGPL). The opportunity is **teaching people to use them**. The tutorials can show the real app on screen,
which is honest original content, and link our paid templates as the "plan" that sits on top of the free app.

## 2. Tax, calculation and finance libraries

| Repo | Stars | Licence | Last push | What it is | Use for us |
|---|---|---|---|---|---|
| **PSLmodels/Tax-Calculator** | 316 | **CC0-1.0** (public domain in the US; verified from its LICENSE) | 2026-11-05 | US federal income and payroll tax model, used in policy research | **Use as a test oracle.** Check the federal tax numbers on the MMS salary pages and the 1099 Money quarterly calculator against it in a test. It's heavy (pandas, numba), so make it a dev-only dependency that runs in CI or by hand, never in the site build |
| **numpy/numpy-financial** | 414 | **BSD-3-Clause** | 2026-11-04 | `pmt`, `nper`, `fv`, `rate`, `irr`: the standard loan and compounding maths | **Use** in tests for the debt-payoff and compound-growth numbers in scripts and pages. It's small, so it can sit beside the factory's fact-check step |
| PolicyEngine/policyengine-us | 171 | AGPL-3.0 | 2026-11-07 | Full US tax and benefits rules engine (state taxes and credits too) | **Reference only.** It would be the best source for state-level checks, but it's AGPL. Compare against its public web calculator by hand rather than importing it |

## 3. Freelancer tools (for 1099 Money's compare pages)

| Repo | Stars | Licence | Last push | Note |
|---|---|---|---|---|
| invoiceninja/invoiceninja | 10.5K | **Elastic License 2.0** (verified) | 2026-11-06 | Invoicing, quotes and time tracking. Self-hosting for your own business is fine, but offering it as a hosted service isn't. A good "free invoicing" option for readers to self-host |
| SolidInvoice/SolidInvoice | 983 | MIT | 2026-11-06 | Simple invoicing; a smaller, permissive alternative |
| kimai/kimai | 5.1K | AGPL-3.0 | 2026-11-06 | Time tracking for freelancers |

These belong on 1099 Money's "free tools" compare page with honest notes on the licence and setup effort. They
aren't for us to run.

## 4. Scam and security resources (for Scam Decoded)

| Repo | Stars | Licence | Last push | Use for us |
|---|---|---|---|---|
| **Lissy93/personal-security-checklist** | 22.7K | **CC BY 4.0** (verified) | 2026-11-01 | 300+ security and privacy tips. **We can adapt sections** into Scam Decoded checklists and videos, with credit, a link and a "modified" note, as CC BY requires. Our Scam-Proof Checklist stays our own, and this is a cross-check that we haven't missed a basic |

## 5. Video, captions and TTS: re-checked against `main`

`github-repos.md` (rounds 1-2) scored 72 repos. Since then, `main` has built most of what it recommended:

| Recommendation (round 1-2) | Status on `main` |
|---|---|
| **Kokoro / Kokoro-FastAPI** (Apache-2.0) as the free voice | **Built:** `media/tts.py` has a `kokoro` provider (FastAPI server or local package) |
| **faster-whisper / stable-ts** (MIT) for word-accurate captions | **Built:** `media/captions.py` uses Kokoro's word timestamps, or whisper alignment with `FACTORY_ALIGN=whisper` |
| A human element (own voice) | **Built:** drop a recording into a post's voice slot ("own voice") |
| Original element in long videos, and no sameness | **Built:** long videos need a chart of their own numbers or the owner's footage, and the look varies against recent posts |
| TikTok without the API | **Built:** posting packages are made for posting by hand, and they show in Today and the calendar |
| **auto-editor** (Unlicense) to cut silences in human recordings | Not built. Still the right tool for Dhruv's narration and screen recordings |
| **Chatterbox** (MIT) or **Qwen3-TTS** (Apache-2.0) as a more expressive voice | Not built. Optional; Kokoro is enough to launch |

**Changes since round 2:** none that change a verdict. The licences re-checked today match `repos.csv`.
Kokoro, faster-whisper, whisperX and stable-ts are still permissive. F5-TTS weights are still
non-commercial. MoneyPrinterV2 is still AGPL with browser-automated posting, so avoid it.

## 5 recommendations, in order

1. **Make "free app + our plan" tutorials, starting with Actual Budget.**
   - Screen-record the real app (MIT, so no licence issue) setting up The 20-Minute Budget's categories.
   - Ship an Actual starter file as a free bonus in the $12 budget product.
   - It's honest original footage (the YouTube inauthentic-content fix), a genuinely useful lesson, and a
     natural pitch.
   - Brand: MMS, then the same in Spanish for Dinero Simple.
2. **Add numpy-financial and Tax-Calculator as test oracles.**
   - A dev-only test that recomputes the loan, payoff and compounding numbers the factory and sites print,
     and the federal tax on each salary band, then fails if ours drift by more than $1.
   - Both are permissive (BSD-3, CC0). Neither goes into the runtime.
   - This protects the "a human checks every number" promise with something automatic.
3. **Use the CC BY security checklist as Scam Decoded's cross-check.**
   - Compare our Scam-Proof Checklist and the Family Kit against it, and add anything basic we missed, in
     our own words.
   - Where we adapt a section closely, credit it as CC BY 4.0 requires.
4. **Wire in auto-editor** (Unlicense) for Dhruv's narration and screen recordings, so the "own voice" and
   screen-footage paths don't need hand trimming. It's a CLI call before the existing own-voice step.
5. **Recommend free tools on the compare pages, don't host them.** Wallos for Bill Cut Kit buyers.
   Invoice Ninja (ELv2), SolidInvoice (MIT) and Kimai (AGPL) on 1099 Money's free-tools page, each with an
   honest licence note and no affiliate link. That's useful content, with nothing we'd have to run or
   maintain.

**Not recommended:** building our own budgeting app (two mature free ones exist), vendoring any AGPL repo
(Firefly III, Maybe/Sure, PolicyEngine, Kimai, OpenMontage, Postiz), or any "faceless generator" repo
that mass-produces stock-footage videos. Those are exactly what YouTube's inauthentic-content rule targets.
