from flask import Flask, render_template, request
import json

app = Flask(__name__)
# start sesion data
session_data ={
    "user_id": "user123",
    "session_id": "session001",
    "timestamp": "2025-09-20T14:00:00",
    "modules": [],
    "summary":{}
}

#add sequence module
sequence_module = {
    "module_name": "sequence_test",
    "questions": [
        {
            "question_id": "q1",
            "question_text": "1, 2, 5, 11,_ ,17",
            "user_answer": "14",
            "correct": True,
            "time_taken_seconds": 12.5,
            "retries": 0,
            "hesitation_seconds": 3.2
        }
    ]
}
session_data["modules"].append(sequence_module)

# add puzzle module
puzzle_module = {
    "module_name": "puzzle_test",
    "questions": [
        {
            "questions_id": "p1",
            "question_text": "arrange the numbers to complete the pattern",
            "user_answer": "solution text",
            "correct_answer": "solution text",
            "correct": True,
            "time_taken_seconds": 20.0,
            "retries": 1,
            "hesitation_seconds": 6.0
        }
    ]
}
session_data["modules"].append(puzzle_module)

# save to JSON
with open("session_data.json", "w") as f:
    json.dump(session_data, f, indent=4) 
def model_status():
    return "Model is working."

@app.route("/", methods=["GET", "POST"])
def puzzle():
    result = None
    if request.method == "POST":
        user_answer = request.form.get("answer")
        if user_answer and user_answer.strip() == "21":
            result = "correct!" 
        else:
            result = "incorrect. try again."
        return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)  

