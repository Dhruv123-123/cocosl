// When each page goes live. `node tools/build-pages.mjs --release` (the Netlify build command) drops any
// page dated after the build date: its folder, its sitemap entry, its hub card and nav link. The committed
// files keep every page, so previews and tests see the whole site. Re-deploy weekly (a Netlify build hook
// on a schedule) so new pages appear on their date. research/scouting/pinterest-seo.md, fix 5.
import { pages } from './compare-data.mjs';

export const LAUNCH = '2026-11-16';

export const releases = {
  '': LAUNCH, 'free/': LAUNCH, 'free/thanks/': LAUNCH, 'compare/': LAUNCH, 'about/': LAUNCH, 'q4/': LAUNCH, 'rate-calculator/': LAUNCH, 'how-we-make-money/': LAUNCH,
  ...Object.fromEntries(pages.map((p) => [`compare/${p.slug}/`, p.published])),
  'invoice-template/': '2026-12-07',
  'mileage/': '2026-12-21',
  'deduction-finder/': '2026-12-28',
};

export const released = (path, today) => (releases[path] || LAUNCH) <= today;
