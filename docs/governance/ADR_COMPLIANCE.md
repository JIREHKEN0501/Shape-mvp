# ADR Compliance Process

## Purpose

Architectural Decisions (ADRs) are enforced automatically through
compliance verification.

Each ADR should include:

- ADR document
- Compliance verifier
- Canonical reference fixture
- GitHub Actions workflow

## Directory Convention

docs/architecture_decisions/

scripts/
    verify_adrXXX_compliance.py

tests/fixtures/

.github/workflows/

## Development Workflow

1. Implement ADR
2. Create reference fixture
3. Write verifier
4. Verify locally
5. Add CI
6. Commit
7. Tag release

## Naming Convention

ADR documents

docs/architecture_decisions/
    ADR-009-<title>.md

Compliance verifiers

scripts/
    verify_adr009_compliance.py

Reference fixtures

tests/
    fixtures/
        routing_traces/
            adr009_reference.jsonl

CI workflow

.github/workflows/
    adr009-compliance.yml

## Local Verification

Run against runtime logs

python scripts/verify_adr009_compliance.py

Run against the canonical fixture

python scripts/verify_adr009_compliance.py \
    --trace-log tests/fixtures/routing_traces/adr009_reference.jsonl

## Governance

Architectural compliance is automatically verified in CI.

Current governance tooling includes:

- ADR-009 Compliance Verification
- Canonical routing trace fixtures
- GitHub Actions enforcement
