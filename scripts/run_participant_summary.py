import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from pprint import pprint

from project.app.services.analytics import (
    generate_participant_summary,
)

participant_id = (
    sys.argv[1]
    if len(sys.argv) > 1
    else"hp_7f0db588"
)

summary = generate_participant_summary(
    participant_id
)

print("\n=== PARTICIPANT SUMMARY ===\n")

pprint(summary)
