## Jira Report (non-technical)

# [RMASUP-2145 — Adjust letter and word spacing](https://github.com/saritasa-nest/rma-mobile/pull/1429)

## Fixed
** - PDF Export - Fixed PDF text rendering spacing.**
- Root cause: Letter and word spacing values in PDF export were set to zero/normal, causing misaligned text in exported documents.
- Resolution: Applied correct spacing values to letter and word spacing in the PDF export styling, restoring proper text alignment.

## Testers
- Start here: Open any Master Form Review, then export to PDF.
- Preconditions: A submitted master form with text content.
- How to verify: The exported PDF should display text with correct character and word spacing — no overlapping or excessive gaps between letters or words.
- Known limitation: Spacing values are tuned for jsPDF/html2canvas exports; results may vary if the PDF export engine changes.

## Notes
- No product behavior change in the app — UI is unaffected. PDF export styling is scoped to the export process only.

---

## PR Report (technical)

# [RMASUP-2145 — Adjust PDF text spacing](https://github.com/saritasa-nest/rma-mobile/pull/1429)

## Goal
- Fix misaligned text in exported PDFs from the Master Form Review page, caused by incorrect letter-spacing and word-spacing CSS values.

## Fixed
** - PDF Export - Fixed PDF text rendering via CSS spacing constants.**
- Root cause: PDF export injected `letter-spacing: 0px` and `word-spacing: normal` into the cloned document, producing misaligned text in generated PDFs.
- Resolution: Replaced zero/normal values with tuned `em`-based measurements (`0.0275em` letter-spacing, `0.01em` word-spacing) and extracted them into named constants (`PDF_EXPORT_LETTER_SPACING`, `PDF_EXPORT_WORD_SPACING`).

## Key decisions
- Used `em` units for spacing — Why: `em` scales relative to font-size, providing consistent text alignment across different font sizes and platforms.
- Extracted values into named constants — Why: Makes the tuned values explicit, documented, and easier to adjust in the future without hunting through injected CSS strings.
- Scoped styling to `html2canvas.onclone` only — Why: Ensures the PDF export CSS never leaks into the live UI rendered by the browser.

## Testing
- Verified: Code reviewed and approved. Constants are documented with inline comments explaining the rationale.
- Not verified: End-to-end PDF visual comparison not confirmed from PR evidence.

## Related areas
- PDF export (jsPDF / html2canvas)
- Master Form Review (`master-form-review.component.ts`)

## Future reuse guidance
- Safe to copy: YES
- Reusable pattern: Extracting tuned CSS values into named constants with documentation comments, then referencing them in injected `onclone` styles for PDF export.
- Caveat: Values are specific to this project's font setup. Verify spacing visually when copying to a different project or when font family changes.
