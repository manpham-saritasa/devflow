import { readdirSync, existsSync } from 'fs';
import { resolve, join } from 'path';
import { DevflowConfig, AiTool } from '../config/schema.js';
import { getContentRoot } from '../utils/source.js';

export interface FileCopyEntry {
  src: string;
  dest: string;
  /** When true, src is the exact content to write (not a file path) */
  isInline?: boolean;
}

const CURSOR_POINTER_CONTENT = `---
description: Main AI rules for this repository
alwaysApply: true
---

Follow all rules defined in \`AGENTS.md\` in the project root.
If \`.ai/startup.md\` exists, read it before starting work.
`;

function agentsMdDest(tool: AiTool): string | null {
  switch (tool) {
    case 'claude':    return 'CLAUDE.md';
    case 'gemini':    return 'GEMINI.md';
    case 'windsurf':  return '.windsurfrules';
    case 'codeium':   return '.codeiumrules';
    case 'aider':     return 'CONVENTIONS.md';
    case 'zed':       return '.rules';
    case 'copilot':   return '.github/copilot-instructions.md';
    case 'cursor':    return null; // handled separately
  }
}

export function buildManifest(config: DevflowConfig, targetDir: string): FileCopyEntry[] {
  const contentRoot = getContentRoot();
  const agentsSrc = resolve(contentRoot, 'AGENTS.md');
  const entries: FileCopyEntry[] = [];

  // Always: AGENTS.md
  entries.push({ src: agentsSrc, dest: resolve(targetDir, 'AGENTS.md') });

  // Per AI tool
  for (const tool of config.tools) {
    const dest = agentsMdDest(tool);
    if (dest) {
      entries.push({ src: agentsSrc, dest: resolve(targetDir, dest) });
    }

    if (tool === 'cursor') {
      entries.push({
        src: CURSOR_POINTER_CONTENT,
        dest: resolve(targetDir, '.cursor/rules/main.mdc'),
        isInline: true,
      });
    }

    if (tool === 'copilot') {
      // Also sync .ai/copilot/ folder
      const copilotSrc = resolve(contentRoot, '.ai', 'copilot');
      if (existsSync(copilotSrc)) {
        entries.push(...copyDirEntries(copilotSrc, resolve(targetDir, '.ai', 'copilot')));
      }
    }
  }

  // Per component
  for (const component of config.components) {
    switch (component) {
      case 'startup':
        entries.push({
          src: resolve(contentRoot, '.ai', 'startup.md'),
          dest: resolve(targetDir, '.ai', 'startup.md'),
        });
        break;

      case 'agents': {
        const agentsRoot = resolve(contentRoot, '.ai', 'agents');
        const selected = config.agents ?? listItems(agentsRoot);
        for (const item of selected) {
          const itemPath = resolve(agentsRoot, item + '.md');
          if (existsSync(itemPath)) {
            entries.push({ src: itemPath, dest: resolve(targetDir, '.ai', 'agents', item + '.md') });
          }
        }
        // Always copy templates/ subdir
        entries.push(...copyDirEntries(
          resolve(agentsRoot, 'templates'),
          resolve(targetDir, '.ai', 'agents', 'templates'),
        ));
        // Always copy README.md if exists
        const readmePath = resolve(agentsRoot, 'README.md');
        if (existsSync(readmePath)) {
          entries.push({ src: readmePath, dest: resolve(targetDir, '.ai', 'agents', 'README.md') });
        }
        break;
      }

      case 'prompts': {
        const promptsRoot = resolve(contentRoot, '.ai', 'prompts');
        const selected = config.prompts ?? listItems(promptsRoot);
        for (const item of selected) {
          const itemPath = resolve(promptsRoot, item + '.md');
          if (existsSync(itemPath)) {
            entries.push({ src: itemPath, dest: resolve(targetDir, '.ai', 'prompts', item + '.md') });
          }
        }
        // Always copy index.md if exists
        const indexPath = resolve(promptsRoot, 'index.md');
        if (existsSync(indexPath)) {
          entries.push({ src: indexPath, dest: resolve(targetDir, '.ai', 'prompts', 'index.md') });
        }
        break;
      }

      case 'instructions': {
        const instructionsRoot = resolve(contentRoot, '.ai', 'instructions');
        const selected = config.instructions ?? listItems(instructionsRoot);
        for (const item of selected) {
          const itemPath = resolve(instructionsRoot, item + '.md');
          if (existsSync(itemPath)) {
            entries.push({ src: itemPath, dest: resolve(targetDir, '.ai', 'instructions', item + '.md') });
          }
        }
        break;
      }

      case 'skills': {
        const skillsRoot = resolve(contentRoot, '.ai', 'skills');
        const selected = config.skills ?? listSkills(skillsRoot);
        for (const skill of selected) {
          const skillSrc = resolve(skillsRoot, skill);
          if (existsSync(skillSrc)) {
            entries.push(...copyDirEntries(skillSrc, resolve(targetDir, '.ai', 'skills', skill)));
          }
        }
        break;
      }
    }
  }

  return dedupe(entries);
}

/** Enumerate all files under srcDir recursively, returning copy entries. */
function copyDirEntries(srcDir: string, destDir: string): FileCopyEntry[] {
  if (!existsSync(srcDir)) return [];
  const entries: FileCopyEntry[] = [];
  for (const name of readdirSync(srcDir, { recursive: true, withFileTypes: true })) {
    if (!name.isFile()) continue;
    const srcPath = join(name.parentPath ?? name.path, name.name);
    const rel = srcPath.slice(srcDir.length + 1);
    entries.push({ src: srcPath, dest: join(destDir, rel) });
  }
  return entries;
}

export function listSkills(skillsRoot: string): string[] {
  if (!existsSync(skillsRoot)) return [];
  return readdirSync(skillsRoot, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name);
}

export function listItems(dir: string): string[] {
  if (!existsSync(dir)) return [];
  return readdirSync(dir, { withFileTypes: true })
    .filter(f => f.isFile() && f.name.endsWith('.md'))
    .map(f => f.name.slice(0, -3)); // remove .md extension
}

function dedupe(entries: FileCopyEntry[]): FileCopyEntry[] {
  const seen = new Set<string>();
  return entries.filter(e => {
    if (seen.has(e.dest)) return false;
    seen.add(e.dest);
    return true;
  });
}
