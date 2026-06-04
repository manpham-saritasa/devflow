"""Check Python files against coding.ts quality thresholds. Returns 0 if clean."""

import ast
import os
import sys

FILE_LIMIT = 300
FUNC_SIZE_LIMIT = 40
PARAM_LIMIT = 4


def check_file(path: str) -> list[str]:
    violations: list[str] = []
    with open(path, encoding="utf-8") as f:
        src = f.read()
    lines = src.splitlines()
    tree = ast.parse(src)
    basename = os.path.basename(path)

    if len(lines) > FILE_LIMIT:
        violations.append(f"{basename}: file {len(lines)} lines (max {FILE_LIMIT})")

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", node.lineno)
            size = end - node.lineno + 1
            argc = len(node.args.args)
            if size > FUNC_SIZE_LIMIT:
                violations.append(
                    f"{basename}::{node.name}(): {size} lines (max {FUNC_SIZE_LIMIT})"
                )
            if argc > PARAM_LIMIT:
                violations.append(
                    f"{basename}::{node.name}(): {argc} params (max {PARAM_LIMIT})"
                )
    return violations


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    violations: list[str] = []

    if os.path.isfile(target):
        violations = check_file(target)
    else:
        for root, _, files in os.walk(target):
            for f in files:
                if f.endswith(".py"):
                    violations.extend(check_file(os.path.join(root, f)))

    if violations:
        for v in violations:
            print(v, file=sys.stderr)
        return 1

    print("All thresholds met.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
