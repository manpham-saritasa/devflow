import { readFileSync, writeFileSync, existsSync } from 'fs';
import { resolve } from 'path';
import { DevflowConfig, DevflowConfigSchema } from './schema.js';

export const CONFIG_FILENAME = '.devflow.json';

export function configPath(targetDir: string): string {
  return resolve(targetDir, CONFIG_FILENAME);
}

export function readConfig(targetDir: string): DevflowConfig | null {
  const path = configPath(targetDir);
  if (!existsSync(path)) return null;
  const raw = JSON.parse(readFileSync(path, 'utf8'));
  return DevflowConfigSchema.parse(raw);
}

export function writeConfig(targetDir: string, config: DevflowConfig): void {
  writeFileSync(configPath(targetDir), JSON.stringify(config, null, 2) + '\n', 'utf8');
}

export function hasConfig(targetDir: string): boolean {
  return existsSync(configPath(targetDir));
}
