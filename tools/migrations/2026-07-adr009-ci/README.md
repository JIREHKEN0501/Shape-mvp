# ADR-009 CI Migration (July 2026)

## Purpose

These utilities were used once to migrate ADR-009 compliance verification
from a runtime-log-based workflow to a deterministic CI workflow.

## Migration steps

1. Added CLI trace selection to `verify_adr009_compliance.py`
2. Created the canonical routing trace fixture
3. Updated the GitHub Actions workflow to verify against the fixture

## Status

Completed.

These scripts are retained for historical reference and are not part of the
normal application runtime.
