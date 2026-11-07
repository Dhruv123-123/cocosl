# Google Sheets + Notion templates: setup and launch

Nine products: three Google Sheets templates and a bundle, three Notion templates and a bundle, plus a free
Notion starter that collects emails. Every folder has the files to upload, three screenshots, store covers and
`LISTING.md` with the copy to paste. Notion folders also have `BUILD.md` and example-data CSVs.

| # | Template | Price | You keep: Gumroad | You keep: Notion Marketplace |
|---|---|---|---|---|
| 1 | Monthly Budget Sheet | $9 | $7.04 | n/a |
| 2 | Debt Payoff Sheet | $12 | $9.65 | n/a |
| 3 | Savings Goals Sheet | $7 | $5.30 | n/a |
| 4 | **Money Sheets Bundle** (1 to 3) | $19 | $15.75 | n/a |
| 5 | Notion Budget Planner | $9 | $7.04 | $7.88 |
| 6 | Notion Debt Payoff Tracker | $12 | $9.65 | $10.64 |
| 7 | Notion Savings Goals Tracker | $7 | $5.30 | $6.04 |
| 8 | **Notion Money HQ** (5 to 7 + weekly check-in) | $19 | $15.75 | $17.08 |
| 9 | **Notion Money Starter** | Free | builds the email list | builds the email list |

Fees checked November 2026: Gumroad direct sales are 10% + $0.50, plus card processing (about 2.9% + $0.30). Sales that come
through Gumroad's Discover marketplace pay a flat 30%. Selling directly on Notion Marketplace costs 8% + $0.40, and Notion
handles sales tax. That needs an approved seller application and Stripe; until then, list on Notion Marketplace with "Sell with"
pointing at Gumroad. Check gumroad.com/pricing and notion.com/help/selling-on-marketplace before launch.

**How the templates sit next to the guides:** these are template-only and cheaper, for people who just want the tool. The
Debt Payoff Sheet uses the same payoff engine as the $17 Debt-Free Date Planner. The planner adds the guide plus the
balance-transfer and consolidation calculators, and the listings say so.

## Order of work (about 2 to 3 hours, once)

1. Make the three Google Sheets copy links (20 minutes).
2. Build the five Notion templates and publish them (5 minutes each with the script, plus finishing touches).
3. Paste every link into `launch/templates/links.json` and rebuild, so the Start Here PDFs carry real links.
4. Create the Gumroad products, then submit the Notion templates to Notion Marketplace.

## 1. Google Sheets: master copies and /copy links

For each `.xlsx` (Monthly Budget, Debt Payoff, Savings Goals):

1. In Google Drive make a folder **MMS template masters**. Upload the `.xlsx` there.
2. Open it with Google Sheets, then **File > Save as Google Sheets**. Delete the uploaded `.xlsx` from Drive; keep the Google Sheet.
3. Check: it opens on **Start**; dropdowns work (Transactions > Category, Deposits > Goal, Payments > Debt); the chart shows on
   Year / Goals / Progress. Rename it, e.g. *Monthly Budget Sheet (Money Made Simple)*.
4. **Share > General access > Anyone with the link > Viewer.** Never give anyone edit access to a master.
5. Copy the link, then replace everything from `/edit` onwards with `/copy`:
   `https://docs.google.com/spreadsheets/d/<long id>/copy`
6. Test it in a private/incognito window: you should see *"Would you like to make a copy of ...?"*
7. Paste it into `links.json` (`sheet_budget`, `sheet_debt`, `sheet_savings`).

If a link ever gets shared publicly, make a new master (repeat 1 to 7), update `links.json` and rebuild. Buyers keep their copies.

## 2. Notion: build, then publish with "Duplicate as template"

Build each template with the script in `BUILD.md` (recommended) or by hand. The script needs a Notion integration token, which you
keep on your own computer: never commit it or paste it into a chat. Build **all five as separate pages**: the three single
templates, the HQ (it builds its own copies of the three inside it) and the free starter. Don't sell links to the HQ's sub-pages.

Without the repo on your computer, use the copy in the `notion-builder/` folder next to this file: `python notion-builder/notion_build.py notion-budget --parent "<link>"` (Python 3.10+, nothing to install).

Then for each one:

1. Do the **finishing touches** in its `BUILD.md`: views, sums, dollar formats. Take your own screenshots now; Notion Marketplace
   wants real ones. The preview images in each folder use the same example data, so yours should look the same.
2. **Share > Publish > Publish.** Turn on **Allow duplicate as template**. Leave editing and comments off. For paid templates,
   turn off search engine indexing.
3. Open the published link in a private window, press **Duplicate**, and check it lands working in a test workspace.
4. Paste the link into `links.json` (`notion_budget`, `notion_debt`, `notion_savings`, `notion_hq`, `notion_starter`).

Anyone with a paid template's link can duplicate it. That's how Notion templates are sold everywhere. The link only lives inside
the Start Here PDF. Notion's own access locking covers templates sold directly through Notion Marketplace.

## 3. Rebuild with the real links

Also fill in `store` (your Gumroad store URL) and `newsletter` (your sign-up page) in `links.json`, then:

```
python launch/templates/build_templates.py
```

The build prints any link still missing. The Start Here PDFs and the free starter's upgrade links now point at the real pages.
Re-run `notion_build.py notion-money-starter` too, or edit its two links by hand.

## 4. Gumroad

For each folder, follow its `LISTING.md`: name, summary, description, tags, price, files (the `.zip` for Sheets templates, the
`Start-Here.pdf` for Notion ones), cover and thumbnail, screenshots.

- **Discount code `STARTER20`:** 20% off, applies to all template products. The free starter prints it.
- **Upsells** (Checkout > Upsells): each single template offers its bundle.
- **Bundle upgrades:** every listing promises "already bought one? reply to your receipt and we'll send a code for the
  difference." When someone asks, make a one-use code worth what they paid.
- **Free starter:** price $0, and turn on *Add buyers to my audience*. Gumroad always asks for an email.

## 5. Notion Marketplace

1. Create your creator profile (notion.com/profile; the help page is notion.com/help/selling-on-marketplace).
2. **Submit a template** for each published page. Use the Marketplace section of its `LISTING.md`.
   - Paid templates: price as listed, **Sell with** your Gumroad product URL. Apply for direct selling (waitlist, Stripe) in
     parallel; approval can take months.
   - Free starter: Free, **Email capture: Require**.
3. Notion reviews each submission and emails you when it's live.

## Email list rules (free starter)

- People sign up for the template **and** the free weekly Money Made Simple email. The listing says so. Send them only that.
- Download the emails from your Notion creator profile (CSV) and your Gumroad audience weekly, and import them into your email
  tool. Never sell or share the list.
- Every email needs a one-click unsubscribe and your mailing address (CAN-SPAM). Honour unsubscribes straight away.

## Rules that keep the store safe

- No made-up reviews, sales counts or "bestseller" badges, and no fake "price ends tonight" timers.
- Screenshots show the template with fictional example data, and say so.
- Every listing and template says it's an educational organising tool, not financial advice.
- Debt-free dates are estimates (monthly interest); the templates and listings say so.

## After launch

- Pin the free starter everywhere: link in bio, a pinned post, the end of each video. It's the top of the funnel.
- Week 2: compare the number of starter downloads against the number of paid sales. If people click but don't buy, test the
  first screenshot and the first line of the description.
- Rebuild after any edit with `python launch/templates/build_templates.py`. It re-checks every workbook and every Notion formula.
