---
name: deliverable-artifact-verification
description: Use when a task requires producing output files or artifacts in the sandbox workspace.
---
# Deliverable Artifact Verification

1. Read the task instruction and only inspect files inside the sandbox/workspace; do not search for hidden graders or external files.
2. Identify every required output artifact and its exact path, schema, header, and format before coding.
3. Write each required artifact to the workspace; do not leave outputs only in memory or stdout.
4. Normalize values to the specified canonical forms: UTC timestamps, categorical spellings, integer minor units for money, and required sort order.
5. Deduplicate and filter rows/records exactly as specified; include only records with known required fields.
6. Include any required meta block with the exact keys and values.
7. After writing, verify each path exists, is non-empty, and matches the required schema/header; re-open and validate the content.
8. If a required artifact is missing or malformed, fix and re-verify before finishing.