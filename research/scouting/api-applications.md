# TikTok and YouTube API access: what to apply for, and the drafts

Researched 2026-11-07 from TikTok's and Google's own developer pages (linked). **Docs only. Nothing has been
submitted.** Dhruv submits anything here himself.

## TL;DR: the two answers turned out different from what we expected

1. **TikTok: don't submit an audit for the factory. It would be refused, and it should be.** TikTok's
   Content Sharing Guidelines name our exact use as unacceptable: "A utility tool to help upload contents
   to the account(s) you or your team manages." They also say apps "must not be limited to test
   applications and should be intended for a wide audience, not limited to internal groups/private use"
   ([TikTok for Developers](https://developers.tiktok.com/doc/content-sharing-guidelines)). Describing the
   factory as anything else to get through would be misleading, and it would risk the developer account.
   **Post TikToks by hand or with TikTok's own scheduler instead** (section 1).
2. **YouTube: no audit is needed any more.** On **2 Nov 2026** YouTube reversed the 2020 rule. Uploads from
   unverified API projects "are no longer restricted to private viewing mode"
   ([YouTube Data API revision history](https://developers.google.com/youtube/v3/revision_history)). Uploads
   use their own quota bucket of about 100 a day, which is far more than we need
   ([videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert)).
3. **Google OAuth verification isn't needed either.** Google exempts apps "for your personal use (fewer
   than 100 users)" ([Google Cloud help](https://support.google.com/cloud/answer/13464323)). Publish the
   consent screen to **In production** without submitting it, so the refresh token stops expiring every
   7 days. That 7-day expiry only applies to apps left in "Testing"
   ([Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)). Dhruv clicks past one
   "Google hasn't verified this app" screen the first time.
4. **Still worth having:** a privacy policy section covering the API data, and a short terms page. Both
   are drafted below. Google requires both if we ever do submit for verification, and they cost nothing.
   The verification drafts (use case, scope justification, demo video script) are in section 3 in case
   Google ever asks.

`launch-playbook.md` said to apply for both audits in week 1. That's corrected in this round.

## 1. TikTok

### What TikTok requires, and why we don't fit

| TikTok rule | Our factory |
|---|---|
| Intended use: "facilitate authentic creators to post original content" | ✓ Original content |
| Unacceptable: "A utility tool to help upload contents to the account(s) you or your team manages" | ✗ That's exactly what it is |
| "intended for a wide audience, not limited to internal groups/private use" | ✗ Four brand accounts, one operator |
| Unaudited apps: posts are private, at most 5 posting users a day, and the account must be private when posting | Makes unaudited posting useless for a public brand account |
| "Only start sending content materials to TikTok after the user has expressly consent[ed] to the upload" | A scheduler that posts on its own doesn't meet this |
| Each post needs the creator info screen, a privacy level the user picks (no default), interaction toggles off by default, a commercial-content toggle, and "By posting, you agree to TikTok's Music Usage Confirmation." | Our CLI has none of that UI |

### What to do instead (in order of preference)

1. **Post in the TikTok app or on TikTok's website.** The factory already renders the 9:16 file and writes the
   caption. Dhruv copies the caption, uploads the file, picks the settings and posts. About 2 minutes a
   video. It also keeps a human in the loop, which `tiktok-instagram-monetization.md` recommends anyway.
2. **Schedule in TikTok's own web uploader** (TikTok Studio on desktop has a schedule option). Batch a
   week's posts in one sitting. *How far ahead it allows wasn't confirmed this round: TikTok's help page
   couldn't be fetched.*
3. **A third-party scheduler that's already approved.** Buffer's free plan has 3 channels and 10 queued
   posts per channel, and lists TikTok. But its page shows automatic TikTok publishing for **business
   profiles**, and our TikTok accounts must stay **personal** to qualify for Creator Rewards. On a personal
   account, expect a phone reminder to finish the post yourself
   ([Buffer pricing](https://buffer.com/pricing)). Check this before relying on it.

**What changes in the factory:** nothing has to. `publish/tiktok.py` already defaults to `SELF_ONLY` and
explains the audit. Leave TikTok out of the automatic publish targets. Have the factory put each TikTok cut
plus its caption in the render folder for Dhruv to post. *Suggested follow-up for the code: a
`factory tiktok-pack <date>` command that zips a day's TikTok files and captions. Not built.*

### If we ever build something that does qualify

TikTok would review a **public tool other creators use to post their own original videos**. For example, the
"AI Ad Studio" idea from earlier rounds, if clients connected their own TikTok accounts to post videos they
had approved. That needs the whole posting screen above, a public website, and real outside users. The
application would describe that product, not the factory. Draft it only once the product exists.

## 2. YouTube: set it up as a personal-use app (no submission)

### Checklist for Dhruv (about 20 minutes, once per Google account that owns brand channels)

1. **Google Cloud Console** → new project, named after the tool, not after YouTube, e.g. `cocosl-publisher`.
   Google's branding rules don't allow "YouTube" in an app name.
2. **APIs & Services → Library →** enable **YouTube Data API v3**.
3. **Google Auth Platform (OAuth consent screen) → Branding:**
   - App name `cocosl publisher` and a support email.
   - Home page `https://<brand domain>/`, privacy policy `https://<brand domain>/privacy/`, terms
     `https://<brand domain>/terms/`. Optional for personal use, but fill them in.
4. **Audience:** User type **External**. Add your own Google account as a test user.
5. **Data access → Add scopes:** exactly the three the factory requests (`publish/oauth.py`,
   `YOUTUBE_SCOPES`). Nothing broader:
   - `https://www.googleapis.com/auth/youtube.upload`
   - `https://www.googleapis.com/auth/youtube.readonly`
   - `https://www.googleapis.com/auth/youtube.force-ssl`, used to reply to comments from the factory's
     inbox and to upload captions.
6. **Clients → Create client → Desktop app.** Copy the client ID and secret into `.env` as `YT_CLIENT_ID` and
   `YT_CLIENT_SECRET`. Never commit them.
7. **Audience → Publish app → In production.** Google will offer verification. **Don't submit.** Personal use
   under 100 users is exempt, and production status stops the 7-day token expiry.
8. Run `factory auth youtube --brand <brand-slug>`, which saves the token under that brand's own name in `.env`. On the "Google hasn't verified this app" screen, choose **Advanced → Go to
   cocosl publisher (unsafe)**. That's expected for your own unverified app. Then pick the **brand channel**,
   not your personal one, and allow all three scopes. Save `YT_REFRESH_TOKEN` to `.env`.
9. Repeat step 8 once per brand channel, with that brand's `--brand`. Each token is tied to the channel picked at consent.
10. **Test:** run one upload with `YT_PRIVACY=private`, check it in Studio, then make it public by hand.
    Keep `YT_PRIVACY=private` as the default for the first two weeks (`launch-playbook.md`).

**Rules to keep while using it** ([YouTube API Developer Policies guide](https://developers.google.com/youtube/terms/developer-policies-guide)):
- Follow the [YouTube API Services Terms](https://developers.google.com/youtube/terms/api-services-terms-of-service).
- Never help break [YouTube's Terms](https://www.youtube.com/t/terms).
- If anyone ever asks for their data to be deleted, do it within 30 days.
- If a use is ever unclear, the guide says to apply for an API Compliance Audit through the
  [audit form](https://support.google.com/youtube/contact/yt_api_form), with "a clear summary that mentions
  any end users". The same form is used for quota increases. Neither applies today.

## 3. Drafts kept on file (only if Google asks, or if users ever pass 100)

### Use case (Google OAuth verification form, "How will the scopes be used?")

> cocosl publisher is a command-line tool used by one small publisher to upload videos it has produced to
> its own YouTube channels and to read those videos' performance. The operator writes and reviews each video,
> then runs the tool, which uploads the file with its title, description, tags and AI-disclosure setting,
> by default as private, so a person checks it in YouTube Studio before it's published. The tool also reads
> view and retention numbers for the operator's own videos to decide what to make next, and lets the
> operator read and reply to comments on those videos. It doesn't access
> any other user's data, has no public sign-up, and stores tokens only on the operator's machine.

### Scope justification

| Scope | Why it's needed | Why a narrower scope won't work |
|---|---|---|
| `youtube.upload` | Upload our own produced videos with `videos.insert` and set custom thumbnails with `thumbnails.set` | It's already the narrowest scope that can upload. It can't read, edit or delete existing videos |
| `youtube.readonly` | Read our own videos' statistics (views, likes, duration) with `videos.list` and `channels.list`, to report what performed, and the comments on our own videos so we can reply | Read-only. `youtube.upload` can't read statistics or comments, and there's no narrower read scope for the channel's own videos |
| `youtube.force-ssl` | Reply to comments on our own videos (`comments.insert`) and upload our own SRT captions (`captions.insert`), which both require this scope | The Data API offers no narrower scope for posting comment replies or caption tracks |

### Demo video script (2-3 minutes, screen recording, consent screen in English)

1. **0:00** Title card: "cocosl publisher: uploading our own videos to our own YouTube channel." Show the
   brand's website home page, then its privacy policy URL.
2. **0:15** Terminal: `factory auth youtube`. The browser opens Google's consent screen. Show the
   **full URL bar** (it contains the client ID) and the app name, which must match the consent screen.
3. **0:35** Scroll the consent screen so **every scope requested is visible**. Pick the brand channel and
   allow.
4. **0:55** Terminal: upload one finished video with `YT_PRIVACY=private`. Show the command output with
   the new video ID. That's the `youtube.upload` scope in use.
5. **1:25** YouTube Studio: the video appears as Private, with its title, description and the
   altered-content setting. Make it public by hand.
6. **1:50** Terminal: `factory metrics` reads that video's statistics, which is the `youtube.readonly`
   scope. Then reply to one comment on our own video from the factory's inbox, which is the
   `youtube.force-ssl` scope.
7. **2:15** Show where the token is stored (the local `.env`, value hidden). Then revoke access at
   myaccount.google.com/permissions to show the user can cut access off.
8. Upload the recording to YouTube as **Unlisted** and paste the link into the verification form.

### Submission checklist (only if verification is ever needed)

1. The brand domain is verified in **Google Search Console** by a project owner.
2. The home page on that domain describes the tool, isn't just a login page, and links to the privacy policy.
3. The privacy policy (below) is live on the same domain. Its URL is identical on the home page and the
   consent screen.
4. The consent screen lists only the scopes in the table above.
5. The demo video is recorded as scripted and uploaded unlisted.
6. **Google Auth Platform → Verification Center → Submit.** Paste the use case and the scope
   justifications. Reply to Google's emails from the project's contact address. Google says missed
   notices can cost API access.

## 4. Privacy policy section (add to each brand's existing `/privacy/` page)

Each site already has a privacy page covering Plausible analytics and email sign-ups. Add this section
instead of making a second policy. Replace `<Brand>` and `<contact email>`.

> ### Videos we publish with YouTube's and other platforms' tools
>
> <Brand> uses its own software to publish our videos to our own accounts on YouTube and other video
> platforms. When we connect our own YouTube channel, we use YouTube API Services, and Google's
> [Privacy Policy](https://policies.google.com/privacy) applies to that connection. By watching our
> videos on YouTube you're also subject to the [YouTube Terms of Service](https://www.youtube.com/t/terms).
>
> **What this software accesses:** only our own channels. It uploads our videos, reads the numbers about them
> (views, likes, watch time), and reads comments left on our own videos so we can reply. A comment's
> author name and text are kept only as long as we need them to reply. We don't collect anything else about
> viewers, and we never access other channels' data.
>
> **Where it's stored:** access tokens for our own accounts are kept on our own computer, not shared with
> anyone, and not sold. Video statistics are kept in a local database to plan future videos.
>
> **Revoking access:** the account owner can revoke this software's access at any time at
> [Google's security settings page](https://myaccount.google.com/permissions).
>
> **Deletion:** if you believe we hold data about you from these platforms, email <contact email>. We'll
> delete it within 30 days.

Spanish version for Dinero Simple: have a native speaker translate it, keep the same links, and keep it
in the page's "Privacidad" section.

## 5. Terms page draft (`/terms/`, one per brand site)

> # Terms of use
>
> *Last updated: <date>*
>
> **Who we are.** <Brand> publishes free articles, videos, calculators and email newsletters about personal
> money topics, and sells a small number of digital guides and templates.
>
> **Not financial, tax or legal advice.** Everything we publish is general education. It isn't advice for
> your situation. Check numbers, deadlines and rules with the official source (we link it) or a licensed
> professional before acting on them.
>
> **How we make content.** We use AI tools to help draft, illustrate and narrate some content. A person
> chooses every topic and reviews what we publish. We label AI-made media where platforms ask us to.
>
> **Links and affiliates.** Some links are affiliate links, and we may earn a commission at no cost to you.
> They're marked. We aren't responsible for other sites' content or offers.
>
> **Purchases.** Digital products are sold and delivered through Gumroad, whose terms also apply. Each
> product page states its refund window.
>
> **Email.** You can unsubscribe from any email with one click. See our [privacy policy](/privacy/) for
> what we collect and why.
>
> **Your use of our material.** You may use our free downloads for yourself and share links to our pages.
> Please don't resell or republish our guides, templates or videos.
>
> **Platforms.** Our videos also appear on YouTube, TikTok, Instagram, Facebook and Pinterest. Your use of
> those platforms is governed by their own terms, including the
> [YouTube Terms of Service](https://www.youtube.com/t/terms).
>
> **Changes and contact.** We may update these terms and will change the date above when we do. Questions:
> <contact email>.

*Not legal advice. Before the products earn real money, have someone qualified read the terms and the
privacy page once.*

## Open questions for Dhruv

1. OK to post TikToks by hand (or with TikTok's scheduler) rather than through the API? Two minutes a
   video, about 5-7 a week per brand once launched.
2. Should the factory get a small `tiktok-pack` command that bundles each day's TikTok files and captions
   for posting by hand?
