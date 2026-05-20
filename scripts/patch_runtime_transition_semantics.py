from pathlib import Path


SCHEMA_PATH = Path(
    "project/governance/validation/runtime_schema.py"
)


content = SCHEMA_PATH.read_text()


OLD_BLOCK = '''
class GovernanceState:
    """
    Active governance runtime state.
    """

    active_modes: List[str] = field(default_factory=list)

    authority_level: float = 1.0

    escalation_level: int = 0
'''


NEW_BLOCK = '''
class GovernanceState:
    """
    Active governance runtime state.
    """

    previous_state: str = ""

    current_state: str = "unrestricted"

    active_modes: List[str] = field(default_factory=list)

    authority_level: float = 1.0

    escalation_level: int = 0
'''


content = content.replace(
    OLD_BLOCK,
    NEW_BLOCK,
)


SCHEMA_PATH.write_text(content)

print(
    "Runtime transition semantics added."
)
