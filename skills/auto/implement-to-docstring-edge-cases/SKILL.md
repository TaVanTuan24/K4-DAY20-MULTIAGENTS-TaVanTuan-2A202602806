---
name: implement-to-docstring-edge-cases
description: Use when implementing or fixing functions that must match docstrings/specs and pass visible tests.
---
# Implement to Docstring and Edge Cases

1. Read each function's docstring and the task spec; treat them as the source of truth for behavior, ordering, and formatting.
2. Handle all documented input formats, including currency symbols, thousands separators, parentheses for negatives, and missing decimals.
3. Use the specified rounding mode (e.g., half-up) and avoid binary floating-point artifacts by using Decimal or integer arithmetic.
4. Match docstring ordering, case, tie-breaking, and CSV quoting/escaping exactly.
5. Return the documented type; do not return error sentinels or exception objects.
6. Run the visible test suite and targeted edge-case checks after each fix; fix failures before moving on.
7. When a caller expects a value, ensure the function returns that value or raises a clear exception instead of silently returning an error object.