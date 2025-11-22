from flask import Flask, request, render_template  request, jsonify, make_response, redirect, url_for
import uuid, hashlib, json, datetime, os

app = Flask(__name__)
CONSENT_VERSION = "v1.0"
CORRECT_ANSWER = "23"  # change to whatever logic you want

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
CONSENT_LOG = os.path.join(LOG_DIR, "consent_log.jsonl")
DATA_LOG = os.path.join(LOG_DIR, "data_log.jsonl")

def append_jsonl(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()

def ip_hash(ip):
    if not ip:
        return ""
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()

@app.route("/", methods=["GET", "POST"])
def index():
    result = NONE
    User_result = ""
    participant_id = request.cookies.get("participant_id")
    if request.method == 'POST':
        # require consent (participant_id presence)
        participant_id = request.cookies.get("participant_id")
        if not participant_id:
            result = "no_consent"
        else:
            user_answer = request.form.get('answer', '').strip()
            ok = (user_answer == CORRECT_ANSWER)
            result = "correct" if ok else "wrong"
            # Log anonymized session event
            log = {
                "participant_id": participant_id,
                "timestamp": now_iso(),
                "task_id": "sequence_test_001",
                "answer": hashlib.sha256(user_answer.encode("utf-8")).hexdigest(),  # hashed to avoid storing raw answer
                "result": result,
                "model_version": "none",
            }
            append_jsonl(DATA_LOG, log)
    return render_template('index.html', result=result, user_answer=user_answer

@app.route('/consent', methods=['POST'])
def consent():
    # Client triggers consent; server will create a participant_id and write consent record
    ip = request.remote_addr or ""
    participant_id = str(uuid.uuid4())
    record = {
        "participant_id": participant_id,
        "timestamp": now_iso(),
        "consent_version": CONSENT_VERSION,
        "consent_given": True,
        "ip_hash": ip_hash(ip),
        "notes": ""
    }    
 append_jsonl(CONSENT_LOG, record)
    resp = make_response(jsonify({"ok": True, "participant_id": participant_id}))
    # set cookie for 1 year; secure flag omitted for dev, set secure=True when using HTTPS
    resp.set_cookie("participant_id", participant_id, max_age=60*60*24*365, httponly=True, samesite="Lax")
    return resp

# Simple export endpoint (authorized? — for demo it's open; secure in production)
@app.route('/export/<participant_id>', methods=['GET'])
def export(participant_id):
    # Return all data_log entries for participant (anonymized)
    results = []
    if os.path.exists(DATA_LOG):
        with open(DATA_LOG, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    j = json.loads(line)
                    if j.get("participant_id") == participant_id:
                        results.append(j)
                except:
                    pass
    return jsonify({"participant_id": participant_id, "events": results})

if __name__ == '__main__':
    app.run(debug=True)
