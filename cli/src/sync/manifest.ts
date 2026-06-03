import { readdirSync, existsSync } from "fs";
import { resolve, join } from "path";
import { DevflowConfig, AiTool } from "../config/schema.js";
import { getContentRoot } from "../utils/source.js";
import {
  parseSkillFrontmatter,
  renderFrontmatter,
} from "../utils/frontmatter.js";

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
    case "claude":
      return "CLAUDE.md";
    case "gemini":
      return "GEMINI.md";
    case "windsurf":
      return ".windsurfrules";
    case "codeium":
      return ".codeiumrules";
    case "aider":
      return "CONVENTIONS.md";
    case "zed":
      return ".rules";
    case "copilot":
      return ".github/copilot-instructions.md";
    case "cursor":
      return null; // handled separately
  }
}

export function buildManifest(
  config: DevflowConfig,
  targetDir: string,
): FileCopyEntry[] {
  const contentRoot = getContentRoot();
  const agentsSrc = resolve(contentRoot, "AGENTS.md");
  const entries: FileCopyEntry[] = [];

  // Always: AGENTS.md
  entries.push({ src: agentsSrc, dest: resolve(targetDir, "AGENTS.md") });

  // Per AI tool
  for (const tool of config.tools) {
    const dest = agentsMdDest(tool);
    if (dest) {
      entries.push({ src: agentsSrc, dest: resolve(targetDir, dest) });
    }

    if (tool === "cursor") {
      entries.push({
        src: CURSOR_POINTER_CONTENT,
        dest: resolve(targetDir, ".cursor/rules/main.mdc"),
        isInline: true,
      });
    }

    if (tool === "copilot") {
      // Also sync .ai/copilot/ folder
      const copilotSrc = resolve(contentRoot, ".ai", "copilot");
      if (existsSync(copilotSrc)) {
        entries.push(
          ...copyDirEntries(copilotSrc, resolve(targetDir, ".ai", "copilot")),
        );
      }
    }
  }

  // Per component
  for (const component of config.components) {
    switch (component) {
      case "startup":
        entries.push({
          src: resolve(contentRoot, ".ai", "startup.md"),
          dest: resolve(targetDir, ".ai", "startup.md"),
        });
        break;

      case "agents": {
        const agentsRoot = resolve(contentRoot, ".ai", "agents");
        const selected = config.agents ?? listItems(agentsRoot);
        for (const item of selected) {
          const itemPath = resolve(agentsRoot, item + ".md");
          if (existsSync(itemPath)) {
            entries.push({
              src: itemPath,
              dest: resolve(targetDir, ".ai", "agents", item + ".md"),
            });
          }
        }
        // Always copy templates/ subdir
        entries.push(
          ...copyDirEntries(
            resolve(agentsRoot, "templates"),
            resolve(targetDir, ".ai", "agents", "templates"),
          ),
        );
        // Always copy README.md if exists
        const readmePath = resolve(agentsRoot, "README.md");
        if (existsSync(readmePath)) {
          entries.push({
            src: readmePath,
            dest: resolve(targetDir, ".ai", "agents", "README.md"),
          });
        }
        break;
      }

      case "prompts": {
        const promptsRoot = resolve(contentRoot, ".ai", "prompts");
        const selected = config.prompts ?? listItems(promptsRoot);
        for (const item of selected) {
          const itemPath = resolve(promptsRoot, item + ".md");
          if (existsSync(itemPath)) {
            entries.push({
              src: itemPath,
              dest: resolve(targetDir, ".ai", "prompts", item + ".md"),
            });
          }
        }
        // Always copy index.md if exists
        const indexPath = resolve(promptsRoot, "index.md");
        if (existsSync(indexPath)) {
          entries.push({
            src: indexPath,
            dest: resolve(targetDir, ".ai", "prompts", "index.md"),
          });
        }
        break;
      }

      case "instructions": {
        const instructionsRoot = resolve(contentRoot, ".ai", "rules");
        const selected = config.instructions ?? listItems(instructionsRoot);
        for (const item of selected) {
          const itemPath = resolve(instructionsRoot, item + ".md");
          if (existsSync(itemPath)) {
            entries.push({
              src: itemPath,
              dest: resolve(targetDir, ".ai", "instructions", item + ".md"),
            });
          }
        }
        break;
      }

      case "skills": {
        const skillsRoot = resolve(contentRoot, ".ai", "skills");
        const selected = config.skills ?? listSkills(skillsRoot);
        for (const skill of selected) {
          const skillSrc = resolve(skillsRoot, skill);
          if (existsSync(skillSrc)) {
            entries.push(
              ...copyDirEntries(
                skillSrc,
                resolve(targetDir, ".ai", "skills", skill),
              ),
            );
          }
        }
        // Claude: generate .claude/skills/ wrappers referencing .ai/skills/
        if (config.tools.includes("claude")) {
          for (const skill of selected) {
            const skillMd = resolve(
              contentRoot,
              ".ai",
              "skills",
              skill,
              "SKILL.md",
            );
            const fm = parseSkillFrontmatter(skillMd);
            if (fm) {
              entries.push({
                src: buildSkillWrapper(fm, `.ai/skills/${skill}/SKILL.md`),
                dest: resolve(
                  targetDir,
                  ".claude",
                  "skills",
                  fm.name,
                  "SKILL.md",
                ),
                isInline: true,
              });
            }
          }
        }
        // Zed: generate .agents/skills/<name>/SKILL.md wrappers referencing .ai/skills/
        if (config.tools.includes("zed")) {
          for (const skill of selected) {
            const skillMd = resolve(
              contentRoot,
              ".ai",
              "skills",
              skill,
              "SKILL.md",
            );
            const fm = parseSkillFrontmatter(skillMd);
            if (fm) {
              entries.push({
                src: buildSkillWrapper(fm, `.ai/skills/${skill}/SKILL.md`),
                dest: resolve(
                  targetDir,
                  ".agents",
                  "skills",
                  fm.name,
                  "SKILL.md",
                ),
                isInline: true,
              });
            }
          }
        }
        break;
      }

      case "plugins": {
        const pluginsRoot = resolve(contentRoot, ".ai", "plugins");
        if (!existsSync(pluginsRoot)) break;
        for (const plugin of readdirSync(pluginsRoot, { withFileTypes: true })
          .filter((d) => d.isDirectory())
          .map((d) => d.name)) {
          const pluginSrc = resolve(pluginsRoot, plugin);
          entries.push(
            ...copyDirEntries(
              pluginSrc,
              resolve(targetDir, ".ai", "plugins", plugin),
            ),
          );

          // Claude: generate .claude/skills/ wrappers for each skill + agent.md
          if (config.tools.includes("claude")) {
            for (const { subdir, skillFile } of listPluginSkills(pluginSrc)) {
              const refPath = subdir
                ? `.ai/plugins/${plugin}/${subdir}/SKILL.md`
                : `.ai/plugins/${plugin}/agent.md`;
              const fm = parseSkillFrontmatter(skillFile);
              if (fm) {
                entries.push({
                  src: buildSkillWrapper(fm, refPath),
                  dest: resolve(
                    targetDir,
                    ".claude",
                    "skills",
                    fm.name,
                    "SKILL.md",
                  ),
                  isInline: true,
                });
              }
            }
          }
          // Zed: generate .agents/skills/<name>/SKILL.md wrappers for each plugin skill
          if (config.tools.includes("zed")) {
            for (const { subdir, skillFile } of listPluginSkills(pluginSrc)) {
              const refPath = subdir
                ? `.ai/plugins/${plugin}/${subdir}/SKILL.md`
                : `.ai/plugins/${plugin}/agent.md`;
              const fm = parseSkillFrontmatter(skillFile);
              if (fm) {
                entries.push({
                  src: buildSkillWrapper(fm, refPath),
                  dest: resolve(
                    targetDir,
                    ".agents",
                    "skills",
                    fm.name,
                    "SKILL.md",
                  ),
                  isInline: true,
                });
              }
            }
          }
        }
        break;
      }

      case "rules": {
        const rulesRoot = resolve(contentRoot, ".ai", "rules");
        const selected = config.rules ?? listItems(rulesRoot);
        for (const item of selected) {
          const itemPath = resolve(rulesRoot, item + ".md");
          if (existsSync(itemPath)) {
            entries.push({
              src: itemPath,
              dest: resolve(targetDir, ".ai", "rules", item + ".md"),
            });
          }
        }
        break;
      }
    }
  }

  // Claude: copy agents to .claude/agents/ when agents component is selected
  if (config.tools.includes("claude") && config.components.includes("agents")) {
    const agentsRoot = resolve(contentRoot, ".ai", "agents");
    const selected = config.agents ?? listItems(agentsRoot);
    for (const item of selected) {
      const itemPath = resolve(agentsRoot, item + ".md");
      if (existsSync(itemPath)) {
        entries.push({
          src: itemPath,
          dest: resolve(targetDir, ".claude", "agents", item + ".md"),
        });
      }
    }
  }

  return dedupe(entries);
}

