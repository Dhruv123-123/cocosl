// Ready-made money calendar files, one per brand, to attach to a welcome email or a lead-magnet page.
// Same dates as budget/money-calendar.html. The 12-month window starts on the day you run it.
// Run from apps/: node tools/build-money-calendars.mjs [out-dir]   (default: /mnt/project-files/content-factory/lead-magnets/money-calendar)
import { writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { BRANDS, calendarFile } from '../budget/lib/moneycal.js';

const out = process.argv[2] || '/mnt/project-files/content-factory/lead-magnets/money-calendar';
mkdirSync(out, { recursive: true });
const d = new Date();
const from = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
const FILES = { mms: 'money-made-simple-money-calendar.ics', 1099: '1099-money-tax-calendar.ics', scam: 'scam-shield-scam-season-calendar.ics', es: 'dinero-simple-calendario-de-dinero.ics' };
for (const [key, file] of Object.entries(FILES)) {
  const { events, ics } = calendarFile(key, { from });
  writeFileSync(join(out, file), ics);
  console.log(`${file}: ${events.length} dates for ${BRANDS[key].name}`);
}
