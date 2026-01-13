# task_registry.py
# Defines task sequencing and progression logic

TASK_SEQUENCE = [
    "pattern_recognition",
    "strategy_under_constraint_v1",
    # add more task IDs here later
    # "memory_01",
    # "conflict_01",
]

def get_next_task(current_task_id):
    """
    Returns the next task_id in sequence.
    If at end, returns None.
    """
    if current_task_id not in TASK_SEQUENCE:
        return None

    idx = TASK_SEQUENCE.index(current_task_id)

    if idx + 1 < len(TASK_SEQUENCE):
        return TASK_SEQUENCE[idx + 1]

    return None

