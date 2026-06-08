import { cpSync, mkdirSync, rmSync, existsSync, readdirSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const cliRoot = resolve(__dirname, "..");
const repoRoot = resolve(cliRoot, "..");
const contentDir = resolve(cliRoot, "content");

if (existsSync(contentDir)) {
  try {
    rmSync(contentDir, { recursive: true });
  } catch {
    /* ok */
  }
}

try {
  mkdirSync(contentDir, { recursive: true });
} catch (e) {
  console.error("mkdir failed:", e.message);
  process.exit(1);
}

try {
  const agentsSource = existsSync(resolve(repoRoot, "AGENTS.md"))
    ? resolve(repoRoot, "AGENTS.md")
    : resolve(repoRoot, ".ai", "rules", "core.md");
  cpSync(agentsSource, resolve(contentDir, "AGENTS.md"));
} catch (e) {
  console.error("AGENTS.md copy failed:", e.message);
}
try {
  cpSync(resolve(repoRoot, ".ai"), resolve(contentDir, ".ai"), {
    recursive: true,
  });
} catch (e) {
  console.error(".ai copy failed:", e.message);
}
try {
  cpSync(resolve(repoRoot, ".cursor"), resolve(contentDir, ".cursor"), {
    recursive: true,
  });
} catch (e) {
  console.error(".cursor copy failed:", e.message);
}
try {
  cpSync(resolve(repoRoot, ".codex"), resolve(contentDir, ".codex"), {
    recursive: true,
  });
} catch (e) {
  console.error(".codex copy failed:", e.message);
}

console.log("✓ Content bundled into cli/content/");
if (existsSync(resolve(contentDir, ".ai/skills"))) {
  console.log(
    "  Skills: " + readdirSync(resolve(contentDir, ".ai/skills")).join(", "),
  );
}
