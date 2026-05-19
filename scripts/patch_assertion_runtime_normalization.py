from pathlib import Path


ASSERTIONS_PATH = Path(
    "project/governance/validation/assertions.py"
)


content = ASSERTIONS_PATH.read_text()


IMPORT_OLD = '''
from .telemetry import telemetry_buffer
'''


IMPORT_NEW = '''
from .telemetry import telemetry_buffer

from .runtime_normalization import (
    normalize_runtime_context,
)
'''


content = content.replace(
    IMPORT_OLD,
    IMPORT_NEW,
)


OLD_FUNCTION_BLOCK = '''
def evaluate_assertion(
    invariant_id: str,
    runtime_context: Dict[str, Any],
) -> AssertionResult:
    """
    Execute a registered governance assertion.
    """

    evaluator = assertion_registry.get(
        invariant_id
    )

    if evaluator is None:
        raise ValueError(
            f"No evaluator registered for {invariant_id}"
        )

    return evaluator(runtime_context)
'''


NEW_FUNCTION_BLOCK = '''
def evaluate_assertion(
    invariant_id: str,
    runtime_context: Dict[str, Any],
) -> AssertionResult:
    """
    Execute a registered governance assertion.
    """

    evaluator = assertion_registry.get(
        invariant_id
    )

    if evaluator is None:
        raise ValueError(
            f"No evaluator registered for {invariant_id}"
        )

    normalized_context = normalize_runtime_context(
        runtime_context
    )

    return evaluator(normalized_context)
'''


content = content.replace(
    OLD_FUNCTION_BLOCK,
    NEW_FUNCTION_BLOCK,
)


ASSERTIONS_PATH.write_text(content)

print(
    "Assertion pipeline runtime normalization integrated."
)
