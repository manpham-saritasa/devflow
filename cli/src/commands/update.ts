import { intro, outro, spinner, log } from '@clack/prompts';
import { resolve } from 'path';
import { readConfig, writeConfig, hasConfig } from '../config/io.js';
import { buildManifest } from '../sync/manifest.js';
import { writeFiles } from '../sync/writer.js';

interface UpdateOptions {
  dryRun: boolean;
  configPath?: string;
}

export async function updateCommand(args: string[]): Promise<void> {
  const dryRun = args.includes('--dry-run');
  const configIdx = args.indexOf('--config');
  const configPath = configIdx !== -1 ? args[configIdx + 1] : undefined;

  const targetDir = resolve(process.cwd());

  intro(`devflow-sync — update${dryRun ? ' (dry run)' : ''}`);

  if (!hasConfig(targetDir)) {
    log.error('No .devflow.json found. Run `npx devflow-sync init` first.');
    process.exit(1);
  }

  const config = readConfig(configPath ? resolve(configPath) : targetDir);
  if (!config) {
    log.error('Failed to read .devflow.json.');
    process.exit(1);
  }

  log.info(`Last sync: ${new Date(config.syncedAt).toLocaleString()}  •  cli@${config.cliVersion}`);

  const manifest = buildManifest(config, targetDir);
  log.info(`${manifest.length} files to sync.`);

  if (dryRun) {
    for (const entry of manifest) {
      log.info(`  ${entry.dest}`);
    }
    outro('Dry run complete — no files written.');
    return;
  }

  const s = spinner();
  s.start('Syncing files...');
  const results = writeFiles(manifest, config.conflictMode);
  const wrote = results.filter(r => r.action === 'wrote').length;
  const backed = results.filter(r => r.action === 'backed-up').length;
  const skipped = results.filter(r => r.action === 'skipped').length;
  s.stop(`Done — ${wrote} written, ${backed} backed up, ${skipped} skipped.`);

  writeConfig(targetDir, {
    ...config,
    syncedAt: new Date().toISOString(),
    cliVersion: '1.0.0',
  });

  outro('Sync complete.');
}
