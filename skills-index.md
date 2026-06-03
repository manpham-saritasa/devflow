# Skill Index

30+ skills available. LLM reads this once to discover all capabilities.

## Agents (2)

| Agent | Path | Description |
|-------|------|-------------|
| devflow | `.ai/agents/devflow.md` | Auto-drives full devflow pipeline: start → plan → code → review → ship → finish |
| refflow | `.ai/agents/refflow.md` | Auto-drives full refactor flow: plan + self-grill → execute → verify |

## Devflow Plugin (11)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| dev-start | `.ai/plugins/devflow/skills/1.dev-start/` | `dev-start`, `devstart` | Create gitflow branch for Jira task |
| dev-plan | `.ai/plugins/devflow/skills/2.dev-plan/` | `dev-plan`, `devplan` | Create execution plan with self-grill from task evidence |
| dev-code | `.ai/plugins/devflow/skills/3.dev-code/` | `dev-code`, `devcode` | Implement planned changes, write changelog |
| dev-review | `.ai/plugins/devflow/skills/4.dev-review/` | `dev-review`, `devreview` | Review code against plan + changelog |
| dev-ship | `.ai/plugins/devflow/skills/5.dev-ship-pr-jira/` | `dev-ship`, `devship` | Create PR + comment Jira + generate reports |
| dev-fix-pr | `.ai/plugins/devflow/skills/6.dev-fix-pr/` | `dev-fix-pr`, `devfixpr` | Fix PR review comments |
| dev-finish | `.ai/plugins/devflow/skills/7.dev-finish/` | `dev-finish`, `devfinish` | Merge PR, delete branch, cleanup |
| dev-adr | `.ai/plugins/devflow/skills/8.dev-adr/` | `dev-adr`, `adr` | Create Architecture Decision Record |
| dev-commit | `.ai/plugins/devflow/skills/dev-commit/` | `dev-commit`, `devcommit` | Stage + commit in related groups |
| dev-get | `.ai/plugins/devflow/skills/dev-get/` | `dev-get`, `devget` | Pull Jira issue into task folder |
| dev-push | `.ai/plugins/devflow/skills/dev-push/` | `dev-push` | Push current branch to origin |

## Jiraflow Plugin (10)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| jira-close | `.ai/plugins/jiraflow/skills/jira-close/` | `jclose` | Close tasks by key, list, or release URL |
| jira-comment | `.ai/plugins/jiraflow/skills/jira-comment/` | `jira-comment`, `jcomment` | Post comment to Jira issue |
| release-list | `.ai/plugins/jiraflow/skills/release-list/` | `rlist` | List releases in a Jira project |
| jira-mine | `.ai/plugins/jiraflow/skills/jira-mine/` | `jtask` | List assigned tasks by status group |
| jira-move | `.ai/plugins/jiraflow/skills/jira-move/` | `jmove` | Move tasks through pipeline milestones |
| jira-urgent | `.ai/plugins/jiraflow/skills/jira-urgent/` | `jurgent` | Find comments where team is waiting on you |
| release-add | `.ai/plugins/jiraflow/skills/release-add/` | `radd` | Add tasks to Jira release version |
| release-complete | `.ai/plugins/jiraflow/skills/release-complete/` | `rcomplete` | Mark a JIRA release as Released |
| release-rename | `.ai/plugins/jiraflow/skills/release-rename/` | `rrename` | Update the name of a JIRA release |
| release-note | `.ai/plugins/jiraflow/skills/release-note/` | `rnote` | Generate client-friendly release notes |

## Githubflow Plugin (4)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| gh-create-pr | `.ai/plugins/githubflow/skills/gh-create-pr/` | `create-pr` | Create or reuse GitHub pull request |
| gh-fix-pr | `.ai/plugins/githubflow/skills/gh-fix-pr/` | — | Fix PR review comments programmatically |
| gh-release | `.ai/plugins/githubflow/skills/gh-release/` | `release-candidates`, `release notes` | List PRs pending release |
| gh-review-pr | `.ai/plugins/githubflow/skills/gh-review-pr/` | `review-pr`, `reviewpr` | Review any PR across 11 dimensions with deep git blame |

## Refflow Plugin (5)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| ref-plan | `.ai/plugins/refflow/skills/1.ref-plan/` | `refactor`, `plan` | Diagnose friction, write plan, self-grill built-in |
| ref-structure | `.ai/plugins/refflow/skills/2.ref-structure/` | — (routed) | Fix boundaries, ownership, layout |
| ref-api | `.ai/plugins/refflow/skills/3.ref-api/` | — (routed) | Redesign contracts with migration planning |
| ref-simplify | `.ai/plugins/refflow/skills/4.ref-simplify/` | — (routed) | Reduce local complexity, nesting, naming |
| ref-verify | `.ai/plugins/refflow/skills/5.ref-verify/` | `verify` | Verify against original specs + quality |

## Interview Skills (1)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| grill-me | `.ai/skills/grill-me/` | `grill me`, `grill this` | Auto-triggers on "should I..." and "why..." — pressure-test any decision |

## Communication Skills (2)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| caveman | `.ai/skills/matt-pocock/caveman/` | `caveman` | Ultra-compressed communication mode |
| handoff | `.ai/skills/matt-pocock/handoff/` | `handoff` | Create handoff doc for another agent |

## Conversion Skills (3)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| md-to-html | `.ai/skills/md-to-html/` | `md-to-html` | Convert Markdown to standalone HTML |
| md-to-docx | `.ai/skills/md-to-docx/` | `md-to-docx` | Convert Markdown to Word document |
| md-view | `.ai/skills/md-view/` | `md-view`, `view md`, `preview md` | Browser-based Markdown preview, no conversion |

## Review Skills (2)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| review-design | `.agents/skills/review-design/` | `review design`, `audit` | Review plugins/skills/workflows across 13 dimensions |
| review-md | `.agents/skills/review-md/` | `review md`, `check md`, `audit markdown` | Audit markdown files for duplicates, stale refs, common mistakes |

## Reporting Skills (1)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| change-report | `.ai/skills/change-report/` | `change report`, `creport` | Auto-detecting change report — preview before, audit after |

## Refactor Skills (1)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| quick-refactor | `.agents/skills/quick-refactor/` | `quick-refactor`, `quick refactor` | Quick, test-driven refactor. ≤ 3 files. No plan file. |

## Personal Skills (1)

| Skill | Path | Triggers | Description |
|-------|------|----------|-------------|
| jira-log | `.local/skills/jira-log/` | `jlog` | Log time to Jira via Tempo API |
