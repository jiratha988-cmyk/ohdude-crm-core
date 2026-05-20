from flask import Flask, request, jsonify
import json
import os
import requests
from datetime import datetime, date

app = Flask(__name__)

# ================= CONFIG =================

GOOGLE_SCRIPT_URL = os.environ.get("GOOGLE_SCRIPT_URL")

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

# ================= MEMORY =================

CALL_LEADS = {}

# ================= HELPERS =================

def now_iso():
    return datetime.now().isoformat(timespec="seconds")

def today_str():
    return date.today().isoformat()

# ================= GOOGLE SHEET PUSH =================

def push_lead_to_google_sheet(lead_data):

    if not GOOGLE_SCRIPT_URL:
        print("GOOGLE_SCRIPT_URL NOT FOUND", flush=True)
        return

    try:

        response = requests.post(
            GOOGLE_SCRIPT_URL,
            json=lead_data,
            timeout=10
        )

        print("GOOGLE SHEET STATUS:", response.status_code, flush=True)
        print("GOOGLE SHEET RESPONSE:", response.text, flush=True)

    except Exception as e:
        print("GOOGLE SHEET ERROR:", str(e), flush=True)

# ================= HOME =================

@app.route("/")
def home():
    return "OhDude CRM Core Running!"

# ================= HEALTH =================

@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })

# ================= CALL LEADS =================

@app.route("/call-leads")
def call_leads():

    return jsonify({
        "total_leads": len(CALL_LEADS),
        "leads": list(CALL_LEADS.values())
    })

# ================= DASHBOARD TODAY =================

@app.route("/dashboard/today")
def dashboard_today():

    today = today_str()

    result = {}

    total = 0

    for lead in CALL_LEADS.values():

        if lead.get("add_date") != today:
            continue

        total += 1

        channel_id = lead.get("channel_id")
        channel_name = lead.get("channel_name")

        if channel_id not in result:
            result[channel_id] = {
                "channel_name": channel_name,
                "new_adds_today": 0
            }

        result[channel_id]["new_adds_today"] += 1

    return jsonify({
        "date": today,
        "total_new_adds_today": total,
        "by_oa": result
    })

# ================= LINE WEBHOOK =================

@app.route("/line-webhook", methods=["POST"])
def line_webhook():

    data = request.get_json(silent=True) or {}

    destination = data.get("destination", "UNKNOWN_DESTINATION")
    channel_name = OA_MAP.get(destination, "UNKNOWN_OA")

    print("========== LINE WEBHOOK ==========", flush=True)
    print("CHANNEL NAME:", channel_name, flush=True)

    events = data.get("events", [])

    for event in events:

        event_type = event.get("type")

        source = event.get("source", {})

        user_id = source.get("userId", "UNKNOWN_USER")

        lead_key = f"{destination}:{user_id}"

        print("EVENT TYPE:", event_type, flush=True)
        print("USER ID:", user_id, flush=True)

        # ================= FOLLOW EVENT =================

        if event_type == "follow":

            timestamp = now_iso()

            lead_data = {
                "lead_key": lead_key,
                "user_id": user_id,
                "channel_id": destination,
                "channel_name": channel_name,
                "follow_status": "followed",
                "lead_status": "new_lead",
                "add_date": today_str(),
                "added_at": timestamp
            }

            CALL_LEADS[lead_key] = lead_data

            print("NEW LEAD SAVED", flush=True)

            # PUSH TO GOOGLE SHEET
            push_lead_to_google_sheet(lead_data)

        # ================= UNFOLLOW =================

        elif event_type == "unfollow":

            if lead_key in CALL_LEADS:
                CALL_LEADS[lead_key]["follow_status"] = "unfollowed"

            print("UNFOLLOW:", user_id, flush=True)

        # ================= MESSAGE =================

        elif event_type == "message":

            message = event.get("message", {})

            text = message.get("text", "")

            print("MESSAGE:", text, flush=True)

            if lead_key in CALL_LEADS:
                CALL_LEADS[lead_key]["last_message"] = text

    return jsonify({
        "status": "ok",
        "channel_name": channel_name
    })

# ================= RUN =================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port
    )
