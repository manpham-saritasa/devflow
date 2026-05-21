import { intro, outro, text, multiselect, select, confirm, spinner, isCancel, cancel } from '@clack/prompts';
import { resolve } from 'path';
import { existsSync } from 'fs';
import {
  AI_TOOLS,
  COMPONENTS,
  CONFLICT_MODES,
  TOOL_LABELS,
  COMPONENT_LABELS,
  DevflowConfig,
} from '../config/schema.js';
import { writeConfig, hasConfig } from '../config/io.js';
import { buildManifest, listSkills, listItems } from '../sync/manifest.js';
import { writeFiles } from '../sync/writer.js';
import { getContentRoot } from '../utils/source.js';

interface ComponentSelection {
  agents: string[] | null;
  skills: string[] | null;
  prompts: string[] | null;
  instructions: string[] | null;
}

export async function initCommand(): Promise<void> {
  intro('devflow-sync — init');

  const targetInput = await text({
    message: 'Target directory?',
    placeholder: '.',
    defaultValue: '.',
  });
  if (isCancel(targetInput)) { cancel('Cancelled.'); process.exit(0); }

  const targetDir = resolve(process.cwd(), String(targetInput));

  if (!existsSync(targetDir)) {
    cancel(`Directory does not exist: ${targetDir}`);
    process.exit(1);
  }

  if (hasConfig(targetDir)) {
    const overwrite = await confirm({
      message: `.devflow.json already exists in target. Overwrite config?`,
    });
    if (isCancel(overwrite) || !overwrite) { cancel('Cancelled.'); process.exit(0); }
  }

  const toolsAnswer = await multiselect({
    message: 'Which AI tools does this project use?',
    options: AI_TOOLS.map(t => ({ value: t, label: TOOL_LABELS[t] })),
    required: true,
  });
  if (isCancel(toolsAnswer)) { cancel('Cancelled.'); process.exit(0); }
  const tools = toolsAnswer as typeof AI_TOOLS[number][];

  const componentsAnswer = await multiselect({
    message: 'Which components do you want to sync?',
    options: COMPONENTS.map(c => ({ value: c, label: COMPONENT_LABELS[c] })),
    required: true,
  });
  if (isCancel(componentsAnswer)) { cancel('Cancelled.'); process.exit(0); }
  const components = componentsAnswer as typeof COMPONENTS[number][];

  const contentRoot = getContentRoot();
  const componentSelection: ComponentSelection = {
    agents: null,
    skills: null,
    prompts: null,
    instructions: null,
  };

  // Ask for each filterable component
  if (components.includes('agents')) {
    const allAgents = await confirm({ message: 'Sync all agents?' });
    if (isCancel(allAgents)) { cancel('Cancelled.'); process.exit(0); }
    if (!allAgents) {
      const available = listItems(resolve(contentRoot, '.ai', 'agents')).filter(
        name => name !== 'README' && !name.startsWith('.')
      );
      if (available.length > 0) {
        const selected = await multiselect({
          message: 'Which agents?',
          options: available.map(a => ({ value: a, label: a })),
          required: true,
        });
        if (isCancel(selected)) { cancel('Cancelled.'); process.exit(0); }
        componentSelection.agents = selected as string[];
      }
    }
  }

  if (components.includes('skills')) {
    const available = listSkills(resolve(contentRoot, '.ai', 'skills'));
    if (available.length > 0) {
      const allSkills = await confirm({ message: 'Sync all skills?' });
      if (isCancel(allSkills)) { cancel('Cancelled.'); process.exit(0); }
      if (!allSkills) {
        const selected = await multiselect({
          message: 'Which skills?',
          options: available.map(s => ({ value: s, label: s })),
          required: true,
        });
        if (isCancel(selected)) { cancel('Cancelled.'); process.exit(0); }
        componentSelection.skills = selected as string[];
      }
    }
  }

  if (components.includes('prompts')) {
    const allPrompts = await confirm({ message: 'Sync all prompts?' });
    if (isCancel(allPrompts)) { cancel('Cancelled.'); process.exit(0); }
    if (!allPrompts) {
      const available = listItems(resolve(contentRoot, '.ai', 'prompts')).filter(
        name => name !== 'index' && !name.startsWith('.')
      );
      if (available.length > 0) {
        const selected = await multiselect({
          message: 'Which prompts?',
          options: available.map(p => ({ value: p, label: p })),
          required: true,
        });
        if (isCancel(selected)) { cancel('Cancelled.'); process.exit(0); }
        componentSelection.prompts = selected as string[];
      }
    }
  }

  if (components.includes('instructions')) {
    const allInstructions = await confirm({ message: 'Sync all instructions?' });
    if (isCancel(allInstructions)) { cancel('Cancelled.'); process.exit(0); }
    if (!allInstructions) {
      const available = listItems(resolve(contentRoot, '.ai', 'instructions')).filter(
        name => !name.startsWith('.')
      );
      if (available.length > 0) {
        const selected = await multiselect({
          message: 'Which instructions?',
          options: available.map(i => ({ value: i, label: i })),
          required: true,
        });
        if (isCancel(selected)) { cancel('Cancelled.'); process.exit(0); }
        componentSelection.instructions = selected as string[];
      }
    }
  }

  const conflictModeAnswer = await select({
    message: 'How to handle existing files?',
    options: [
      { value: 'overwrite', label: 'Overwrite' },
      { value: 'backup', label: 'Backup (.devflow.bak)' },
      { value: 'skip', label: 'Skip existing' },
    ],
  });
  if (isCancel(conflictModeAnswer)) { cancel('Cancelled.'); process.exit(0); }
  const conflictMode = conflictModeAnswer as typeof CONFLICT_MODES[number];

  const config: DevflowConfig = {
    version: '1',
    syncedAt: new Date().toISOString(),
    cliVersion: '1.0.0',
    tools,
    components,
    agents: componentSelection.agents,
    skills: componentSelection.skills,
    prompts: componentSelection.prompts,
    instructions: componentSelection.instructions,
    conflictMode,
  };

  const manifest = buildManifest(config, targetDir);

  const ok = await confirm({ message: `Write ${manifest.length} files to ${targetDir}?` });
  if (isCancel(ok) || !ok) { cancel('Cancelled.'); process.exit(0); }

  const s = spinner();
  s.start('Writing files...');
  const results = writeFiles(manifest, conflictMode);
  s.stop(`Done — ${results.filter(r => r.action === 'wrote').length} written, ${results.filter(r => r.action === 'backed-up').length} backed up, ${results.filter(r => r.action === 'skipped').length} skipped.`);

  writeConfig(targetDir, config);

  outro(`Synced. Run \`npx devflow-sync update\` to re-sync later.`);
}
