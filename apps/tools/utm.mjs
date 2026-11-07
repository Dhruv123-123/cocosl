#!/usr/bin/env node
// UTM helper for every link in bios, pins, posts and newsletters. Conventions: docs/UTM.md.
//
//   node tools/utm.mjs link <url> --source pinterest --medium social --campaign pin-emergency-fund-3
//   node tools/utm.mjs bios [--out file.md]          bio links for every brand and platform
//   node tools/utm.mjs check <files...>              list own-site and store links with no UTM
//   node tools/utm.mjs tag <files...> --source pinterest --medium social [--campaign x] [--write]
//
// `tag` only touches links to the brands' own sites and apps and to Gumroad/Stripe checkout.
// It never changes affiliate links (networks track those themselves, and extra params can
// break them) and never overrides UTM already on a link. Without --write it only prints.
import { readFileSync, writeFileSync } from 'node:fs';
import { basename, dirname, extname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { clean, hostOf, isGumroadLink, isStripeLink, tagLink, utmFrom } from '../shared/track.js';

const HERE = dirname(fileURLToPath(import.meta.url));
export const BRANDS = JSON.parse(readFileSync(join(HERE, 'brands.json'), 'utf8'));
export const MEDIUMS = ['social', 'bio', 'email', 'app', 'referral', 'paid'];
const URL_RE = /https?:\/\/[^\s"'<>(),\]\\]+[^\s"'<>()\]\\.,;:!?]/g;

export function ownHosts(brands = BRANDS.brands) {
  return new Set(brands.flatMap((b) => [b.site, ...(b.apps || [])]).map(hostOf).filter(Boolean));
}

/** Should this link carry UTM? Own sites/apps and checkout links yes; everything else no. */
export function wantsUtm(url, hosts = ownHosts()) {
  return hosts.has(hostOf(url)) || isGumroadLink(url) || isStripeLink(url);
}

export function hasUtm(url) {
  const q = url.split('#')[0].split('?')[1] || '';
  return Boolean(utmFrom(q).source);
}

/** Which dashboard channel a visit or sale belongs to, from its UTM. */
export function channelFor({ source = '', medium = '' } = {}) {
  const s = source.toLowerCase(); const m = medium.toLowerCase();
  if (BRANDS.platforms.includes(s)) return s;
  if (m === 'email' || s === 'newsletter' || s === 'email') return 'email';
  if (m === 'app') return 'apps';
  if (m === 'paid') return 'paid';
  if (s === 'linkpage') return 'link page';
  if (m === 'referral' || s === 'embed') return 'referral';
  return s ? 'other' : 'direct';
}

export function bioLinks(brands = BRANDS.brands, platforms = BRANDS.platforms) {
  return brands.map((b) => ({
    brand: b.name,
    links: platforms.map((p) => ({ platform: p, url: tagLink(b.site + (b.bio_path || '/'), { source: p, medium: 'bio', campaign: 'profile' }) })),
  }));
}

export function findLinks(text) {
  return [...new Set(text.match(URL_RE) || [])];
}

/** Tag the links in a block of text. Returns { text, changed: [[before, after]] }. */
export function tagText(text, utm, hosts = ownHosts()) {
  const changed = [];
  const out = text.replace(URL_RE, (url) => {
    if (!wantsUtm(url, hosts) || hasUtm(url)) return url;
    const next = tagLink(url, utm);
    if (next !== url) changed.push([url, next]);
    return next;
  });
  return { text: out, changed };
}

function args(argv) {
  const opts = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) { const k = a.slice(2); const v = argv[i + 1]; if (!v || v.startsWith('--')) opts[k] = true; else { opts[k] = v; i++; } } else opts._.push(a);
  }
  return opts;
}

function bioMarkdown() {
  const lines = ['# Bio links', '', 'Paste the matching link into each profile. Each one tells Plausible and the owner dashboard which platform the visit came from.', ''];
  for (const b of bioLinks()) {
    lines.push(`## ${b.brand}`, '', '| Platform | Link |', '|---|---|');
    for (const l of b.links) lines.push(`| ${l.platform} | ${l.url} |`);
    lines.push('');
  }
  return lines.join('\n');
}

export function main(argv, log = console.log) {
  const [cmd, ...rest] = argv;
  const o = args(rest);
  if (cmd === 'link') {
    if (!o._[0] || !o.source || !o.medium) throw new Error('usage: link <url> --source x --medium y [--campaign z] [--content w]');
    log(tagLink(o._[0], { source: o.source, medium: o.medium, campaign: o.campaign || '', content: o.content || '' }));
    return 0;
  }
  if (cmd === 'bios') {
    const md = bioMarkdown();
    if (o.out) { writeFileSync(o.out, md + '\n'); log(`Wrote ${o.out}`); } else log(md);
    return 0;
  }
  if (cmd === 'check') {
    let missing = 0;
    for (const f of o._) {
      for (const url of findLinks(readFileSync(f, 'utf8'))) {
        if (wantsUtm(url) && !hasUtm(url)) { missing++; log(`${f}: ${url}`); }
      }
    }
    log(missing ? `${missing} link(s) without UTM` : 'All own-site and checkout links carry UTM.');
    return missing ? 1 : 0;
  }
  if (cmd === 'tag') {
    if (!o.source || !o.medium) throw new Error('usage: tag <files...> --source x --medium y [--campaign z] [--write]');
    if (!MEDIUMS.includes(o.medium)) log(`warning: medium "${o.medium}" isn't one of ${MEDIUMS.join(', ')}`);
    let total = 0;
    for (const f of o._) {
      const campaign = o.campaign || clean(basename(f, extname(f))).toLowerCase();
      const { text, changed } = tagText(readFileSync(f, 'utf8'), { source: o.source, medium: o.medium, campaign, content: o.content || '' });
      for (const [a, b] of changed) log(`${f}: ${a}\n  -> ${b}`);
      total += changed.length;
      if (o.write && changed.length) writeFileSync(f, text);
    }
    log(`${total} link(s) ${o.write ? 'tagged' : 'would be tagged (add --write to save)'}`);
    return 0;
  }
  log('commands: link, bios, check, tag (see the top of tools/utm.mjs)');
  return cmd ? 1 : 0;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try { process.exitCode = main(process.argv.slice(2)); } catch (e) { console.error(e.message); process.exitCode = 2; }
}
