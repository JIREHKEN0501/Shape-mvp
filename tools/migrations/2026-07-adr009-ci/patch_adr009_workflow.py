#!/usr/bin/env python3

"""
Patch the ADR-009 GitHub Actions workflow
to use the canonical fixture.
"""

from pathlib import Path
import sys

WORKFLOW = Path(".github/workflows/adr009-compliance.yml")

if not WORKFLOW.exists():
    print("Workflow not found.")
    sys.exit(1)

text = WORKFLOW.read_text(encoding="utf-8")

old = "python scripts/verify_adr009_compliance.py"

new = (
    "python scripts/verify_adr009_compliance.py "
    "--trace-log tests/fixtures/routing_traces/adr009_reference.jsonl"
)

if old not in text:
    print("Expected workflow command not found.")
    sys.exit(1)

text = text.replace(old, new, 1)

WORKFLOW.write_text(text, encoding="utf-8")

print("Workflow updated successfully.")
