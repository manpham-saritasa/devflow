import { cpSync, writeFileSync, renameSync, existsSync, mkdirSync } from 'fs';
import { dirname } from 'path';
import { ConflictMode } from '../config/schema.js';
import { FileCopyEntry } from './manifest.js';

export type WriteAction = 'wrote' | 'backed-up' | 'skipped';

export interface WriteResult {
  entry: FileCopyEntry;
  action: WriteAction;
}

export function writeFiles(
  entries: FileCopyEntry[],
  conflictMode: ConflictMode,
  dryRun = false,
): WriteResult[] {
  return entries.map(entry => {
    const exists = existsSync(entry.dest);

    if (exists && conflictMode === 'skip') {
      return { entry, action: 'skipped' };
    }

    if (dryRun) {
      return { entry, action: exists && conflictMode === 'backup' ? 'backed-up' : 'wrote' };
    }

    mkdirSync(dirname(entry.dest), { recursive: true });

    if (exists && conflictMode === 'backup') {
      renameSync(entry.dest, entry.dest + '.devflow.bak');
    }

    if (entry.isInline) {
      writeFileSync(entry.dest, entry.src, 'utf8');
    } else {
      cpSync(entry.src, entry.dest);
    }

    return { entry, action: exists && conflictMode === 'backup' ? 'backed-up' : 'wrote' };
  });
}
