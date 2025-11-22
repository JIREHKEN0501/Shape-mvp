from flask import Flask, request, render_template
import main

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def puzzle():
    """
    handles the main puzzle route.
    always returns a response whether GET or POST.
    """
    correct_answer = "17"  # sequence:1, 2, 5, 11, 17
    message = ""

    if request.method == "POST":
        user_answer = request.form.get("answer", "").strip()
        if user_answer == correct_answer:
            message = "Correct!"
        else:
            message = "Try again."
    
    return render_template("puzzle.html", message=message)

@app.route("/second", methods=["GET", "POST"])
def second_puzzle():
    correct_answer = "24"
    message = ""
    if request.method == "POST":
        user_answer = request.form.get("answer", "").strip()
        if user_answer == correct_answer:
            message = "Correct!"
        else:
            message = "Try again."
    return render_template("second_puzzle.html", message=message) 

@app.route('/status')
def status():
    return main.model_status()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Find the Missing Shape MVP is running"
@app.route('/status')
def status():
    return main.model_status()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
