from pathlib import Path

TARGET_FILE = Path(
    "project/app/services/routing/routing_history_loader.py"
)

OLD_BLOCK = '''
                trace = entry.get(
                    "trace",
                    {}
                )

                matching_entries.append(trace)
'''

NEW_BLOCK = '''
                trace = entry.get(
                    "trace",
                    {}
                )

                health = entry.get(
                    "health",
                    {}
                )

                matching_entries.append({

                    "trace": trace,

                    "health": health
                })
'''

def main():

    content = TARGET_FILE.read_text(
        encoding="utf-8"
    )

    if '"health": health' in content:

        print(
            "Health-aware history loading already integrated."
        )

        return

    if OLD_BLOCK not in content:

        print("Target history block not found.")

        return

    updated = content.replace(
        OLD_BLOCK,
        NEW_BLOCK
    )

    TARGET_FILE.write_text(
        updated,
        encoding="utf-8"
    )

    print(
        "Health-aware orchestration history loading integrated."
    )


if __name__ == "__main__":
    main()
