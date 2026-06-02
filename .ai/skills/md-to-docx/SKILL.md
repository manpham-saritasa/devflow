---
name: md-to-docx
description: Convert Markdown files into Microsoft Word .docx files using a reusable bundled converter that preserves headings, paragraphs, lists, tables, quotes, and code blocks.
triggers:
  - "md-to-docx"
  - "to-docx"
  - "md-docx"
  - "word export"
---

# Skill: md-to-docx

## Purpose

Use this skill when the user wants to:
- Convert a Markdown file into a Microsoft Word document.
- Create a `.docx` file from notes, ADRs, specs, reports, plans, or documentation.
- Produce a shareable Word file instead of plain Markdown or HTML.
- Reuse the same conversion flow across Markdown-based docs.

This skill is specifically for:
- ADRs
- Documentation pages
- Reports
- Technical notes
- Project plans
- Internal writeups

## Output rules

- The final deliverable must be a `.docx` file.
- Keep the document structure close to the source Markdown.
- Preserve headings, paragraphs, bullet lists, numbered lists, tables, blockquotes, and code blocks when practical.
- Use readable Word-native formatting with the same color palette as the `md-to-html` skill.
- Do not use card layout in Word output.
- Do not embed secrets, personal info, or machine-local absolute paths into the output document.

## Conversion behavior

- Convert Markdown headings into Word heading styles.
- Convert Markdown paragraphs into normal Word paragraphs.
- Convert Markdown bullet and numbered lists into Word list paragraphs.
- Convert Markdown tables into Word tables.
- Reuse the `md-to-html` skill palette for headings, text, quotes, and table styling.
- Keep the Word layout simple and document-like; do not try to mimic HTML card layout.
- Make table header rows taller and vertically center the header text.
- Convert blockquotes into quote-style paragraphs when available.
- Convert code blocks into plain monospaced-style paragraphs when practical.
- Preserve section order from the source Markdown unless the user asks to restructure it.
- Keep the original meaning of the Markdown file.

## Usage

Install the parser dependencies first:

```bash
python -m pip install -r .ai/skills/md-to-docx/requirements.txt
```

If `python` is not available on Windows, use:

```bash
py.exe -m pip install -r .ai/skills/md-to-docx/requirements.txt
```

Then run the bundled converter script:

```bash
python .ai/skills/md-to-docx/scripts/main.py <input.md> [output.docx]
```

If `python` is not available on Windows, use:

```bash
py.exe .ai/skills/md-to-docx/scripts/main.py <input.md> [output.docx]
```

If `output.docx` is omitted, it writes to `<input_stem>.docx` alongside the source file.

The script handles Markdown parsing and a practical Word conversion in one pass.

## File naming

Use descriptive lowercase hyphenated filenames when creating new standalone documents, for example:
- `project-plan.docx`
- `technical-notes.docx`
- `migration-report.docx`
- `converted-document.docx`

## Notes

- This skill clones the `md-to-html` color palette into Word-native formatting.
- This skill aims for practical Word output, not pixel-perfect parity with HTML rendering.
- The generated `.docx` should be easy to read and edit in Microsoft Word.
