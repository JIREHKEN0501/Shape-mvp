from pathlib import Path


SCHEMA_PATH = Path(
    "project/governance/validation/runtime_schema.py"
)


content = SCHEMA_PATH.read_text()


INSERT_AFTER = '''
class GovernanceTrace:
'''


TEMPORAL_BLOCK = '''
@dataclass
class TemporalGovernanceState:
    """
    Temporal governance reevaluation state.

    Tracks governance persistence timing and
    reevaluation sensitivity semantics.
    """

    governance_state_entered_at: str = ""

    last_evaluation_at: str = ""

    reevaluation_required: bool = False


@dataclass
class GovernanceTrace:
'''


if "class TemporalGovernanceState" not in content:

    content = content.replace(
        INSERT_AFTER,
        TEMPORAL_BLOCK,
    )


OLD_RUNTIME_BLOCK = '''
    governance_trace: GovernanceTrace = field(
        default_factory=GovernanceTrace
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )
'''


NEW_RUNTIME_BLOCK = '''
    governance_trace: GovernanceTrace = field(
        default_factory=GovernanceTrace
    )

    temporal_state: TemporalGovernanceState = field(
        default_factory=TemporalGovernanceState
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )
'''


content = content.replace(
    OLD_RUNTIME_BLOCK,
    NEW_RUNTIME_BLOCK,
)


SCHEMA_PATH.write_text(content)

print(
    "Temporal governance runtime schema added."
)
