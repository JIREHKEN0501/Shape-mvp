# project/app/config.py
#
# Central configuration for behavioral signal thresholds and system defaults.
# These values are intentionally separated from logic to enable:
#   - calibration without touching core logic
#   - environment-specific tuning
#   - single source of truth across modules

# ---------------------------------------------------------------------------
# Behavioral signal thresholds
# ---------------------------------------------------------------------------

# Minimum hesitation count to register as a meaningful hesitation event.
# Heuristic — subject to calibration once sufficient participant data is
# collected (recommend 50+ sessions before adjusting).
HESITATION_THRESHOLD = 4

# Minimum effective retries to flag as a retry signal.
# effective_retries = raw_retries - 1 (first click is always 1)
RETRY_THRESHOLD = 1
