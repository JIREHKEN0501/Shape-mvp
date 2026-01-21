# project/app/utils/summary_validator.py

SUPPORTED_SUMMARY_VERSIONS = {"1.0"}

SUMMARY_VERSION_STATUS = {
    "1.0": "active",
    # future examples:
    # "2.0": "active",
    # "0.9": "deprecated",
}

SUPPORTED_SUMMARY_TYPES = {"cognitive", "strategy", "behavioral"}


def validate_summary_schema(summary: dict) -> tuple[bool, str | None]:
    """
    Validate a session summary against the declared schema contract.
    Returns (ok, error_message).
    """

    if not isinstance(summary, dict):
        return False, "summary must be an object"

    version = summary.get("summary_version")

    status = SUMMARY_VERSION_STATUS.get(version)
    if status is None:
        return False, f"unknown summary_version: {version}"

    if status == "retired":
        return False, f"summary_version {version} is retired"

    summary_type = summary.get("summary_type")
    if summary_type not in SUPPORTED_SUMMARY_TYPES:
        return False, f"unsupported summary_type: {summary_type}"

    data = summary.get("data")
    if not isinstance(data, dict):
        return False, "summary.data must be an object"

    # Minimal guarantees for cognitive summaries
    if summary_type == "cognitive":
        required_keys = {
            "total_questions",
            "accuracy_ratio",
            "avg_time_per_question",
            "median_time_per_question",
            "time_variance",
            "speed_accuracy_profile",
        }

        missing = required_keys - data.keys()
        if missing:
            return False, f"missing cognitive summary fields: {sorted(missing)}"

    return True, None

