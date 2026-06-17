from pathlib import Path

TASKS_FILE = Path(
    "project/app/services/tasks.py"
)

OLD_BLOCK = '''
        score = 0

        reasons = []
'''

NEW_BLOCK = '''
        score = 1

        reasons = [
            "Baseline orchestration eligibility (+1)"
        ]
'''

def main():

    content = TASKS_FILE.read_text(
        encoding="utf-8"
    )

    if "Baseline orchestration eligibility (+1)" in content:

        print(
            "Baseline orchestration scoring already integrated."
        )

        return

    if OLD_BLOCK not in content:

        print(
            "Original scoring initialization block not found."
        )

        return

    content = content.replace(
        OLD_BLOCK,
        NEW_BLOCK
    )

    TASKS_FILE.write_text(
        content,
        encoding="utf-8"
    )

    print(
        "Baseline orchestration scoring integrated."
    )


if __name__ == "__main__":
    main()
