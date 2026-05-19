"""
Canonical governance validation constants.

This module centralizes governance threshold semantics to reduce
evaluator drift and preserve constitutional consistency.
"""

# Authority semantics

FULL_AUTHORITY_LEVEL = 1.0

HIGH_AUTHORITY_THRESHOLD = 0.85

MODERATE_AUTHORITY_THRESHOLD = 0.5

LOW_AUTHORITY_THRESHOLD = 0.25


# Evidence semantics

MINIMUM_EVIDENCE_SCORE = 0.3

SUFFICIENT_EVIDENCE_SCORE = 0.7


# Legitimacy semantics

HIGH_CONFIDENCE_THRESHOLD = 0.8

MODERATE_CONFIDENCE_THRESHOLD = 0.5

LOW_CONFIDENCE_THRESHOLD = 0.2
