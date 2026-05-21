import { initCommand } from './commands/init.js';
import { updateCommand } from './commands/update.js';

const [,, command, ...args] = process.argv;

switch (command) {
  case 'init':
    await initCommand();
    break;
  case 'update':
    await updateCommand(args);
    break;
  default:
    console.log('Usage: devflow-sync <command>');
    console.log('');
    console.log('Commands:');
    console.log('  init              Interactive first-time setup');
    console.log('  update            Re-sync using .devflow.json config');
    console.log('');
    console.log('Options for update:');
    console.log('  --dry-run         List files without writing');
    console.log('  --config <path>   Use a specific .devflow.json path');
    process.exit(command ? 1 : 0);
}
