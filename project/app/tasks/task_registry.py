# project/app/tasks/task_registry.py

TASKS = [
    {
        "id": "pattern_recognition",
        "type": "cognitive",
        "template": "tasks/pattern_recognition.html",
        "next": "sequence_test",
    },
    {
        "id": "sequence_test",
        "type": "cognitive",
        "template": "index.html",
        "next": None,
    },
]

def get_task(task_id):
    for task in TASKS:
        if task["id"] == task_id:
            return task
    return None