/** Enumerate all files under srcDir recursively, returning copy entries. */
function copyDirEntries(srcDir: string, destDir: string): FileCopyEntry[] {
  if (!existsSync(srcDir)) return [];
  const entries: FileCopyEntry[] = [];
  for (const name of readdirSync(srcDir, {
    recursive: true,
    withFileTypes: true,
  })) {
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
    .filter((d) => d.isDirectory())
    .map((d) => d.name);
}

export function listItems(dir: string): string[] {
  if (!existsSync(dir)) return [];
  return readdirSync(dir, { withFileTypes: true })
    .filter((f) => f.isFile() && f.name.endsWith(".md"))
    .map((f) => f.name.slice(0, -3)); // remove .md extension
}

function dedupe(entries: FileCopyEntry[]): FileCopyEntry[] {
  const seen = new Set<string>();
  return entries.filter((e) => {
    if (seen.has(e.dest)) return false;
    seen.add(e.dest);
    return true;
  });
}

/**
 * Returns all SKILL.md files (and agent.md) found in a plugin directory.
 * Each entry has the subdir name (empty string for root agent.md) and the full skill file path.
 */
function listPluginSkills(
  pluginDir: string,
): Array<{ subdir: string; skillFile: string }> {
  if (!existsSync(pluginDir)) return [];
  const results: Array<{ subdir: string; skillFile: string }> = [];

  // Root agent.md (orchestrator)
  const agentMd = resolve(pluginDir, "agent.md");
  if (existsSync(agentMd)) {
    results.push({ subdir: "", skillFile: agentMd });
  }

  // Recursively find SKILL.md files
  function scan(dir: string, prefix: string) {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue;
      const skillMd = resolve(dir, entry.name, "SKILL.md");
      const relPath = prefix ? `${prefix}/${entry.name}` : entry.name;
      if (existsSync(skillMd)) {
        results.push({ subdir: relPath, skillFile: skillMd });
      } else {
        // Recurse into subdirectories (e.g. devflow/skills/)
        scan(resolve(dir, entry.name), relPath);
      }
    }
  }
  scan(pluginDir, "");

  return results;
}

/** Generates inline SKILL.md wrapper content that delegates via @ reference. */
function buildSkillWrapper(
  fm: ReturnType<typeof parseSkillFrontmatter>,
  refPath: string,
): string {
  if (!fm) return "";
  return `${renderFrontmatter(fm)}\n\n@${refPath}\n`;
}
