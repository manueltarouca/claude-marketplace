#!/usr/bin/env node
/**
 * Check a built HTML5 game against CrazyGames' *documented* limits.
 *
 *   node check-build.mjs <dist-dir> [--json]
 *
 * The point of this script is to separate the mechanically checkable from the
 * human judgements. Bundle size, file count, absolute paths and which SDK
 * version you shipped are facts a script can settle in a second. Legibility,
 * ad placement and originality are not, and a tool that quietly implies "no
 * findings = ready to submit" does more harm than good — so those are printed
 * as an explicit not-checked list rather than omitted.
 *
 * Every threshold here is traceable to a docs page, cited inline. If a number
 * has no citation it does not belong in this file.
 */
import { readdirSync, readFileSync, statSync, existsSync } from 'node:fs';
import { join, extname, relative } from 'node:path';

const args = process.argv.slice(2);
const asJson = args.includes('--json');
const dir = args.find((a) => !a.startsWith('--'));

if (!dir || !existsSync(dir)) {
  console.error('usage: check-build.mjs <dist-dir> [--json]');
  process.exit(2);
}

/** Documented limits — `/requirements/technical/`. */
const LIMIT = {
  totalBytes: 250 * 1024 * 1024,
  files: 1500,
  initialBytes: 50 * 1024 * 1024,
  initialBytesMobileHomepage: 20 * 1024 * 1024,
};

const findings = [];
const pass = [];
const fail = (level, text, detail) => findings.push({ level, text, detail });

// ------------------------------------------------------------------ walk

function walk(root) {
  const out = [];
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const full = join(root, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else out.push({ path: full, rel: relative(dir, full), size: statSync(full).size });
  }
  return out;
}

const files = walk(dir);
const totalBytes = files.reduce((n, f) => n + f.size, 0);
const mb = (n) => (n / 1024 / 1024).toFixed(2) + ' MB';

if (totalBytes > LIMIT.totalBytes) fail('error', `Total bundle ${mb(totalBytes)} exceeds the 250 MB limit`);
else pass.push(`Total bundle ${mb(totalBytes)} / 250 MB`);

if (files.length > LIMIT.files) fail('error', `${files.length} files exceeds the 1500 file limit`);
else pass.push(`${files.length} files / 1500`);

// --------------------------------------------------- entry and initial load

const entry = files.find((f) => f.rel === 'index.html')
  ?? files.find((f) => f.rel.endsWith('index.html'));

if (!entry) {
  fail('error', 'No index.html found — the portal loads the game from one');
}

const html = entry ? readFileSync(entry.path, 'utf8') : '';

/**
 * Estimate the initial download: the entry document plus everything it
 * references directly.
 *
 * This is an approximation and is reported as one. The docs measure from the
 * start of loading to the first `gameplayStart()` event, which depends on
 * runtime behaviour a static scan cannot see — a game that lazy-loads a 40 MB
 * level pack after firing the event will measure far smaller than this, and one
 * that never fires the event will measure the whole bundle.
 */
