# Skill Index

20+ skills available. LLM reads this once to discover all capabilities.

## Agent Definition (1)

| Agent | Path | Description |
|-------|------|-------------|
| refactorflow | `.ai/agents/refactorflow.md` | Auto-drives full refactor flow: review → grill → execute → verify |

## Devflow Plugin (11)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| dev-start | `.ai/plugins/devflow/1.dev-start/` | `dev-start`, `devstart` | Create gitflow branch for Jira task |
| dev-plan | `.ai/plugins/devflow/2.dev-plan/` | `dev-plan`, `devplan` | Create execution plan from task evidence |
| dev-code | `.ai/plugins/devflow/3.dev-code/` | `dev-code`, `devcode` | Implement planned changes, write changelog |
| dev-review | `.ai/plugins/devflow/4.dev-review/` | `dev-review`, `devreview` | Review code against plan + changelog |
| dev-ship | `.ai/plugins/devflow/5.dev-ship-pr-jira/` | `dev-ship`, `dev-ship-pr-jira` | Create PR + comment Jira |
| dev-fix-pr | `.ai/plugins/devflow/6.dev-fix-pr/` | `dev-fix-pr`, `devfixpr` | Fix PR review comments |
| dev-finish | `.ai/plugins/devflow/7.dev-finish/` | `dev-finish`, `devfinish` | Merge PR, delete branch, cleanup |
| dev-adr | `.ai/plugins/devflow/8.dev-adr/` | `dev-adr`, `adr` | Create Architecture Decision Record |
| dev-commit | `.ai/plugins/devflow/dev-commit/` | `dev-commit`, `devcommit` | Stage + commit in related groups |
| dev-get | `.ai/plugins/devflow/dev-get/` | `dev-get`, `devget` | Pull Jira issue into task folder |
| dev-review-pr | `.ai/plugins/devflow/dev-review-pr/` | `review-pr`, `reviewpr` | Review any PR across 8 dimensions |

## Jiraflow Plugin (3)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| jira-urgent | `.ai/plugins/jiraflow/jira-urgent/` | `jurgent` | Find comments where team is waiting on you |
| jira-task | `.ai/plugins/jiraflow/jira-task/` | `jtask` | List assigned tasks by status group |
| jira-move | `.ai/plugins/jiraflow/jira-move/` | `jmove` | Move tasks through pipeline milestones |

## Refactorflow Plugin (6)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| plan | `.ai/plugins/refactorflow/skills/1.plan/` | `refactor`, `plan` | Diagnose architecture friction, write plan |
| grill | `.ai/plugins/refactorflow/skills/2.grill/` | `grill` | Pressure-test refactor plan |
| structure | `.ai/plugins/refactorflow/skills/3.structure/` | — (routed) | Fix boundaries, ownership, layout |
| api | `.ai/plugins/refactorflow/skills/4.api/` | — (routed) | Redesign contracts with migration planning |
| simplify | `.ai/plugins/refactorflow/skills/5.simplify/` | — (routed) | Reduce local complexity, nesting, naming |
| verify | `.ai/plugins/refactorflow/skills/6.verify/` | `verify` | Verify against original specs + quality |

## Matt Pocock Skills (4)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| caveman | `.ai/skills/matt-pocock/caveman/` | `caveman` | Ultra-compressed communication mode |
| grill-me | `.ai/skills/matt-pocock/grill-me/` | `grill me`, `grill` | Interview about design decisions |
| handoff | `.ai/skills/matt-pocock/handoff/` | `handoff` | Create handoff doc for another agent |
| write-a-skill | `.ai/skills/matt-pocock/write-a-skill/` | `write-a-skill` | Create new skills with proper structure |

## Conversion Skills (2)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| md-to-html | `.ai/skills/md-to-html/` | `md-to-html` | Convert Markdown to standalone HTML |
| md-to-docx | `.ai/skills/md-to-docx/` | `md-to-docx` | Convert Markdown to Word document |

## Review Skills (2)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| review-design | `.agents/skills/review-design/` | `review design`, `audit` | Review plugins/skills/workflows across 13 dimensions |
| review-md | `.agents/skills/review-md/` | `review md`, `check md`, `audit markdown` | Audit markdown files for duplicates, stale refs, frontmatter, common mistakes |

## Refactor Skills (1)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| quick-refactor | `.agents/skills/quick-refactor/` | `quick-refactor`, `quick refactor` | Quick, test-driven refactor. ≤ 3 files. No plan file. |

## Personal Skills (1)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| jira-log | `.local/skills/jira-log/` | `jlog` | Log time to Jira via Tempo API |
