import { log } from '@clack/prompts';

export function info(msg: string): void {
  log.info(msg);
}

export function success(msg: string): void {
  log.success(msg);
}

export function warn(msg: string): void {
  log.warn(msg);
}

export function error(msg: string): void {
  log.error(msg);
}
