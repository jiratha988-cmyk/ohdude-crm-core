from flask import Flask, request, jsonify
import json
import os
from datetime import datetime, date

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

# ================= TEMP MEMORY =================

CALL_LEADS = {}
MESSAGE_LOG = []

# ================= HELPERS =================

def now_iso():
    return datetime.now().isoformat(timespec="seconds")

def today_str():
    return date.today().isoformat()

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

# ================= CALL LEADS =================

@app.route("/call-leads", methods=["GET"])
def call_leads():
    return jsonify({
        "total_leads": len(CALL_LEADS),
        "leads": list(CALL_LEADS.values())
    })

# ================= DAILY ADDS DASHBOARD =================

@app.route("/dashboard/daily-adds", methods=["GET"])
def daily_adds():

    dashboard = {}

    for lead in CALL_LEADS.values():
        add_date = lead.get("add_date")
        channel_id = lead.get("channel_id")
        channel_name = lead.get("channel_name", "UNKNOWN_OA")

        key = f"{add_date}:{channel_id}"

        if key not in dashboard:
            dashboard[key] = {
                "date": add_date,
                "channel_id": channel_id,
                "channel_name": channel_name,
                "new_adds": 0
            }

        dashboard[key]["new_adds"] += 1

    return jsonify({
        "total_days_oa_rows": len(dashboard),
        "total_new_adds": len(CALL_LEADS),
        "daily_adds": list(dashboard.values())
    })

# ================= TODAY DASHBOARD =================

@app.route("/dashboard/today", methods=["GET"])
def dashboard_today():

    today = today_str()
    by_oa = {}
    total_today = 0

    for lead in CALL_LEADS.values():
        if lead.get("add_date") == today:
            total_today += 1

            channel_id = lead.get("channel_id")
            channel_name = lead.get("channel_name", "UNKNOWN_OA")

            if channel_id not in by_oa:
                by_oa[channel_id] = {
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "new_adds_today": 0
                }

            by_oa[channel_id]["new_adds_today"] += 1

    return jsonify({
        "date": today,
        "total_new_adds_today": total_today,
        "by_oa": list(by_oa.values())
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
    print("CHANNEL ID:", destination, flush=True)

    events = data.get("events", [])

    for event in events:

        event_type = event.get("type")
        source = event.get("source", {})
        user_id = source.get("userId", "UNKNOWN_USER")
        source_type = source.get("type", "UNKNOWN_SOURCE")
        timestamp = now_iso()

        print("---------- EVENT ----------", flush=True)
        print("CHANNEL NAME:", channel_name, flush=True)
        print("EVENT TYPE:", event_type, flush=True)
        print("USER ID:", user_id, flush=True)

        lead_key = f"{destination}:{user_id}"

        # ===== NEW ADD / FOLLOW EVENT =====

        if event_type == "follow" and user_id != "UNKNOWN_USER":

            if lead_key not in CALL_LEADS:
                CALL_LEADS[lead_key] = {
                    "lead_key": lead_key,
                    "user_id": user_id,
                    "channel_id": destination,
                    "channel_name": channel_name,
                    "source_type": source_type,
                    "lead_status": "new_lead",
                    "follow_status": "followed",
                    "add_date": today_str(),
                    "added_at": timestamp,
                    "last_seen": timestamp,
                    "message_count": 0,
                    "last_message": ""
                }

                print("NEW CALL LEAD ADDED:", lead_key, flush=True)

            else:
                CALL_LEADS[lead_key]["follow_status"] = "followed"
                CALL_LEADS[lead_key]["last_seen"] = timestamp

                print("EXISTING LEAD FOLLOWED AGAIN:", lead_key, flush=True)

        # ===== UNFOLLOW =====

        elif event_type == "unfollow" and user_id != "UNKNOWN_USER":

            if lead_key in CALL_LEADS:
                CALL_LEADS[lead_key]["follow_status"] = "unfollowed"
                CALL_LEADS[lead_key]["last_seen"] = timestamp

            print("UNFOLLOW:", lead_key, flush=True)

        # ===== MESSAGE =====

        elif event_type == "message" and user_id != "UNKNOWN_USER":

            message = event.get("message", {})
            message_type = message.get("type", "UNKNOWN_MESSAGE_TYPE")
            text = message.get("text", "")

            MESSAGE_LOG.append({
                "channel_id": destination,
                "channel_name": channel_name,
                "user_id": user_id,
                "message_type": message_type,
                "text": text,
                "created_at": timestamp
            })

            if lead_key in CALL_LEADS:
                CALL_LEADS[lead_key]["message_count"] += 1
                CALL_LEADS[lead_key]["last_message"] = text
                CALL_LEADS[lead_key]["last_seen"] = timestamp

            print("MESSAGE TEXT:", text, flush=True)

    return jsonify({
        "status": "ok",
        "channel_name": channel_name,
        "destination": destination,
        "events_received": len(events),
        "total_call_leads": len(CALL_LEADS)
    })

# ================= RUN =================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
