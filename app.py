from flask import Flask, request, jsonify, redirect
import json
import os

app = Flask(__name__)

# ================= HOME =================

@app.route("/")
def home():
    return "OhDude CRM Core Running!"

# ================= HEALTH CHECK =================

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "ohdude-crm-core"
    })

# ================= SEND SMS =================

@app.route("/send-sms", methods=["POST"])
def send_sms():

    data = request.json

    print("SEND SMS REQUEST")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    return jsonify({
        "success": True,
        "message": "SMS API READY"
    })

# ================= LINE WEBHOOK =================

@app.route("/line-webhook", methods=["POST"])
def line_webhook():

    data = request.json

    print("========== LINE WEBHOOK ==========")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    events = data.get("events", [])

    for event in events:

        event_type = event.get("type")

        # ===== FOLLOW =====

        if event_type == "follow":

            user_id = event.get("source", {}).get("userId")

            print("NEW FOLLOW:", user_id)

        # ===== UNFOLLOW =====

        elif event_type == "unfollow":

            user_id = event.get("source", {}).get("userId")

            print("UNFOLLOW:", user_id)

        # ===== MESSAGE =====

        elif event_type == "message":

            user_id = event.get("source", {}).get("userId")

            print("MESSAGE FROM:", user_id)

    return jsonify({
        "status": "ok"
    })

# ================= RUN =================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
