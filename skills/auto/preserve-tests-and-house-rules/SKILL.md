---
name: preserve-tests-and-house-rules
description: Use when modifying a package with existing tests and house rules like changelog, regression tests, or type hints.
---
# Preserve Tests and House Rules

1. Do not modify existing test files; add new test files only when the task allows or requires them.
2. Add tests/test_regressions.py with one test function per bug fixed, and ensure the file passes.
3. Update CHANGELOG.md under '## Unreleased' with one bullet per fix in the required format: '- fix(<function name>): <short description>'.
4. Annotate every public function's parameters and return value with type hints.
5. Run the visible test suite after changes; fix all failures before finishing.
6. Keep changes scoped to the package and required house-rule files; do not edit unrelated files.
7. If a house rule is unclear, re-read the task instruction and existing conventions inside the sandbox.