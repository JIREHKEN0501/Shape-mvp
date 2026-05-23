from dataclasses import dataclass, field
from typing import List

from .governance_envelope import (
    GovernanceEnvelope,
)

@dataclass(frozen=True)
class GovernanceContinuityRecord:
    """
    Replay-safe constitutional continuity record.

    Represents sequential governance evolution
    while preserving reconstruction-safe
    constitutional semantics.
    """

    continuity_id: str

    predecessor_continuity_id: str | None

    governance_envelope: GovernanceEnvelope

    transition_explanation: str

    topology_transition: str

    reevaluation_continuity: bool

    unresolved_ambiguities: List[str] = field(
        default_factory=list
    )

    continuity_timestamp: str = ""

@dataclass(frozen=True)
class GovernanceContinuityTimeline:
    """
    Canonical replay-safe governance continuity
    timeline preserving sequential constitutional
    evolution.
    """

    timeline_id: str

    continuity_records: List[
        GovernanceContinuityRecord
    ] = field(default_factory=list)

    replay_safe: bool = True


def validate_continuity_append(
    timeline: GovernanceContinuityTimeline,

    record: GovernanceContinuityRecord,

) -> List[str]:
    """
    Validate governance continuity append
    operation before timeline extension.

    Returns replay-safety and continuity
    violations preventing safe append.
    """

    violations: List[str] = []

    existing_ids = {
        continuity_record.continuity_id

        for continuity_record in (
            timeline.continuity_records
        )
    }

    if record.continuity_id in existing_ids:

        violations.append(
            "continuity_id already exists "
            "in timeline"
        )

    if not record.transition_explanation.strip():

        violations.append(
            "transition_explanation required"
        )

    if not timeline.continuity_records:

        if (
            record.predecessor_continuity_id
            is not None
        ):

            violations.append(
                "genesis continuity record "
                "cannot define predecessor"
            )

        return violations

    latest_record = (
        timeline.continuity_records[-1]
    )

    if (
        record.predecessor_continuity_id
        != latest_record.continuity_id
    ):

        violations.append(
            "predecessor_continuity_id "
            "does not match latest "
            "continuity record"
        )

    return violations

def append_continuity_record(
    timeline: GovernanceContinuityTimeline,

    record: GovernanceContinuityRecord,

) -> GovernanceContinuityTimeline:
    """
    Immutably append validated governance
    continuity record into replay-safe
    constitutional continuity timeline.

    Never mutates existing timeline state.
    """

    violations = validate_continuity_append(
        timeline,
        record,
    )

    if violations:

        raise ValueError(
            "Continuity append invalid: "
            + "; ".join(violations)
        )

    return GovernanceContinuityTimeline(
        timeline_id=timeline.timeline_id,

        continuity_records=[
            *timeline.continuity_records,
            record,
        ],

        replay_safe=timeline.replay_safe,
    )

def validate_reconstruction_integrity(
    timeline: GovernanceContinuityTimeline,
) -> List[str]:
    """
    Validate replay-safe continuity reconstruction
    integrity across governance timeline.

    Ensures constitutional continuity chain
    remains sequentially reconstructable.
    """

    violations: List[str] = []

    if not timeline.continuity_records:

        return violations

    continuity_index = {
        record.continuity_id: record

        for record in (
            timeline.continuity_records
        )
    }

    genesis_record = (
        timeline.continuity_records[0]
    )

    if (
        genesis_record.predecessor_continuity_id
        is not None
    ):

        violations.append(
            "genesis continuity record "
            "cannot define predecessor"
        )

    for index, record in enumerate(
        timeline.continuity_records
    ):

        if index == 0:
            continue

        predecessor_id = (
            record.predecessor_continuity_id
        )

        if predecessor_id is None:

            violations.append(
                f"{record.continuity_id} "
                "missing predecessor "
                "continuity reference"
            )

            continue

        if predecessor_id not in continuity_index:

            violations.append(
                f"{record.continuity_id} "
                "references unknown "
                "predecessor continuity"
            )

            continue

        expected_predecessor = (
            timeline.continuity_records[
                index - 1
            ].continuity_id
        )

        if predecessor_id != expected_predecessor:

            violations.append(
                f"{record.continuity_id} "
                "breaks sequential "
                "continuity ordering"
            )

    return violations
