from pathlib import Path

TASKS_FILE = Path(
    "project/app/services/tasks.py"
)

OLD_FUNCTION = '''
    def task_score(task):
        score = 0
        reasons = []
'''

NEW_FUNCTION = '''
    def score_task(task):

        score = 0
        reasons = []
'''

SORT_BLOCK = '''
    # Rank tasks by adaptive score
    remaining_tasks.sort(key=task_score, reverse=True)

    # Add light randomness to avoid predictability
    top_slice = remaining_tasks[:5] if len(remaining_tasks) >= 5 else remaining_tasks

    raw_task = random.choice(top_slice)
'''

NEW_SORT_BLOCK = '''
    # =====================================
    # Explicit orchestration scoring
    # =====================================

    scored_tasks = []

    for task in remaining_tasks:

        result = score_task(task)

        scored_tasks.append({

            "task": task,

            "score": result["score"],

            "reasons": result["reasons"]
        })

    scored_tasks.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # Add light randomness to avoid predictability
    top_slice = (
        scored_tasks[:5]
        if len(scored_tasks) >= 5
        else scored_tasks
    )

    selected = random.choice(top_slice)

    raw_task = selected["task"]

    selection_score = selected["score"]

    selection_reasons = selected["reasons"]
'''

RETURN_BLOCK = '''
        task["_selection_score"] =round(score, 2)
        task["_selection_reasons"] = reasons
        return score
'''

NEW_RETURN_BLOCK = '''
        return {

            "task": task,

            "score": round(score, 2),

            "reasons": reasons
        }
'''

SELECTION_TRACE_BLOCK = '''
            selection_reasons=raw_task.get(
                "_selection_reasons",
                []
            ),
'''

NEW_SELECTION_TRACE_BLOCK = '''
            selection_reasons=selection_reasons,
'''

ROUTING_META_BLOCK = '''
            "selection_score": raw_task.get("_selection_score"),

            "selection_reasons": raw_task.get("_selection_reasons", [])
'''

NEW_ROUTING_META_BLOCK = '''
            "selection_score": selection_score,

            "selection_reasons": selection_reasons
'''

def main():

    content = TASKS_FILE.read_text(
        encoding="utf-8"
    )

    if "scored_tasks = []" in content:

        print(
            "Explicit scoring refactor already integrated."
        )

        return

    replacements = [

        (OLD_FUNCTION, NEW_FUNCTION),

        (SORT_BLOCK, NEW_SORT_BLOCK),

        (RETURN_BLOCK, NEW_RETURN_BLOCK),

        (
            SELECTION_TRACE_BLOCK,
            NEW_SELECTION_TRACE_BLOCK
        ),

        (
            ROUTING_META_BLOCK,
            NEW_ROUTING_META_BLOCK
        )
    ]

    for old, new in replacements:

        if old not in content:

            print(
                f"Required block not found:\\n{old[:80]}"
            )

            return

        content = content.replace(
            old,
            new
        )

    TASKS_FILE.write_text(
        content,
        encoding="utf-8"
    )

    print(
        "Explicit scoring refactor integrated."
    )


if __name__ == "__main__":
    main()
