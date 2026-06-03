import { readFileSync, existsSync } from "fs";

export interface SkillFrontmatter {
  name: string;
  description: string;
  triggers: string[];
}

/**
 * Parses YAML frontmatter from a SKILL.md or agent.md file.
 * Returns null if file missing or frontmatter incomplete.
 */
export function parseSkillFrontmatter(
  filePath: string,
): SkillFrontmatter | null {
  if (!existsSync(filePath)) return null;

  const content = readFileSync(filePath, "utf8");
  const match = content.match(/^---[\r\n]+([\s\S]*?)[\r\n]+---/);
  if (!match) return null;

  const block = match[1];

  const nameMatch = block.match(/^name:\s*["']?(.+?)["']?\s*$/m);
  const descMatch = block.match(/^description:\s*["']?(.+?)["']?\s*$/m);

  if (!nameMatch || !descMatch) return null;

  const triggers: string[] = [];
  const triggersBlockMatch = block.match(
    /^triggers:\s*[\r\n]((?:[ \t]+-[ \t]+.+[\r\n]?)*)/m,
  );
  if (triggersBlockMatch) {
    for (const line of triggersBlockMatch[1].split(/[\r\n]+/)) {
      const t = line.match(/^[ \t]+-[ \t]+["']?(.+?)["']?\s*$/);
      if (t) triggers.push(t[1]);
    }
  }

  return {
    name: nameMatch[1].trim(),
    description: descMatch[1].trim(),
    triggers,
  };
}

/** Renders parsed frontmatter back to YAML string (for wrapper files). */
export function renderFrontmatter(fm: SkillFrontmatter): string {
  const triggersYaml =
    fm.triggers.length > 0
      ? `triggers:\n${fm.triggers.map((t) => `  - "${t}"`).join("\n")}\n`
      : "";
  return `---\nname: ${fm.name}\ndescription: ${fm.description}\n${triggersYaml}---`;
}
