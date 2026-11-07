import { test } from 'node:test';
import assert from 'node:assert/strict';
import { buildScript, lintText, scriptToText, overlay, FORMATS, LENGTHS } from '../lib/scripts.js';

const candle = {
  brand: 'Hollowick', product: 'Cedar & Smoke candle', niche: 'candles', price: '28',
  facts: ['wooden wick that crackles', 'hand-poured soy wax', '8 oz amber jar'], audience: 'candle lovers', cta: 'Link below',
  format: 'sensory', length: 20, presenter: 'ai-voice',
};

test('every format and length builds a script whose timings cover the whole ad', () => {
  for (const format of Object.keys(FORMATS)) {
    for (const length of LENGTHS) {
      const s = buildScript({ ...candle, format, length, problem: 'tunnelling candles', alternative: 'paraffin candles' });
      assert.equal(s.rows[0].time.split('–')[0], '0', format);
      assert.equal(s.rows.at(-1).time, `${s.rows.at(-1).time.split('–')[0]}–${length}s`, `${format} ${length}`);
      for (let i = 1; i < s.rows.length; i++) {
        const prevEnd = s.rows[i - 1].time.split('–')[1].replace('s', '');
        assert.equal(s.rows[i].time.split('–')[0], prevEnd, `${format} ${length} row ${i}`);
        const [a, b] = s.rows[i].time.replace('s', '').split('–').map(Number);
        assert.ok(b - a >= 2, `${format} ${length}: beat ${i} is only ${b - a}s`);
      }
      assert.equal(s.hooks.length, 3);
      assert.ok(s.rows.every((r) => r.visual && r.voice && r.text), format);
      assert.ok(!/undefined|null/.test(scriptToText(s)), `${format} ${length} has a hole`);
    }
  }
});

test('uses only the facts given and ends on brand, price and the CTA', () => {
  const s = buildScript(candle);
  const voice = s.rows.map((r) => r.voice).join(' ');
  for (const f of candle.facts) assert.match(voice.toLowerCase(), new RegExp(f.toLowerCase()));
  assert.equal(s.rows.at(-1).voice, 'Hollowick. Link below.');
  assert.equal(s.rows.at(-1).text, 'Hollowick · $28');
  assert.equal(s.label, 'AI-generated voice · Ad');
  assert.match(s.caption, /^Cedar & Smoke candle from Hollowick\. Wooden wick that crackles\. \$28\. Link below\.$/);
});

test('founder format always uses the real founder, never an AI presenter', () => {
  const s = buildScript({ ...candle, format: 'founder', presenter: 'ai-presenter' });
  assert.equal(s.presenter, 'Founder (real person)');
  assert.equal(s.label, 'Ad');
  assert.ok(s.notes.some((n) => /real founder/.test(n)));
});

test('a 15-second ad stays short', () => {
  const s = buildScript({ ...candle, format: 'three-things', length: 15 });
  assert.ok(s.rows.length <= 4, String(s.rows.length));
});

test('needs a brand, a product and two facts', () => {
  assert.throws(() => buildScript({ ...candle, brand: ' ' }), /brand/);
  assert.throws(() => buildScript({ ...candle, product: '' }), /product/);
  assert.throws(() => buildScript({ ...candle, facts: ['only one', ' '] }), /two true facts/);
});

test('lint catches testimonials, health claims, ratings, guarantees and income claims', () => {
  const ids = (t) => lintText(t).map((x) => x.phrase.toLowerCase());
  assert.deepEqual(ids('I love this candle'), ['i love']);
  assert.ok(ids('cures eczema overnight').includes('cures'));
  assert.ok(ids('rated 5 stars by customers').includes('5 stars'));
  assert.ok(ids('guaranteed to last').includes('guaranteed'));
  assert.ok(ids('the #1 candle').includes('#1'));
  assert.ok(ids('earn $500 a week').length);
  assert.deepEqual(lintText('hand-poured soy wax in an 8 oz amber jar'), []);
  const s = buildScript({ ...candle, facts: ['best candle ever', 'I love the smell'] });
  assert.equal(s.lint.length, 2);
});

test('on-screen text is cut at a word, not mid-word', () => {
  assert.equal(overlay('hand-poured soy wax'), 'Hand-poured soy wax');
  const long = overlay('a wooden wick that crackles softly while it burns all evening');
  assert.ok(long.length <= 29 && long.endsWith('…') && !/\s…$/.test(long), long);
});
