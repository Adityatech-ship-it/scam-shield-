"""
Trust Who - Main Web Application
Flask backend providing REST APIs for scam analysis, community reporting, and live heatmap feed.
"""

from flask import Flask, render_template, request, jsonify
import os
import database
from detector import detector

app = Flask(__name__)

# Initialize database on startup
database.init_db()

# Sample demo presets for 1-click relatable testing during demos
DEMO_PRESETS = [
    {
        "id": "electricity",
        "title": "⚡ Fake Electricity Bill",
        "category": "Fake Electricity Bill Disconnection",
        "badge": "Trending Alert",
        "sample": "Dear consumer, your electricity power will be disconnected tonight at 9:30 PM from the power office because your previous month bill was not updated. Please immediately contact our electricity officer Mr. Sharma at 9811223344. Thank you, State Electricity Board."
    },
    {
        "id": "upi_pin",
        "title": "💸 UPI PIN 'Receive Money' Scam",
        "category": "UPI 'Receive Money' PIN Fraud",
        "badge": "High Financial Risk",
        "sample": "Hi, I am interested in buying your sofa listed on OLX. I am in the army and cannot come in person. I have sent you a payment request of Rs. 15,000. Please approve and enter your 6-digit UPI PIN to receive the money directly into your bank account immediately."
    },
    {
        "id": "telegram_job",
        "title": "📱 Telegram Work-From-Home Scam",
        "category": "Part-Time Job / Telegram Scam",
        "badge": "Youth & Student Target",
        "sample": "Greetings from Global Recruitment! Part-time online job: Earn Rs. 3000 to Rs. 8000 daily simply by subscribing to YouTube channels and giving 5-star Google Map reviews. Daily payouts. No experience needed. Contact our HR manager on Telegram: t.me/GlobalTasks01 now."
    },
    {
        "id": "digital_arrest",
        "title": "🚨 Digital Arrest / FedEx Drug Parcel",
        "category": "Digital Arrest / Fake Police & Customs",
        "badge": "Intimidation Tactic",
        "sample": "This is FedEx Customs Clearance. A parcel booked under your Aadhaar card containing 5 expired passports and 140 grams of MDMA narcotics was intercepted at Mumbai International Airport. Your case has been transferred to CBI Cyber Cell. Join immediate Skype interrogation or face instant arrest."
    },
    {
        "id": "kyc_phishing",
        "title": "🏦 Bank KYC / PAN Card Expiry",
        "category": "Bank KYC / PAN Phishing",
        "badge": "Phishing Link",
        "sample": "Dear SBI Customer, your YONO NetBanking account has been suspended today due to pending KYC documents. Please update your PAN Card immediately by clicking http://sbi-kyc-auth.xyz to avoid permanent account block within 24 hours."
    },
    {
        "id": "safe_message",
        "title": "✅ Genuine Bank Transaction (Safe)",
        "category": "Safe Alert",
        "badge": "Legitimate",
        "sample": "Rs. 250.00 debited from A/c XX1234 on 21-Nov-26 at 18:30 via UPI to GROCERY STORE. Avail Bal: Rs. 14,820.50. If not done by you, SMS BLOCK to 567676 or call 1800112211."
    }
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/presets", methods=["GET"])
def get_presets():
    return jsonify(DEMO_PRESETS)

@app.route("/api/analyze", methods=["POST"])
def analyze_scam():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "")
    result = detector.analyze(text)
    return jsonify(result)

@app.route("/api/reports", methods=["GET"])
def get_reports():
    city = request.args.get("city")
    scam_type = request.args.get("scam_type")
    limit = int(request.args.get("limit", 25))
    reports = database.get_recent_reports(limit=limit, city=city, scam_type=scam_type)
    return jsonify(reports)

@app.route("/api/reports", methods=["POST"])
def submit_report():
    data = request.get_json(force=True, silent=True) or {}
    city = data.get("city", "").strip()
    scam_type = data.get("scam_type", "").strip()
    snippet = data.get("message_snippet", "").strip()
    suspect = data.get("suspect_identifier", "").strip()
    pincode = data.get("pincode", "").strip()

    if not city or not scam_type or not snippet:
        return jsonify({"error": "City, scam type, and message snippet are required."}), 400

    report_id = database.add_report(
        city=city,
        scam_type=scam_type,
        message_snippet=snippet,
        suspect_identifier=suspect,
        pincode=pincode
    )
    return jsonify({
        "success": True,
        "message": "Report logged anonymously. Thank you for protecting your community!",
        "report_id": report_id
    })

@app.route("/api/heatmap", methods=["GET"])
def get_heatmap():
    points = database.get_heatmap_data()
    return jsonify({"points": points})

@app.route("/api/stats", methods=["GET"])
def get_stats():
    stats = database.get_stats()
    return jsonify(stats)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "Trust Who"})

if __name__ == "__main__":
    # Run development server on port 5000
    print("=" * 60)
    print("🛡️  TRUST WHO WEB APPLICATION STARTING")
    print("📍 Local URL: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)
