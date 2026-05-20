from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# ================= OA MAP =================

OA_MAP = {
    "Uedddaf9295467c78e43a7a0eb8c9f849": "Oh Dude Shop",
    "U9d1886f9671b75880c75afaaf94bc1d7": "OhDude",
    "Ue0895a039c34300edb5bc9a650de46f5": "Oh Dude มาแล้วค้าบบ",
    "Ua5c3d239ec2f5aa61d44a285445303c2": "OH DUDE YT",
    "U6b3d04f7c8ec91856f43f82f4c9ba378": "OH DUDE IG",
    "U937d255095b540376376ab89b167f67d": "OH DUDE V1",
    "Uc52c930ca257b5ef418c74874fecc5de": "OH DUDE"
}

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

    print("========== SEND SMS REQUEST ==========", flush=True)
    print(json.dumps(data, indent=2, ensure_ascii=False), flush=True)

    return jsonify({
        "success": True,
        "message": "SMS API READY"
    })

# ================= LINE WEBHOOK =================

@app.route("/line-webhook", methods=["POST"])
def line_webhook():

    data = request.get_json(silent=True) or {}

    destination = data.get("destination", "UNKNOWN_DESTINATION")
    channel_name = OA_MAP.get(destination, "UNKNOWN_OA")

    print("========== LINE WEBHOOK ==========", flush=True)
    print("CHANNEL NAME:", channel_name, flush=True)
    print("DESTINATION / CHANNEL ID:", destination, flush=True)
    print(json.dumps(data, indent=2, ensure_ascii=False), flush=True)

    events = data.get("events", [])

    for event in events:

        event_type = event.get("type")
        source = event.get("source", {})
        user_id = source.get("userId", "UNKNOWN_USER")
        source_type = source.get("type", "UNKNOWN_SOURCE")

        print("---------- EVENT ----------", flush=True)
        print("CHANNEL NAME:", channel_name, flush=True)
        print("CHANNEL ID:", destination, flush=True)
        print("EVENT TYPE:", event_type, flush=True)
        print("SOURCE TYPE:", source_type, flush=True)
        print("USER ID:", user_id, flush=True)

        if event_type == "follow":

            print("NEW FOLLOW:", user_id, flush=True)

        elif event_type == "unfollow":

            print("UNFOLLOW:", user_id, flush=True)

        elif event_type == "message":

            message = event.get("message", {})
            message_type = message.get("type", "UNKNOWN_MESSAGE_TYPE")
            text = message.get("text", "")

            print("MESSAGE FROM:", user_id, flush=True)
            print("MESSAGE TYPE:", message_type, flush=True)
            print("MESSAGE TEXT:", text, flush=True)

    return jsonify({
        "status": "ok",
        "channel_name": channel_name,
        "destination": destination,
        "events_received": len(events)
    })

# ================= RUN =================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
