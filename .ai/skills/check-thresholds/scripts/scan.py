"""Multi-language quality threshold checker.

Supports: Python (.py), C# (.cs), PHP (.php)

Checks:
  - File line count ≤ 300
  - Function/method size ≤ 40 lines
  - Function/method param count ≤ 4

Usage:
  python scan.py [file_or_dir]     # defaults to cwd
  python scan.py --changed file1.cs file2.py  # check specific files only
"""

import os
import re
import sys
from typing import Optional

FILE_LIMIT = 300
FUNC_SIZE_LIMIT = 40
PARAM_LIMIT = 4


# ── Signature patterns ──────────────────────────────────────────────

PY_SIG = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)")

CS_SIG = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|static|virtual|override|"
    r"abstract|async|sealed|unsafe|readonly|extern|partial|new)\s+)+\s*"
    r"\S+\s+(\w+)\s*\(([^)]*)\)"
)

PHP_SIG = re.compile(
    r"^\s*(?:(?:public|private|protected|static|abstract|final)\s+)*"
    r"function\s+(\w+)\s*\(([^)]*)\)"
)


# ── Helpers ─────────────────────────────────────────────────────────


def count_params(sig: str) -> int:
    """Count non-empty params from signature substring inside parens."""
    sig = sig.strip()
    if not sig:
        return 0
    return len([p for p in sig.split(",") if p.strip()])


def _leading_ws(line: str) -> int:
    return len(line) - len(line.lstrip())


# ── Python: indent-based ────────────────────────────────────────────


def _find_py_body_start(lines: list[str], i: int, sig_indent: int) -> Optional[int]:
    """Return line index of function body start, or None if no body."""
    j = i + 1
    while j < len(lines):
        stripped = lines[j].strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("@"):
            j += 1
            continue
        if _leading_ws(lines[j]) > sig_indent:
            return j
        j += 1
        return None
    return None


def _find_py_func_end(lines: list[str], start: int, sig_indent: int) -> int:
    """Return last line index of function body before dedent."""
    func_end = start
    j = start
    while j < len(lines):
        stripped = lines[j].strip()
        if stripped and not stripped.startswith("#"):
            if _leading_ws(lines[j]) <= sig_indent:
                break
            func_end = j
        j += 1
    return func_end


def check_python(path: str) -> list[str]:
    violations = []
    with open(path, encoding="utf-8") as f:
        lines = [l.rstrip("\n\r") for l in f.readlines()]

    basename = os.path.basename(path)

    if len(lines) > FILE_LIMIT:
        violations.append(f"{basename}: file {len(lines)} lines (max {FILE_LIMIT})")

    i = 0
    while i < len(lines):
        m = PY_SIG.match(lines[i])
        if not m:
            i += 1
            continue

        name = m.group(1)
        params = count_params(m.group(2))
        if params > PARAM_LIMIT:
            violations.append(
                f"{basename}::{name}(): {params} params (max {PARAM_LIMIT})"
            )

        sig_indent = _leading_ws(lines[i])
        body_start = _find_py_body_start(lines, i, sig_indent)
        if body_start is None:
            i += 1
            continue

        func_end = _find_py_func_end(lines, body_start, sig_indent)
        size = func_end - i + 1
        if size > FUNC_SIZE_LIMIT:
            violations.append(
                f"{basename}::{name}(): {size} lines (max {FUNC_SIZE_LIMIT})"
            )
        i = func_end + 1

    return violations


# ── C# / PHP: brace-based ───────────────────────────────────────────


def _find_matching_brace(lines: list[str], start: int) -> int:
    """Return line index of matching } for the { at or after `start`."""
    depth = 0
    started = False
    for i in range(start, len(lines)):
        for ch in lines[i]:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
                if started and depth == 0:
                    return i
    return len(lines) - 1


def check_brace_lang(path: str, ext: str) -> list[str]:
    violations = []
    with open(path, encoding="utf-8") as f:
        lines = [l.rstrip("\n\r") for l in f.readlines()]

    basename = os.path.basename(path)
    pattern = CS_SIG if ext == ".cs" else PHP_SIG

    if len(lines) > FILE_LIMIT:
        violations.append(f"{basename}: file {len(lines)} lines (max {FILE_LIMIT})")

    # Find opening brace line for each signature
    for i, line in enumerate(lines):
        m = pattern.match(line)
        if not m:
            continue

        name = m.group(1)
        params = count_params(m.group(2))
        if params > PARAM_LIMIT:
            violations.append(
                f"{basename}::{name}(): {params} params (max {PARAM_LIMIT})"
            )

        # Locate opening brace (may be on same line or next line)
        brace_line = i
        while brace_line < len(lines) and "{" not in lines[brace_line]:
            brace_line += 1
        if brace_line >= len(lines):
            continue

        end_line = _find_matching_brace(lines, brace_line)
        size = end_line - i + 1
        if size > FUNC_SIZE_LIMIT:
            violations.append(
                f"{basename}::{name}(): {size} lines (max {FUNC_SIZE_LIMIT})"
            )

    return violations


# ── Dispatch ────────────────────────────────────────────────────────

CHECKERS = {
    ".py": check_python,
    ".cs": lambda p: check_brace_lang(p, ".cs"),
    ".php": lambda p: check_brace_lang(p, ".php"),
}


def check_file(path: str) -> list[str]:
    ext = os.path.splitext(path)[1].lower()
    checker = CHECKERS.get(ext)
    if checker is None:
        return []
    return checker(path)


# ── Main ────────────────────────────────────────────────────────────


def main() -> int:
    targets: list[str] = []

    if "--changed" in sys.argv:
        idx = sys.argv.index("--changed")
        targets = sys.argv[idx + 1 :]
    elif len(sys.argv) > 1:
        targets = [sys.argv[1]]
    else:
        targets = ["."]

    violations: list[str] = []
    exts = {".py", ".cs", ".php"}

    for target in targets:
        if os.path.isfile(target):
            violations.extend(check_file(target))
        elif os.path.isdir(target):
            for root, _, files in os.walk(target):
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in exts:
                        violations.extend(check_file(os.path.join(root, f)))
        else:
            print(f"Target not found: {target}", file=sys.stderr)
            return 1

    if violations:
        for v in violations:
            print(f"  ❌ {v}", file=sys.stderr)
        print(f"\n{violations.__len__()} violation(s) found.", file=sys.stderr)
        return 1

    print("✅ All thresholds met.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
