# Money Toolkit (offline bundle)

The free tools from `apps/` as one $9 download that works with no internet: each tool becomes a single HTML
file (CSS, scripts and images inlined) plus an index page, zipped.

- What goes in: `apps/tools/toolkit.mjs` (45 tools). `apps/shared/test/toolkit.test.js` checks the list.
- Build (needs esbuild): `cd apps && npm i --no-save esbuild && node tools/build-toolkit.mjs`
  Output: `launch/money-toolkit/dist/Money-Toolkit/` and `dist/Money-Toolkit.zip` (not committed).
- Listing copy: `LISTING.md` (price shown as [PRICE], suggested $9). Covers: `cover.png`, `thumbnail.png`.
- Rebuild after any tool changes, check a few tools by opening the files directly, then upload the new zip.

Nothing is live: Dhruv creates the Gumroad product, uploads the zip and sets the price.
