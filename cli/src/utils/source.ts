import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

export function getContentRoot(): string {
  const __dirname = dirname(fileURLToPath(import.meta.url));
  // dist/index.js → ../content  (one level up from dist/)
  return resolve(__dirname, '..', 'content');
}
