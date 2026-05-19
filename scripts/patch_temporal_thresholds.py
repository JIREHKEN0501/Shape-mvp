from pathlib import Path


CONSTANTS_PATH = Path(
    "project/governance/validation/constants.py"
)


content = CONSTANTS_PATH.read_text()


TEMPORAL_CONSTANTS = '''


# =====================================
# Temporal governance thresholds
# =====================================

MAX_REEVALUATION_INTERVAL_SECONDS = 3600

MAX_GOVERNANCE_STATE_DURATION_SECONDS = 7200
'''


if "MAX_REEVALUATION_INTERVAL_SECONDS" not in content:

    content += TEMPORAL_CONSTANTS


CONSTANTS_PATH.write_text(content)

print(
    "Temporal governance thresholds added."
)
