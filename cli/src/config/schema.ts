import { z } from 'zod';

export const AI_TOOLS = ['claude', 'gemini', 'copilot', 'cursor', 'windsurf', 'codeium', 'aider', 'zed'] as const;
export const COMPONENTS = ['agents', 'skills', 'prompts', 'instructions', 'startup', 'plugins', 'rules'] as const;
export const CONFLICT_MODES = ['overwrite', 'backup', 'skip'] as const;

export type AiTool = (typeof AI_TOOLS)[number];
export type Component = (typeof COMPONENTS)[number];
export type ConflictMode = (typeof CONFLICT_MODES)[number];

export const DevflowConfigSchema = z.object({
  version: z.string(),
  syncedAt: z.string(),
  cliVersion: z.string(),
  tools: z.array(z.enum(AI_TOOLS)),
  components: z.array(z.enum(COMPONENTS)),
  agents: z.array(z.string()).nullable().default(null),
  skills: z.array(z.string()).nullable().default(null),
  prompts: z.array(z.string()).nullable().default(null),
  instructions: z.array(z.string()).nullable().default(null),
  plugins: z.array(z.string()).nullable().default(null),
  rules: z.array(z.string()).nullable().default(null),
  conflictMode: z.enum(CONFLICT_MODES),
});

export type DevflowConfig = z.infer<typeof DevflowConfigSchema>;

export const TOOL_LABELS: Record<AiTool, string> = {
  claude: 'Claude Code',
  gemini: 'Gemini CLI',
  copilot: 'GitHub Copilot',
  cursor: 'Cursor',
  windsurf: 'Windsurf',
  codeium: 'Codeium',
  aider: 'Aider',
  zed: 'Zed / JetBrains AI',
};

export const COMPONENT_LABELS: Record<Component, string> = {
  agents: 'Agents (planner, coder, reviewer)',
  skills: 'Skills (automation workflows)',
  prompts: 'Prompts (reusable templates)',
  instructions: 'Instructions (coding & communication rules)',
  startup: 'Startup (session entry point)',
  plugins: 'Plugins (devflow skills, commands & orchestrator)',
  rules: 'Rules (PR rules, coding rules, session)',
};
