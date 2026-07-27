#!/usr/bin/env python3

"""
Patch verify_adr009_compliance.py so that the routing trace
log can be supplied on the command line.

Creates a timestamp-free .bak backup before modifying.
"""

from pathlib import Path
import shutil
import sys

VERIFIER = Path("scripts/verify_adr009_compliance.py")

if not VERIFIER.exists():
    print("Verifier not found.")
    sys.exit(1)

backup = VERIFIER.with_suffix(".py.bak")
shutil.copy2(VERIFIER, backup)

text = VERIFIER.read_text(encoding="utf-8")

if "import argparse" not in text:
    text = text.replace(
        "import json\n",
        "import json\nimport argparse\n",
        1,
    )

old = 'ROUTING_TRACE_LOG = Path("logs/routing_trace_log.jsonl")'

new = '''
parser = argparse.ArgumentParser(
    description="Verify ADR-009 routing trace compliance."
)

parser.add_argument(
    "--trace-log",
    default="logs/routing_trace_log.jsonl",
    help="Path to routing trace JSONL file.",
)

args = parser.parse_args()

ROUTING_TRACE_LOG = Path(args.trace_log)
'''.strip()

if old not in text:
    print("Expected routing trace declaration not found.")
    sys.exit(1)

text = text.replace(old, new, 1)

VERIFIER.write_text(text, encoding="utf-8")

print("Verifier successfully patched.")
print(f"Backup written to: {backup}")
