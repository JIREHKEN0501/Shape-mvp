from project.governance.validation.governance_envelope import (
    GovernanceEnvelope,
)

from project.governance.validation.governance_timeline import (
    GovernanceContinuityRecord,
    GovernanceContinuityTimeline,
    append_continuity_record,
    validate_reconstruction_integrity,
)

governance_envelope = GovernanceEnvelope(
    governance_status="stable",

    topology_integrity="stable",

    authority_ceiling=0.5,

    reevaluation_required=True,

    arbitration_active=False,
)

timeline = GovernanceContinuityTimeline(
    timeline_id="timeline_alpha"
)

genesis_record = GovernanceContinuityRecord(
    continuity_id="continuity_001",

    predecessor_continuity_id=None,

    governance_envelope=governance_envelope,

    transition_explanation=(
        "Initial constitutional stabilization."
    ),

    topology_transition=(
        "initialization"
    ),

    reevaluation_continuity=True,

    unresolved_ambiguities=[
        "baseline legitimacy still evolving"
    ],

    continuity_timestamp=(
        "2026-05-23T21:00:00Z"
    ),
)

timeline = append_continuity_record(
    timeline,
    genesis_record,
)

second_record = GovernanceContinuityRecord(
    continuity_id="continuity_002",

    predecessor_continuity_id=(
        "continuity_001"
    ),

    governance_envelope=governance_envelope,

    transition_explanation=(
        "Reevaluation continuity preserved "
        "during bounded recovery."
    ),

    topology_transition=(
        "stabilization_to_rehabilitation"
    ),

    reevaluation_continuity=True,

    unresolved_ambiguities=[
        "rehabilitation remains constrained"
    ],

    continuity_timestamp=(
        "2026-05-23T22:00:00Z"
    ),
)

timeline = append_continuity_record(
    timeline,
    second_record,
)

print("\n=== GOVERNANCE TIMELINE ===\n")

print(
    "timeline_id:",
    timeline.timeline_id,
)

print(
    "record_count:",
    len(timeline.continuity_records),
)

print(
    "replay_safe:",
    timeline.replay_safe,
)

print("\n=== CONTINUITY RECORDS ===\n")

for record in timeline.continuity_records:

    print(
        "continuity_id:",
        record.continuity_id,
    )

    print(
        "predecessor:",
        record.predecessor_continuity_id,
    )

    print(
        "transition_explanation:",
        record.transition_explanation,
    )

    print(
        "topology_transition:",
        record.topology_transition,
    )

    print(
        "timestamp:",
        record.continuity_timestamp,
    )

    print("---")

invalid_record = GovernanceContinuityRecord(
    continuity_id="continuity_003",

    predecessor_continuity_id=(
        "invalid_predecessor"
    ),

    governance_envelope=governance_envelope,

    transition_explanation=(
        "Invalid continuity append."
    ),

    topology_transition="invalid_transition",

    reevaluation_continuity=True,
)

try:

    append_continuity_record(
        timeline,
        invalid_record,
    )

except ValueError as error:

    print(
        "\n=== INVALID APPEND DETECTED ===\n"
    )

    print(error)

print(
    "\n=== RECONSTRUCTION VALIDATION ===\n"
)

reconstruction_violations = (
    validate_reconstruction_integrity(
        timeline
    )
)

print(
    "reconstruction_violations:",
    reconstruction_violations,
)

broken_record = GovernanceContinuityRecord(
    continuity_id="continuity_999",

    predecessor_continuity_id=(
        "missing_continuity"
    ),

    governance_envelope=governance_envelope,

    transition_explanation=(
        "Broken reconstruction lineage."
    ),

    topology_transition="invalid_transition",

    reevaluation_continuity=True,
)

broken_timeline = (
    GovernanceContinuityTimeline(
        timeline_id="broken_timeline",

        continuity_records=[
            genesis_record,
            broken_record,
        ],
    )
)

print(
    "\n=== BROKEN RECONSTRUCTION ===\n"
)

broken_violations = (
    validate_reconstruction_integrity(
        broken_timeline
    )
)

print(
    "broken_reconstruction_violations:",
    broken_violations,
)


