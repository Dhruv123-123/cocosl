# Instagram, Facebook and Pinterest APIs: what's allowed for our own accounts

Researched 2026-11-07 from Meta's and Pinterest's developer docs (linked). **Docs only. No app has been
created and nothing has been submitted.** This follows `api-applications.md`, which found that TikTok
rules out tools that post to accounts "you or your team manages".

## TL;DR

1. **Meta (Instagram and Facebook): there's no TikTok-style problem. Posting to our own accounts is the
   intended use of Standard Access.** Meta approves Standard Access automatically, with no App Review and
   no Business Verification. It works for "app users who have a role on the requesting app"
   ([Meta access levels](https://developers.facebook.com/docs/graph-api/overview/access-levels)). Dhruv
   adds himself, and anyone else who posts, as a role on the app, and the factory posts to accounts those
   people manage.
2. **Pinterest: allowed for our own accounts, but with three catches.**
   - **Trial access is a sandbox:** "all Pins and Boards created with Trial access are only visible to
     their creator as Sandbox entities." Real pins need **Standard access**, which takes a recorded demo
     of the OAuth flow. Pinterest asks for it even when "you are the only intended user"
     ([Pinterest access tiers](https://developers.pinterest.com/docs/key-concepts/access-tiers/)).
   - **Each pin has to be chosen by a person:** "if your app allows end users to schedule Pin
     publishing, the end user must choose each Pin to be published." The factory's `review` / `approve`
     step does exactly that, as long as pins are approved one at a time, never in bulk
     ([Pinterest Developer Guidelines](https://policy.pinterest.com/en/developer-guidelines)).
   - **No storing data from the API:** "you may not store any information accessed through any Pinterest
     Materials including the API... call the API each time you need to access information." The factory's
     `metrics` / `insights` store numbers in its database. That's fine for other platforms, but a future
     Pinterest publisher must not save pin analytics.
3. **Rate limits are far above our volume on every platform:**
   - **Instagram:** 100 API posts a day per account.
   - **Facebook:** 30 Reels a day per Page.
   - **Pinterest Standard:** 100 write calls a minute.

   Our cap is 2 posts a day per platform.
4. **The factory already has Instagram and Facebook publishers** (`publish/instagram.py`, `publish/facebook.py`)
   that match these docs. **There's no Pinterest publisher yet.** Until there is one, pins go through
   Pinterest's own scheduler, or Postiz if its Pinterest provider is enabled (`pinterest-seo.md`).

## 1. Instagram (Graph API content publishing)

| Item | What the docs say | Source |
|---|---|---|
| **Account** | An Instagram **professional** account (Creator or Business) | [Content publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing) |
| **Login options** | **Instagram Login** (Business Login for Instagram): `instagram_business_basic`, `instagram_business_content_publish`. No Facebook Page needed. **Facebook Login for Business**: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`, with the Instagram account linked to a Facebook Page. Add `ads_management` and `ads_read` only if the Page role came through Business Manager | same |
| **Access level** | Standard Access, approved automatically, for people with a role on the app. App Review and Business Verification are needed only for Advanced Access (other people's accounts) | [Access levels](https://developers.facebook.com/docs/graph-api/overview/access-levels) |
| **Rate limit** | **100 API-published posts per rolling 24 hours** (a carousel counts as 1). Check usage with `GET /<IG_ID>/content_publishing_limit`. One section of the same page still says 50; plan for 50 to be safe | same |
| **Media** | Images: **JPEG only**. Reels: `media_type=REELS`. Stories: `media_type=STORIES`. Carousels: **up to 20** items, all cropped to the first item's ratio (1:1 by default). Media must be on a **public HTTPS URL** when the container is created | same |
| **Not supported** | Shopping tags, filters. `alt_text` works on images only, not Reels or Stories | same |
| **Supported extras** | **Trial Reels** (`trial_params`, `MANUAL` or `SS_PERFORMANCE`); **AI label** `is_ai_generated=true`, set on the carousel container only, because setting it on child items errors | same |
| **Page Publishing Authorization** | If the linked Facebook Page requires PPA, publishing fails until it's done. Do it in advance | same |

**Against the factory:** `publish/instagram.py` already uses these endpoints, `is_ai_generated` and
`trial_params`, and says that posting to your own accounts works with the account added as an app role.
Two small differences, neither urgent:
- Its notes say carousels have at most 10 children, but the limit is now 20.
- The 50-versus-100 daily limit line on Meta's page is inconsistent. At 2 a day it doesn't matter.

## 2. Facebook Pages (Reels and posts)

| Item | What the docs say | Source |
|---|---|---|
| **Permissions** | Facebook Login with `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, a **Page access token**, and the **CREATE_CONTENT** task on the Page | [Reels publishing](https://developers.facebook.com/docs/video-api/guides/reels-publishing) |
| **Rate limit** | **30 API-published Reels per Page per rolling 24 hours** | same |
| **Reel specs** | .mp4, 9:16, 1080×1920 recommended (minimum 540×960), 24-60 fps, **3-90 seconds** (60 s maximum if published as a Page story), AAC stereo 48 kHz ≥128 kbps | same |
| **Steps** | `POST /{page-id}/video_reels` with `upload_phase=start` → upload to `rupload.facebook.com` → `upload_phase=finish` and `video_state=PUBLISHED` | same |
| **Restrictions** | Page posts are always public. A hosted file is refused if the host's `robots.txt` blocks `facebookexternalhit`. Files on Meta's own CDN (fbcdn) are refused | same |

**Against the factory:** `publish/facebook.py` implements this same start, upload and finish flow.
- Our 30-55 second shorts and 65-90 second TikTok cuts both fit the 90 second limit.
- The 6-10 minute long videos go up as Page videos (`/videos`), not as Reels.
- **Check before launch:** the site or `PUBLIC_MEDIA_BASE_URL` host must not block `facebookexternalhit`
  in `robots.txt`.

## 3. Pinterest (API v5)

| Item | What the docs say | Source |
|---|---|---|
| **Getting access** | Register an app with the account that will run it (a business account); the app name can't contain "Pinterest". Pinterest reviews it and emails approval → **Trial access** | [Set up your app](https://developers.pinterest.com/docs/getting-started/set-up-app/) |
| **Trial access** | For exploring the API. **Pins and boards are sandbox entities, visible only to their creator.** Limits are counted per day per app: 1,000 requests a day in total; `org_write` (create pins and boards) 300 a day | [Access tiers](https://developers.pinterest.com/docs/key-concepts/access-tiers/), [Rate limits](https://developers.pinterest.com/docs/reference/rate-limits/) |
| **Standard access** | Normal, public pins. Upgrade from the app card: **My apps → Upgrade**, upload a **video of the OAuth flow**, submit. Required "if you are the only intended user". Authentication must use OAuth tokens. Collecting logins or cookies gets the app refused. Limits are per minute per user per app: `org_write` 100, `org_read` 1,000, `org_analytics` 60, 100 requests a second overall | same |
| **Scheduling** | "The end user must choose each Pin to be published." No features that "automatically initiate actions without specifically considering each action" | [Developer Guidelines](https://policy.pinterest.com/en/developer-guidelines) |
| **Data** | "You may not store any information accessed through... the API." Call the API each time instead. No using Pinterest data to train AI | same |
| **Accounts** | "Do not use someone else's API credentials, and do not allow anyone else to use yours." Don't reconnect "the same or a substantially similar app using a different account or under a different name" | same |
| **New-app note** | Apps registered on or after 14 Sep 2026 may get `403 PINNER_DATA_ACCESS_DENIED` when reading boards or pins of non-business users. Not a problem for our own business accounts | [Access tiers](https://developers.pinterest.com/docs/key-concepts/access-tiers/) |

### What this means for a Pinterest publisher (not built)

- **One app for all four brand accounts,** and Dhruv connects each one through OAuth. Never share the app's
  credentials with another tool.
- **Every pin goes through `factory review` → `factory approve <id>` one at a time.** No bulk approval for
  Pinterest, and nothing that turns a blog post into pins and posts them without that step.
- **Don't save Pinterest analytics.** Read them live when the dashboard asks, and show them without writing
  them to the database. Clicks to the site can still be measured our own way (UTM tags and Plausible),
  because that's our data, not Pinterest's.
- **The demo video for Standard access** (about 1 minute): start the factory's Pinterest connect command,
  show Pinterest's OAuth consent page with the app name, approve, and show that the token was received (value
  hidden). Then create one pin with `factory approve`, and open it on the brand's Pinterest profile. Upload
  it at **My apps → Upgrade**.

## 4. Setup steps

### Meta (one app for Instagram and Facebook, about 30 minutes)

1. **developers.facebook.com → My Apps → Create app**, type **Business**. Name it after the tool, for example
   `cocosl publisher`. Don't use Meta's brand names.
2. **App roles → Roles:** add Dhruv (and anyone else who will post) as **Admin** or **Developer**. Standard
   Access only works for people with a role.
3. Each brand's **Instagram account → Settings → Account type → Professional (Creator).** Link it to the
   brand's **Facebook Page** (Meta Business Suite → Settings → Accounts).
4. Do **Page Publishing Authorization** on each Page now if Meta asks for it (Page settings → Page
   Publishing Authorization). Otherwise it can block posting later.
5. Add products **Instagram** (API setup with Facebook Login for Business) and **Facebook Login for
   Business**. Request only the permissions in the tables above, plus `instagram_manage_insights` for
   metrics.
6. Run `factory auth meta --brand <slug>` once per brand. It covers Facebook and Instagram, and saves
   `FB_PAGE_ID`, `FB_PAGE_TOKEN` and the Instagram IDs under that brand's name.
7. Set `PUBLIC_MEDIA_BASE_URL` to a public HTTPS host that serves the rendered files and doesn't block
   `facebookexternalhit`.
8. **Test** with one carousel and one Reel per brand, and check them in the app. Then look at
   `content_publishing_limit` once to confirm the limit the account actually has.
9. Leave the app in its current mode. **Don't request Advanced Access or start Business Verification.**
   Neither is needed for our own accounts.


### Pinterest (about 20 minutes, plus waiting for review)

1. Make sure each brand's Pinterest account is a **business account** and its domain is claimed
   (`pinterest-seo.md`).
2. **developers.pinterest.com → My apps → Connect app.** Use Dhruv's main brand account, and name it
   without "Pinterest". Add the redirect URI exactly as the publisher will send it.
3. Wait for Trial approval (Pinterest emails you).
4. Build the publisher (not done; see above), connect one brand, and record the demo video.
5. **My apps → Upgrade → upload the video → submit.** Until Standard is approved, pins created through the
   API stay in the sandbox, so keep using Pinterest's own scheduler for real pins.

## Flags, in order of importance

1. **Pinterest: one human choice per pin, and no stored API data.** Both are written into the developer
   guidelines, and the second runs against how the factory stores metrics for other platforms. Build the
   Pinterest publisher with both in mind from the start.
2. **Pinterest Trial access isn't real posting.** Don't mistake sandbox pins for live ones while testing.
3. **Meta: only people with a role on the app.** If a freelancer or a second person ever posts for a brand,
   add them as an app role. Don't share Dhruv's token. Anything beyond role users needs App Review and
   Business Verification.
4. **Meta's own spam and originality rules still apply.** The API doesn't change them: original content only,
   and the 2-a-day cadence cap (`tiktok-instagram-monetization.md`, `launch-playbook.md`).

## Open question for Dhruv

- Should the factory get a Pinterest publisher that follows these rules (one approval per pin, live
  analytics only)? Otherwise pins stay in Pinterest's own scheduler, about 1-3 a day per brand.
