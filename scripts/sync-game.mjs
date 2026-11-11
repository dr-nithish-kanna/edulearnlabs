#!/usr/bin/env node
// Copies a game's build into the website so it is served from our own domain at /play/<game-id>/.
// Same domain matters: the game and the website talk with postMessage and only trust their own origin.
//
// Usage: npm run sync-game -- ../addition-grade-1
// The game repo must be committed (no uncommitted changes), so the website always records an exact version.
// Why copy builds into this repo (for now): the game and kit repos are private, so the website's deploy cannot
// fetch them without a token. A copied build is small (about 50 KB) and pinned to a commit in src/data/games.json.
import { execSync } from 'node:child_process';
import { cpSync, existsSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';

const gameDir = resolve(process.argv[2] ?? '');
if (!existsSync(join(gameDir, 'game.json'))) { console.error('Give the path to a game repo, for example ../addition-grade-1'); process.exit(1); }
const sh = cmd => execSync(cmd, { cwd: gameDir, stdio: ['ignore', 'pipe', 'inherit'] }).toString().trim();

if (sh('git status --porcelain')) { console.error('The game repo has uncommitted changes. Commit them first.'); process.exit(1); }
const commit = sh('git rev-parse --short HEAD');
const def = JSON.parse(readFileSync(join(gameDir, 'game.json'), 'utf8'));

console.log(`Building ${def.id} at ${commit}...`);
execSync('npm run build', { cwd: gameDir, stdio: 'inherit' });

const target = resolve('public/play', def.id);
rmSync(target, { recursive: true, force: true });
cpSync(join(gameDir, 'dist'), target, { recursive: true });
writeFileSync(join(target, 'BUILD_INFO.json'), JSON.stringify({ game: def.id, version: def.version, commit, builtAt: new Date().toISOString() }, null, 2) + '\n');

const catalogPath = resolve('src/data/games.json');
const catalog = JSON.parse(readFileSync(catalogPath, 'utf8'));
const entry = catalog.find(g => g.id === def.id);
if (entry) { entry.source = { ...entry.source, commit }; writeFileSync(catalogPath, JSON.stringify(catalog, null, 2) + '\n'); }
else console.warn(`Add "${def.id}" to src/data/games.json so it gets a page.`);
console.log(`Done: public/play/${def.id}/ is version ${def.version} (${commit}).`);
