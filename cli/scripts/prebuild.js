import { cpSync, mkdirSync, rmSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const cliRoot = resolve(__dirname, '..');
const repoRoot = resolve(cliRoot, '..');
const contentDir = resolve(cliRoot, 'content');

if (existsSync(contentDir)) {
  rmSync(contentDir, { recursive: true });
}

mkdirSync(contentDir, { recursive: true });

cpSync(resolve(repoRoot, 'AGENTS.md'), resolve(contentDir, 'AGENTS.md'));
cpSync(resolve(repoRoot, '.ai'), resolve(contentDir, '.ai'), { recursive: true });
cpSync(resolve(repoRoot, '.cursor'), resolve(contentDir, '.cursor'), { recursive: true });

console.log('✓ Content bundled into cli/content/');
