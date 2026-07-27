#!/usr/bin/env python3

"""
Create the canonical ADR-009 routing trace fixture
used by GitHub Actions.

Copies the verified routing traces into
tests/fixtures/routing_traces/.
"""

from pathlib import Path
import shutil
import sys

SOURCE = Path("logs/routing_trace_log.jsonl")
DEST_DIR = Path("tests/fixtures/routing_traces")
DEST = DEST_DIR / "adr009_reference.jsonl"

if not SOURCE.exists():
    print(f"Source file not found: {SOURCE}")
    sys.exit(1)

DEST_DIR.mkdir(parents=True, exist_ok=True)

shutil.copy2(SOURCE, DEST)

print("Reference fixture created.")
print(f"Source : {SOURCE}")
print(f"Target : {DEST}")
