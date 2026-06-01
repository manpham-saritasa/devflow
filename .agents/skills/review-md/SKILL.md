---
name: review-md
description: Audit markdown files (skills, plugins, agents, rules, prompts) for duplicated text, stale references, missing frontmatter, common mistakes, and structural issues. Use when user says "review md", "check md files", "audit markdown", or wants to quality-check agent instructions.
---

# Review Markdown Files

Audit all `.md` files in a target subtree for duplication and common mistakes.
Read every file, then evaluate across all check dimensions.

## Target

If user specifies a path (e.g. `.ai/plugins/refactorflow`), scope to that subtree.
If no path given, ask which subtree to review.

## Check dimensions

### 1. Duplicates

- **Within a file**: Any section, paragraph, or block that appears twice in the same file.
- **Across files**: Same heading + same body appearing in multiple files. Flag if near-identical (≥80% match).
- **Config duplication**: Same path, value, or variable defined in multiple files instead of `config.md` or `PRINCIPLES.md`.
- **Concepts**: Same idea explained in multiple skills without cross-reference. Example: "Preserve behavior" explained in 3 SKILL.md files instead of once in PRINCIPLES.md.

### 2. Frontmatter

Check every `.md` file with `---` delimiters:

- **Missing delimiters**: First line must be `---`, frontmatter must close with `---`.
- **Missing `name`**: Every SKILL.md must have `name:` matching the directory name.
- **Missing `description`**: Every SKILL.md and agent must have a description.
- **Missing `version`**: Newer skills should have `version:` field.
- **Inline YAML without delimiters**: Raw `name: value` at top of file without `---` wrapping.

### 3. Stale references

- **Dead paths**: Any file path reference (e.g. `skills/grill/SKILL.md`) where the file doesn't exist.
- **Old names**: Any reference to a renamed skill, plugin, or agent (e.g. `dev-refactor` after rename to `refactorflow`).
- **Ghost citations**: Placeholder references like `[web:306]`, `[TODO]`, `[FIXME]`, `[XXX]`.

### 4. Inconsistency

- **Pattern mismatch**: Same section (e.g. "When to use") formatted differently across sibling files.
- **Naming mismatch**: Skill name in frontmatter doesn't match directory name.
- **Version mismatch**: Different `version:` values across files in the same plugin.
- **Table of contents mismatch**: README file map doesn't match actual directory contents (missing files, extra entries, wrong order).

### 5. Config compliance

- **Hardcoded paths**: Paths like `.local/work/refactor-plan.md` that should reference `config.md` instead.
- **Missing from config**: Values referenced by multiple files but not centralized in `config.md`.
- **Config variable mismatch**: UPPER_CASE variable names used in files but not defined in `config.md`.

### 6. Cross-references

- **Orphan references**: Skill A says "use skill B", but skill B doesn't exist or has a different name.
- **Circular references**: A → B → A dependency chain.
- **Missing cross-ref**: Related skills without mutual references.

### 7. Structure

- **Empty files**: `.md` files with no content or only frontmatter.
- **Missing sections**: SKILL.md without "When to use", "Rules", or equivalent.
- **Unexpected files**: Files that don't belong in a skills/plugins/agents folder (e.g. `.DS_Store`, temp files).

### 8. Formatting

- **Mixed heading styles**: `## Section` vs `## section` vs `## Section:` in the same file.
- **Broken markdown**: Unclosed code blocks, mismatched backticks, invalid tables.
- **Long lines**: Paragraphs > 120 chars that should be wrapped.
- **Trailing whitespace**: Lines ending with spaces.

### 9. Data privacy

Flag anything that looks like real data. Skills, plugins, agents, and rules
should use placeholders — never real values.

- **Emails**: Anything matching `@` that isn't clearly a placeholder (e.g. `user@example.com` is OK, `john@realcompany.com` is not).
- **Names**: Full names that look like real people (placeholders like `John Doe`, `Jane Smith` are OK).
- **Company names**: Real company names (except in `config.md` where they may be necessary as examples).
- **API keys / tokens**: Any string matching key patterns (`sk-`, `ghp_`, `xoxb-`, `JWT`, long hex/base64 strings).
- **URLs / IPs**: Real URLs or IPs that aren't `example.com`, `localhost`, `127.0.0.1`, or similarly obvious placeholders.
- **Project names**: Internal project codenames or product names that shouldn't be public.
- **Client data**: Names, IDs, account numbers, addresses, phone numbers.
- **Secrets in code blocks**: Check code examples for accidentally pasted real values.

**Rules:**
- Flag anything suspicious. User decides if it's real.
- Placeholder patterns that are clearly fake (e.g. `test@example.com`, `abc123`, `my-token`) are fine.
- `config.md` may contain real paths relative to the repo — that's OK.
- If unsure, flag it and ask: "Real or placeholder?"

## Output format

```
## Review — [target path]

Files checked: [N]
Date: [YYYY-MM-DD]

### Duplicates

| # | Type | Location | Detail | Fix |
|---|------|----------|--------|-----|

### Frontmatter issues

| # | File | Issue | Fix |
|---|------|-------|-----|

### Stale references

| # | File | Reference | Issue | Fix |
|---|------|-----------|-------|-----|

### Inconsistency

| # | Files | Issue | Fix |
|---|-------|-------|-----|

### Config compliance

| # | File | Issue | Fix |
|---|------|-------|-----|

### Cross-references

| # | From | To | Issue | Fix |
|---|------|----|-------|-----|

### Structure

| # | File | Issue | Fix |
|---|------|-------|-----|

### Formatting

| # | File | Issue | Fix |
|---|------|-------|-----|

### Data privacy

| # | File | Pattern | Detail | Action |
|---|------|---------|--------|--------|

### Summary

- Duplicates: [N]
- Frontmatter: [N]
- Stale refs: [N]
- Inconsistency: [N]
- Config: [N]
- Cross-refs: [N]
- Structure: [N]
- Formatting: [N]
- Privacy: [N]

### Verdict

[Clean / Minor issues / Needs work]
```

## Rules

- Read every `.md` file in the target subtree before reporting.
- Don't skip dimensions. If clean, note: "No issues found."
- Sort findings within each section by severity (worst first).
- Report exact file paths and line numbers or headings.
- Flag duplicates even if they're minor — they grow over time.
