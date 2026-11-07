# Dinero Simple: start here

**Dinero Simple is paused until the week-8 gate.** Everything is written and kept in the repo. Nothing goes out
until a paid native reviewer has checked the lean set. This is the order to do things, and every blank you'll
need to fill.

## The order

| # | When | Step | Where |
|---|---|---|---|
| 1 | Now (Nov 2026), free | Check the name, buy the domain, reserve the YouTube handle and set up the channel page. **Upload nothing** | `CHANNEL_RESERVATION.md` §1–4 |
| 2 | Weeks 1–8 | Nothing for Dinero. MMS and Scam Decoded launch first (scouting's `two-brand-launch-plan.md` on PR #2) | — |
| 3 | **Week 8, around 10 Jan 2027** | Brand-3 gate: if all five checks pass, **1099 Money** goes live as brand 3. Dinero is brand 4 | PR #2 `two-brand-launch-plan.md` → "Criteria for adding brand 3" |
| 4 | Jan 2027 (your call: $45) | **Hire the reviewer:** post the job, send the paid 2-hour test, score it, and hire at 70+ | `reviewer/JOB_POST.md`, `reviewer/dist/Prueba-Pagada-Revision.pdf`, `reviewer/RUBRIC.md` |
| 5 | Jan 2027 | Reserve the other platforms' handles (TikTok as a personal account, Instagram + Threads, Facebook Page) | `CHANNEL_RESERVATION.md` §5 |
| 6 | Feb–Mar 2027 (your call: about $200–350, cap $500, plus about $35 for the attorney) | **Lean review.** Send `Lean-Revision-Espanol-Nativo.pdf` (about 10–14 h) to the reviewer and `Lean-Attorney-Review-Packet.pdf` (about 1.2 h) to a Spanish-reading immigration attorney or accredited representative (a bar referral service is $35 for 30 minutes) | `review/dist/`, project files `review-packets/` |
| 7 | Mar 2027 | Apply the fixes, rebuild, import, and record the passes in the review gate | `reviewer/WORKFLOW.md` |
| 8 | Late Mar 2027 | **Brand-4 gate:** the same five checks, now with 1099 Money running too, plus the go-live check | PR #2 plan + `CHANNEL_RESERVATION.md` §6 |
| 9 | **April 2027** | **Launch the lean set:** site, freebie, 5 welcome emails, the Kit, the bill-tracker printable, 14 posts over 4 weeks | `lean/LEAN_LAUNCH.md` → Go-live order, `POSTING_PLAN_LEAN.md` |
| 10 | After launch | Phase 2, one piece at a time: review with the full packets (Part 1 first), take the piece out of the hold, then remove its plan's banner | `review/REVIEW_PACKETS.md` |

Steps 2–3 belong to the other brands. If the week-8 gate fails, fix the failing check and look again in two
weeks. Dinero moves back by the same amount.

## Every blank, and where it lives

**Before the lean launch** (step 9):

| Blank | Now | Where to set it |
|---|---|---|
| Domain | `dinerosimple.netlify.app` | `sites/dinero-simple/site.json` `url` and `plausible_domain` (planned: `eldinerosimple.com`) |
| Handle, if not `@dinerosimple` | `@dinerosimple` | `brands/dinero-simple.yaml` `accounts`, `site.json` `socials` |
| Contact email | `hola@example.com` | `site.json` `contact_email` |
| Email signup (Sender) | form `action` and `email_field` empty | `site.json` `email` (`action`, `email_field`); see `sites/dinero-simple/README.md` |
| Welcome emails | not loaded | Load the 5 emails from `brands/sequences/dinero-simple.yaml` into Sender, with the template language set to **Spanish** |
| Credit-guide link in email day 5 | `https://example.com/credito-sin-seguro-social/` | `brands/sequences/dinero-simple.yaml` `links.credito_guia`. The page is phase 2, so either drop the link from day 5 for the lean launch or publish that page first |
| Kit Gumroad URL | `https://example.gumroad.com/l/recortar-gastos` | `sites/dinero-simple/content/products/el-kit-para-recortar-gastos.md` `buy_url` **and** `brands/dinero-simple.yaml` `products` |
| Bill-tracker price | `[PRICE]` (suggested $5–7) | `launch/dinero-simple/imprimibles/build_imprimibles.py` `PRICE`, then rebuild; list it on Etsy and Gumroad |
| Reviewer's name in the gate | — | `factory review-gate pass <id> native_review --by "Name"` (`reviewer/WORKFLOW.md`) |
| Spanish voice | — | Kokoro `ef_dora` (default) or `em_alex`, never the English voice |

**Phase 2 only** (leave these until those pieces are reviewed):

| Blank | Where |
|---|---|
| Other products' Gumroad URLs (Presupuesto $12, Fecha $17, Invertir $19, Paquete $29) and the launch codes RECORTE5 / FECHA5 / INVERTIR5 | `brands/dinero-simple.yaml` `products`, the site's `content/products/*.md`, the store |
| Free-tool links (PR #8 apps) | `site.json` `tool_urls` (`REPLACE_ME` until deployed) |
| Affiliate URLs (remittance, tax prep, ITIN bank and card) | `site.json` `go_links`. Only real, approved programs; remittance content still names no provider in ranked form |
| 2027 payroll tables | `/calculadora-de-sueldo/`: update `TABLES` before any January 2027 tax content |
| Workbook and other printables' prices | `primer-ano/` (Gumroad only), `imprimibles/` |

## Don'ts

- Don't post or upload anything outside `POSTING_PLAN_LEAN.md` until it has been reviewed. The review gate and the
  site hold enforce this.
- Don't send `reviewer/ANSWER_KEY.md`, and don't recruit unpaid volunteers.
- Immigration questions go to a licensed immigration attorney or a DOJ-accredited representative, never a notario.
- After running any month builder, run `python3 launch/dinero-simple/lean/lean_launch.py` again, so the phase-2
  banners and tags come back.
