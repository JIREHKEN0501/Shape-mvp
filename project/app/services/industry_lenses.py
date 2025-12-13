"""
Industry interpretation lenses for HumanOS.

These functions translate neutral performance summaries into
contextual, non-diagnostic insights for different domains.
They respect system confidence and data sufficiency.
"""


def education_lens(summary: dict) -> dict:
    confidence = summary.get("confidence", {})
    confidence_level = confidence.get("confidence_level", "unknown")
    sufficient = confidence.get("data_sufficiency", False)

    key_observations = [
        "Accuracy reflects current mastery level.",
        "Response speed may indicate confidence or learning style.",
    ]

    recommended_focus = [
        "Reinforce lower-performing categories.",
        "Gradually increase difficulty where accuracy is strong.",
    ]

    if not sufficient:
        key_observations.append(
            "Limited data available; learning patterns may not yet be stable."
        )
        recommended_focus.insert(
            0,
            "Collect more task attempts before drawing strong conclusions."
        )

    return {
        "context": "Learning & skill development",
        "key_observations": key_observations,
        "recommended_focus": recommended_focus,
        "confidence_context": confidence_level,
        "disclaimer": (
            "This is not a measure of intelligence or potential, "
            "only current task performance."
        ),
    }


def hr_lens(summary: dict) -> dict:
    confidence = summary.get("confidence", {})
    confidence_level = confidence.get("confidence_level", "unknown")
    sufficient = confidence.get("data_sufficiency", False)

    key_observations = [
        "Task accuracy reflects reliability under structured conditions.",
        "Latency patterns may reflect decision-making style.",
    ]

    recommended_focus = [
        "Balance speed and accuracy based on role demands.",
        "Avoid single-task conclusions; look for trends.",
    ]

    if not sufficient:
        key_observations.append(
            "Observed tendencies are preliminary and may change with more data."
        )

    return {
        "context": "Workplace performance tendencies",
        "key_observations": key_observations,
        "recommended_focus": recommended_focus,
        "confidence_context": confidence_level,
        "disclaimer": (
            "Not a hiring decision tool. Should be combined with interviews "
            "and human judgment."
        ),
    }


def healthcare_lens(summary: dict) -> dict:
    confidence = summary.get("confidence", {})
    confidence_level = confidence.get("confidence_level", "unknown")
    sufficient = confidence.get("data_sufficiency", False)

    key_observations = [
        "Performance reflects task engagement, not medical status.",
        "Variability may indicate fatigue or task difficulty.",
    ]

    recommended_focus = [
        "Monitor changes over time rather than single sessions.",
        "Use alongside professional evaluation if needed.",
    ]

    if not sufficient:
        key_observations.append(
            "Data volume is insufficient for longitudinal interpretation."
        )

    return {
        "context": "Cognitive engagement signals",
        "key_observations": key_observations,
        "recommended_focus": recommended_focus,
        "confidence_context": confidence_level,
        "disclaimer": (
            "This system does not diagnose or assess medical or psychological conditions."
        ),
    }


def security_lens(summary: dict) -> dict:
    confidence = summary.get("confidence", {})
    confidence_level = confidence.get("confidence_level", "unknown")
    sufficient = confidence.get("data_sufficiency", False)

    key_observations = [
        "Accuracy under time pressure is critical in high-stakes roles.",
        "Inconsistencies may indicate stress sensitivity.",
    ]

    recommended_focus = [
        "Train under varied difficulty and time constraints.",
        "Avoid using results as sole risk indicators.",
    ]

    if not sufficient:
        recommended_focus.insert(
            0,
            "Avoid operational conclusions until consistent performance data is available."
        )

    return {
        "context": "Operational readiness signals",
        "key_observations": key_observations,
        "recommended_focus": recommended_focus,
        "confidence_context": confidence_level,
        "disclaimer": (
            "This does not predict real-world behavior or intent."
        ),
    }


LENSES = {
    "education": education_lens,
    "hr": hr_lens,
    "healthcare": healthcare_lens,
    "security": security_lens,
}


def apply_industry_lens(summary: dict, lens: str) -> dict:
    fn = LENSES.get(lens)
    if not fn:
        return {
            "context": "Generic",
            "key_observations": [],
            "recommended_focus": [],
            "confidence_context": "unknown",
            "disclaimer": "No industry lens applied.",
        }
    return fn(summary)

