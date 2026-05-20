from flask import Flask, request, jsonify
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

    data = request.get_json(silent=True) or {}

    print("========== SEND SMS REQUEST ==========")
    print(json.dumps(data, indent=2, ensure_ascii=False), flush=True)

    return jsonify({
        "success": True,
        "message": "SMS API READY"
    })

# ================= LINE WEBHOOK =================

@app.route("/line-webhook", methods=["POST"])
def line_webhook():

    data = request.get_json(silent=True) or {}

    # LINE OA Channel ID
    destination = data.get("destination", "UNKNOWN_DESTINATION")

    print("========== LINE WEBHOOK ==========", flush=True)
    print("DESTINATION / CHANNEL ID:", destination, flush=True)
    print(json.dumps(data, indent=2, ensure_ascii=False), flush=True)

    events = data.get("events", [])

    for event in events:

        event_type = event.get("type")
        source = event.get("source", {})
        user_id = source.get("userId", "UNKNOWN_USER")
        source_type = source.get("type", "UNKNOWN_SOURCE")

        print("---------- EVENT ----------", flush=True)
        print("CHANNEL ID:", destination, flush=True)
        print("EVENT TYPE:", event_type, flush=True)
        print("SOURCE TYPE:", source_type, flush=True)
        print("USER ID:", user_id, flush=True)

        # ===== FOLLOW =====

        if event_type == "follow":

            print("NEW FOLLOW:", user_id, flush=True)

        # ===== UNFOLLOW =====

        elif event_type == "unfollow":

            print("UNFOLLOW:", user_id, flush=True)

        # ===== MESSAGE =====

        elif event_type == "message":

            message = event.get("message", {})
            message_type = message.get("type", "UNKNOWN_MESSAGE_TYPE")
            text = message.get("text", "")

            print("MESSAGE FROM:", user_id, flush=True)
            print("MESSAGE TYPE:", message_type, flush=True)
            print("MESSAGE TEXT:", text, flush=True)

    return jsonify({
        "status": "ok",
        "destination": destination,
        "events_received": len(events)
    })

# ================= RUN =================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
