// Copy apps/shared/*.js into each app's lib/ folder. Each app can deploy as its own Netlify
// site (base = the app folder), so shared code has to live inside every app.
// Run after editing anything in shared/; test/shared.test.js fails if a copy is stale.
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
export const APPS = ['scam-checker', 'money-calculators', 'ad-script-builder', 'budget'];
const HEADER = '// GENERATED from apps/shared/ by tools/sync-shared.mjs. Edit the shared copy, not this one.\n';

export function expected(file) {
  return HEADER + readFileSync(join(ROOT, 'shared', file), 'utf8');
}

export function sharedFiles() {
  return readdirSync(join(ROOT, 'shared')).filter((f) => f.endsWith('.js'));
}

if (import.meta.url === `file://${process.argv[1]}`) {
  for (const app of APPS) for (const f of sharedFiles()) writeFileSync(join(ROOT, app, 'lib', f), expected(f));
  console.log(`Synced ${sharedFiles().join(', ')} into ${APPS.join(', ')}`);
}
