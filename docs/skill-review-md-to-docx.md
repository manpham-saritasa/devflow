# Skill Review — md-to-docx

**Skill:** `devflow/.ai/skills/md-to-docx/`
**Files:** SKILL.md, main.py, requirements.txt
**Reviewed:** 2026-05-28

## Summary

- Files: 3
- Issues: 5 (Medium: 1, Low: 4)
- Verdict: **Approved with suggestions**

## Findings

| # | Priority | File | Line | Issue | Fix |
|--|----------|------|------|-------|-----|
| 1 | Medium | `main.py` | 48–62 | `convert()` has no try/except. `markdown()`, `BeautifulSoup()`, `doc.save()` throw raw tracebacks. | Wrap in try/except with actionable messages |
| 2 | Low | `main.py` | 105–115 | `_set_cell_text` is dead code — defined but never called after `_populate_cell` was introduced. | Remove the method |
| 3 | Low | `main.py` | 157 | `_extract_lines()` re-parses HTML with `"html.parser"` while outer tree uses `"lxml"`. Wasteful + different parser behavior. | Use `node.get_text("\n")` on existing tree |
| 4 | Low | `main.py` | 95,101,145 | Private API access: `cell._tc`, `row._tr`, `paragraph._p`. Fragile across python-docx versions. No public alternative exists. | Add comment noting python-docx limitation and version tested |
| 5 | Low | `main.py` | 263 | `section_width = 6.9` hardcoded — breaks silently if page margins change in `convert()`. | Compute from `doc.sections[0].page_width` minus margins |

## Rule Checklist

| Rule | Status |
|------|--------|
| Reuse over duplication | ✅ PALETTE, helpers all shared |
| Architecture patterns | ✅ Single class, clean separation |
| Error handling | 🟡 No try/except in convert() |
| Security | ✅ No secrets, safe paths |
| Dependencies | ✅ Version-bounded, justified |
| Naming | ✅ Consistent conventions |
| SKILL.md accuracy | ✅ Docs match implementation |

## Strengths

- PALETTE mirrors `md-to-html` — single color source of truth
- `_append_inline_content` handles `<strong>`, `<a>`, `<br>` in one tree walker
- Nested lists supported via recursion
- Hyperlinks use real OOXML instead of styled text
