---
name: Review changes one by one
description: Show each planned change as a scrollable option list, confirm individually, execute all at once
type: review
---

You are reviewing a set of planned changes. Follow this flow:

## Step 1: Show the plan

```
## Planned Changes

| # | File | Change | Options |
|---|------|--------|---------|
| 1 | `{file}` | {what} | A: {option}, B: {option} |
| 2 | `{file}` | {what} | A: {option}, B: {option} |
```

## Step 2: Confirm each change

For each `#` in order, ask:

```
❓ Change #{N}: {file} — {what}

| Option | Action |
|--------|--------|
| A | {first option} |
| B | {second option} |
| C | Skip this change |
```

Wait for user to pick a letter before moving to the next `#`.

## Step 3: Execute all

After ALL changes confirmed, run everything at once. Do not execute one-by-one.

## Rules

- User can scroll and pick — never force sequential locked-in choices.
- If user says "go with A for all", accept and execute all.
- Never execute before final change is confirmed.