const referenced = new Set();
for (const m of html.matchAll(/(?:src|href)\s*=\s*["']([^"']+)["']/g)) referenced.add(m[1]);
let initialBytes = entry ? entry.size : 0;
for (const ref of referenced) {
  if (/^(https?:)?\/\//.test(ref) || ref.startsWith('data:')) continue;
  const clean = ref.replace(/^\.?\//, '').split('?')[0];
  const f = files.find((x) => x.rel === clean || x.rel.endsWith('/' + clean));
  if (f) initialBytes += f.size;
}

if (initialBytes > LIMIT.initialBytes) {
  fail('error', `Estimated initial download ${mb(initialBytes)} exceeds the 50 MB limit`);
} else if (initialBytes > LIMIT.initialBytesMobileHomepage) {
  fail('warn', `Estimated initial download ${mb(initialBytes)} is over 20 MB — under the 50 MB limit, but not eligible for the mobile homepage`);
} else {
  pass.push(`Estimated initial download ${mb(initialBytes)} / 50 MB (and under the 20 MB mobile-homepage figure)`);
}

// ------------------------------------------------------------ absolute paths

// `/requirements/technical/`: relative paths only; absolute paths fail to load.
const absolute = [];
for (const f of files) {
  if (!['.html', '.css', '.js', '.json'].includes(extname(f.rel))) continue;
  const text = readFileSync(f.path, 'utf8');
  for (const m of text.matchAll(/(?:src|href)\s*=\s*["'](\/[^"'/][^"']*)["']/g)) {
    absolute.push(`${f.rel}: ${m[1]}`);
  }
}
if (absolute.length) fail('error', `${absolute.length} absolute path(s) — these fail to load in the portal`, absolute.slice(0, 8));
else pass.push('No absolute asset paths');

// ------------------------------------------------------------------- the SDK

const allText = files
  .filter((f) => ['.html', '.js'].includes(extname(f.rel)))
  .map((f) => readFileSync(f.path, 'utf8'))
  .join('\n');

const hasV3 = /crazygames-sdk-v3\.js/.test(allText);
const hasV2 = /crazygames-sdk-v2\.js/.test(allText) || /sdkGameLoadingStart/.test(allText);

if (hasV2) {
  fail('error', 'This build uses the v2 SDK. v3 is current; v2 sample code is still all over the web', [
    'sdkGameLoadingStart() -> loadingStart()',
    'sdkGameLoadingStop() -> loadingStop()',
    'async getters -> plain properties',
    'await SDK.init() is now required',
  ]);
} else if (!hasV3) {
  fail('warn', 'No CrazyGames SDK found. Optional for Basic Launch (ads are disabled there anyway); required for Full Launch');
} else {
  pass.push('CrazyGames SDK v3 script present');

  if (!/SDK\s*\.\s*init\s*\(/.test(allText)) {
    fail('error', 'SDK v3 requires an awaited init() before anything else works');
  }
  const events = ['loadingStart', 'loadingStop', 'gameplayStart', 'gameplayStop'];
  const missing = events.filter((e) => !new RegExp(`\\b${e}\\s*\\(`).test(allText));
  if (missing.includes('gameplayStart')) {
    fail('error', 'gameplayStart() is missing — initial download is measured up to this event, so without it your measured size is the whole bundle');
  }
  const others = missing.filter((m) => m !== 'gameplayStart');
  if (others.length) fail('warn', `SDK game events not found: ${others.join(', ')}`);
  if (!missing.length) pass.push('All four SDK game events present');
}

// ------------------------------------------------------- prohibited / advised

// `/requirements/gameplay/`: custom in-game fullscreen buttons are prohibited.
if (/requestFullscreen|webkitRequestFullscreen|requestFullScreen/.test(allText)) {
  fail('error', 'Calls requestFullscreen — custom in-game fullscreen buttons are prohibited; the platform provides fullscreen');
} else {
  pass.push('No custom fullscreen call');
}

// `/requirements/technical/`: disable text selection so long-press gestures behave.
const css = files
  .filter((f) => ['.css', '.html'].includes(extname(f.rel)))
  .map((f) => readFileSync(f.path, 'utf8'))
  .join('\n');
if (!/user-select\s*:\s*none/.test(css)) {
  fail('warn', 'No `user-select: none` — on mobile a long press will select text or raise the iOS callout');
} else {
  pass.push('Text selection disabled for mobile');
}

// ------------------------------------------------------------------- report

const result = {
  dir,
  totalBytes,
  fileCount: files.length,
  estimatedInitialBytes: initialBytes,
  findings,
  passed: pass,
  notChecked: [
    'Legibility at 821x462 and 800x450 — open the build at those sizes and read the HUD',
    'Max 1 click to gameplay — count the clicks from load to playing',
    'Ad placement: never during play, mute + pause on adStarted, no reward on adError',
    'Frame-rate independence at 144 Hz and 165 Hz — verify a fixed-step loop',
    'Mouse, keyboard and touch all work',
    'English present; originality; PEGI 12',
  ],
};

if (asJson) {
  console.log(JSON.stringify(result, null, 2));
  process.exit(findings.some((f) => f.level === 'error') ? 1 : 0);
}

const icon = { error: 'FAIL', warn: 'WARN' };
console.log(`\nCrazyGames build check — ${dir}\n`);
for (const p of pass) console.log(`  ok    ${p}`);
if (findings.length) console.log('');
for (const f of findings) {
  console.log(`  ${icon[f.level]}  ${f.text}`);
  for (const d of f.detail ?? []) console.log(`          ${d}`);
}

console.log('\nNot checked here — these need a human and a browser:');
for (const n of result.notChecked) console.log(`  ·  ${n}`);

const errors = findings.filter((f) => f.level === 'error').length;
const warns = findings.filter((f) => f.level === 'warn').length;
console.log(`\n${errors} blocking, ${warns} worth a look. Mechanical checks only — see above.\n`);
process.exit(errors ? 1 : 0);
