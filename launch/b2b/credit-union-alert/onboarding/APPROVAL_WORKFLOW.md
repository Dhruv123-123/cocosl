# Approval workflow

Every issue needs a written yes from the credit union before members see it. The credit union sends;
we never do. This page is for us and can be shared with the client as-is.

## Who does what

| Role | Who | Does |
|---|---|---|
| Writer | Dhruv | Writes, fact-checks and builds each issue; makes edits; keeps the log. |
| Reviewer | The client's named compliance reviewer (form item 1.4) | Reads each issue and approves it, asks for changes, or holds it. |
| Sender | The client's marketing contact | Loads the approved email into their platform, posts the social image, puts up the lobby slide. |

One person on the client side can be both reviewer and sender.

## Once, at the start: the template sign-off

Before the first real issue, the reviewer approves the **template**: the footer, insurance statement,
"we will never ask" line, logo, colors and phone number. Log it as issue `TEMPLATE`. After that,
weekly reviews are about the content only. Any later change to those fixed parts gets a new
`TEMPLATE` sign-off.

## Every week

| Day (member send = day 0, a Tuesday) | Step |
|---|---|
| **Day −7, Tuesday** | Dhruv emails the pack (delivery email in `../DELIVERY_WORKFLOW.md`), with the sources list and "reply APPROVED, or send changes, by Friday". Log the row with `delivered_at`. |
| Day −7 to −4 | Reviewer reads it. The sources file and staff brief are there to make this quick. |
| **Day −4, Friday, 5 pm their time** | Edit deadline. |
| Day −3, Monday | Dhruv applies any edits, rebuilds, and resends the full pack marked **v2**. Reviewer confirms v2. |
| **Day 0, Tuesday** | Sender sends. |

### What counts as an approval

- A reply from the reviewer (or someone they name in writing) that says the issue is approved, about
  a named version: "2027-02-a v1 approved" or a reply on the v1 email saying "approved".
- **Silence is not approval.** If nothing comes back by Monday, send one short note ("No reply yet on
  this week's issue; it's fine to skip a week"). The client decides whether to send. We never chase
  them into sending.
- Approvals by phone: follow up the same day with an email ("Confirming you approved 2027-02-a v1 on
  the phone today") and log that email.

### Edits

| Kind of edit | What happens |
|---|---|
| Wording, tone, a sentence removed | Make it, rebuild, send v2. It changes only that client's edition. |
| A fact or source they question | Recheck the source. If they're right, fix it for **every** client and tell the others. If the source stands, explain it once with the link; their call after that. |
| A change to the footer, promise or brand | That's a template change: update `clients/<slug>.json` and log a new `TEMPLATE` sign-off. |
| "Can you add our new product / rate?" | No. Alerts stay education-only (see `../COMPLIANCE_NOTE.md`). Offer to mention the feature in a neutral way if it's a security feature, such as card controls in their app. |

Edits after Friday: do them if you can, but the client may need to push the send by a week. Say so
plainly rather than rushing a fact-check.

### Holds and emergency pulls

- **Hold:** the client may skip any week, for any reason, with no charge change. Log it as `held`.
- **Pull after sending:** if an issue turns out wrong after members got it (a source changed, a
  phone number was wrong), tell the client within the hour, give them a one-paragraph correction
  they can send or post, and log it. Fix the cause in the build before the next issue.
- **Breaking scam:** if a scam is hitting their members right now, offer a short extra issue. It goes
  through the same approval; only the timeline is shorter.

## The sign-off log (`approval-log.csv`)

One row per issue per client. Keep every row; never edit one after the fact, add a new row instead.

| Column | Fill with |
|---|---|
| `client_slug` | Matches `clients/<slug>.json`. |
| `issue_id` | From `issues.json`, or `TEMPLATE`. |
| `version` | v1, v2, … |
| `delivered_at` | Date and time the pack was emailed. |
| `reviewer` | Name and title of whoever approved. |
| `decision` | `approved`, `changes`, `held`, `pulled`. |
| `decided_at` | Date and time of their reply. |
| `evidence` | Where the approval lives: "email reply, subject …" or a saved PDF of the email. |
| `member_send_date` | The day it actually went to members (ask the sender if unsure). |
| `notes` | Edits made, questions, member feedback. |

Save each approval email as a PDF in your client folder (outside the repo). If a client or an examiner
ever asks who approved an issue, the log and the saved email answer it.
