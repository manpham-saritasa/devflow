# Table Cell List Sample

**Purpose:** Visual check for bullet-like table cells
**Date:** 2026-05-24

***

## 1. Expected Behavior

This sample checks that bullet-like lines inside table cells become real HTML lists instead of plain text with `<br>` separators.

| Area | Details | Notes |
| --- | --- | --- |
| Features | - First item <br> - Second item <br> - Third item | Should become a real unordered list in HTML. |
| Mixed bullets | * Alpha <br> * Beta <br> * Gamma | Star bullets should also become a real unordered list. |
| Plain text | Single line only | Should stay normal text, not a list. |

## 2. Visual Check Notes

Look at the generated HTML table cells:

- `Features` should show a real `<ul>`.
- `Mixed bullets` should show a real `<ul>`.
- `Plain text` should remain plain text.
