"""
Scam Shield - Database & Geolocation Layer
Manages anonymous community scam reports and coordinates for live heatmap visualization.
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "scams.db")

# Known coordinates for Indian metros and major cities for live heatmap plotting
CITY_COORDINATES = {
    "New Delhi": (28.6139, 77.2090),
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Bengaluru": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "Chandigarh": (30.7333, 76.7794),
    "Noida": (28.5355, 77.3910),
    "Gurugram": (28.4595, 77.0266),
    "Indore": (22.7196, 75.8577),
    "Bhopal": (23.2599, 77.4126),
    "Patna": (25.5941, 85.1376),
    "Surat": (21.1702, 72.8311),
    "Nagpur": (21.1458, 79.0882),
    "Kochi": (9.9312, 76.2673)
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema and seeds initial scam reports if empty."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scam_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                pincode TEXT,
                scam_type TEXT NOT NULL,
                message_snippet TEXT NOT NULL,
                suspect_identifier TEXT,
                risk_level TEXT DEFAULT 'high',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        # Check if table is empty, seed realistic demo data
        cursor.execute("SELECT COUNT(*) FROM scam_reports")
        count = cursor.fetchone()[0]
        if count == 0:
            seed_initial_data(cursor)
            conn.commit()

def lookup_city_coords(city_name: str):
    """Fuzzy lookup of city coordinates, with small jitter so points don't stack directly on top."""
    city_name_clean = city_name.strip().title()
    for known_city, (lat, lon) in CITY_COORDINATES.items():
        if known_city.lower() in city_name_clean.lower() or city_name_clean.lower() in known_city.lower():
            # Add slight random jitter (approx 1-3 km) to disperse nearby reports
            jitter_lat = lat + random.uniform(-0.025, 0.025)
            jitter_lon = lon + random.uniform(-0.025, 0.025)
            return jitter_lat, jitter_lon, known_city

    # Fallback to Delhi with jitter
    return 28.6139 + random.uniform(-0.03, 0.03), 77.2090 + random.uniform(-0.03, 0.03), city_name_clean

def seed_initial_data(cursor):
    """Seeds realistic community scam alerts for a live, believable radar map."""
    seed_reports = [
        # Delhi
        ("New Delhi", "Fake Electricity Bill Disconnection", "Dear consumer electricity will be disconnected tonight at 9:30 PM bill not updated call 9811223344", "9811223344", "danger"),
        ("New Delhi", "Digital Arrest / Fake Police & Customs", "FedEx customs parcel intercepted with illegal narcotics in Mumbai, Skype call order CBI", "+919420011223", "danger"),
        ("Noida", "Part-Time Job / Telegram Scam", "Earn Rs 4500 daily liking YouTube videos and rating Google maps hotels contact hr on Telegram", "t.me/GlobalTasks01", "danger"),
        ("Gurugram", "UPI 'Receive Money' PIN Fraud", "OLX buyer sent QR code and told enter UPI PIN to receive advance token money 15000", "army.rahul@okaxis", "danger"),
        ("New Delhi", "Bank KYC / PAN Phishing", "SBI account suspended today due to KYC update PAN immediately at http://sbi-kyc-auth.xyz", "http://sbi-kyc-auth.xyz", "danger"),
        ("New Delhi", "Fake Electricity Bill Disconnection", "Disconnection notice from BSES power officer call 9711883399 immediately", "9711883399", "danger"),

        # Mumbai
        ("Mumbai", "Fake Electricity Bill Disconnection", "Mahavitaran power cut notice tonight call officer 9820012345 to update last month receipt", "9820012345", "danger"),
        ("Mumbai", "Digital Arrest / Fake Police & Customs", "Crime Branch officer calling regarding money laundering through Canara Bank account", "+919930214455", "danger"),
        ("Mumbai", "UPI 'Receive Money' PIN Fraud", "Received collect request of Rs 9,999 saying 'Google Pay Cashback Approved Enter PIN'", "cashback99@paytm", "danger"),
        ("Mumbai", "Malicious APK Screen Share", "Download PM Kisan Yojana app from pmkisan-verify.apk to claim subsidy", "pmkisan-verify.apk", "danger"),
        ("Mumbai", "Part-Time Job / Telegram Scam", "Review luxury hotels on TripAdvisor earn 6000 Rs per day telegram recruitment", "t.me/LuxuryReviewJob", "danger"),

        # Bengaluru
        ("Bengaluru", "Part-Time Job / Telegram Scam", "Amazon merchant review task earn 5000 daily deposit 1000 for VIP crypto account", "t.me/AmazonVendorVIP", "danger"),
        ("Bengaluru", "Fake Electricity Bill Disconnection", "BESCOM power cut alert call electricity desk at 9900112233 immediately", "9900112233", "danger"),
        ("Bengaluru", "Bank KYC / PAN Phishing", "HDFC Netbanking access blocked click link https://hdfc-quick-pan.online to submit documents", "https://hdfc-quick-pan.online", "danger"),
        ("Bengaluru", "UPI 'Receive Money' PIN Fraud", "Flat broker asking to scan QR code to receive refund deposit", "broker_deposit@icici", "danger"),
        ("Bengaluru", "Digital Arrest / Fake Police & Customs", "Bengaluru Cyber Crime police station summons via WhatsApp video call", "+918022998877", "danger"),

        # Hyderabad
        ("Hyderabad", "UPI 'Receive Money' PIN Fraud", "Buyer on Quikr agreed to buy sofa asked to enter PIN to credit 12000", "quikr_buyer@ybl", "danger"),
        ("Hyderabad", "Fake Electricity Bill Disconnection", "TSSPDCL electricity bill not paid power supply cut tonight contact 9848011223", "9848011223", "danger"),
        ("Hyderabad", "Bank KYC / PAN Phishing", "ICICI Bank notice: Update PAN card immediately to avoid account closure", "http://icici-pan-verify.xyz", "danger"),
        ("Hyderabad", "Lottery / KBC Advance Fee", "Congratulations you won KBC 25 Lakh lottery call manager Rana Pratap on WhatsApp", "9875544332", "danger"),

        # Pune
        ("Pune", "Fake Electricity Bill Disconnection", "MSEDCL power disconnection notice tonight call officer 9850114477", "9850114477", "danger"),
        ("Pune", "Part-Time Job / Telegram Scam", "Work from home data entry and YouTube subscription task earn 3000 daily", "t.me/EasyEarnPune", "danger"),
        ("Pune", "Malicious APK Screen Share", "Customer care asked to install AnyDesk to process pending LPG subsidy refund", "AnyDesk App", "danger"),

        # Kolkata
        ("Kolkata", "Digital Arrest / Fake Police & Customs", "Kolkata customs confiscated courier parcel containing fake credit cards", "+919830114488", "danger"),
        ("Kolkata", "Fake Electricity Bill Disconnection", "CESC urgent power cut alert call section officer 9831002233", "9831002233", "danger"),
        ("Kolkata", "Bank KYC / PAN Phishing", "PBL/SBI yono login locked update KYC immediately", "http://yono-service.club", "danger"),

        # Chennai
        ("Chennai", "Fake Electricity Bill Disconnection", "TANGEDCO power supply will be cut tonight at 10 PM call officer 9444012345", "9444012345", "danger"),
        ("Chennai", "UPI 'Receive Money' PIN Fraud", "Vehicle buyer on OLX sending QR code to pay advance", "olx_army_chennai@upi", "danger"),

        # Ahmedabad & Jaipur
        ("Ahmedabad", "Fake Electricity Bill Disconnection", "UGVCL power supply will be stopped tonight call 9898012345", "9898012345", "danger"),
        ("Ahmedabad", "Part-Time Job / Telegram Scam", "Telegram cryptocurrency recharge task earn 8000 daily", "t.me/CryptoTasksHub", "danger"),
        ("Jaipur", "Lottery / KBC Advance Fee", "Jio lucky draw winner 25 Lakh pay 15000 GST to claim", "+919929001122", "danger"),
        ("Jaipur", "Fake Electricity Bill Disconnection", "Jaipur Vidyut Vitran Nigam alert power cut tonight", "9829003344", "danger")
    ]

    now = datetime.now()
    for item in seed_reports:
        city, scam_type, snippet, suspect, risk = item
        lat, lon, std_city = lookup_city_coords(city)
        # Random time within the last 72 hours
        hours_ago = random.randint(1, 72)
        created_time = (now - timedelta(hours=hours_ago, minutes=random.randint(0, 59))).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO scam_reports (city, lat, lon, pincode, scam_type, message_snippet, suspect_identifier, risk_level, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (std_city, lat, lon, "", scam_type, snippet, suspect, risk, created_time))

def add_report(city: str, scam_type: str, message_snippet: str, suspect_identifier: str = "", pincode: str = ""):
    lat, lon, std_city = lookup_city_coords(city)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scam_reports (city, lat, lon, pincode, scam_type, message_snippet, suspect_identifier, risk_level, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'danger', datetime('now', 'localtime'))
        """, (std_city, lat, lon, pincode, scam_type, message_snippet, suspect_identifier))
        conn.commit()
        return cursor.lastrowid

def get_recent_reports(limit: int = 30, city: str = None, scam_type: str = None):
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM scam_reports WHERE 1=1"
        params = []
        if city and city.strip():
            query += " AND city LIKE ?"
            params.append(f"%{city.strip()}%")
        if scam_type and scam_type.strip():
            query += " AND scam_type LIKE ?"
            params.append(f"%{scam_type.strip()}%")

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]
        return rows

def get_heatmap_data():
    """Returns coordinates and intensities for Leaflet.heat ([lat, lon, intensity])."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT lat, lon, scam_type, city, message_snippet, created_at FROM scam_reports")
        rows = cursor.fetchall()
        points = []
        for r in rows:
            # intensity weight between 0.5 and 1.0
            points.append({
                "lat": r["lat"],
                "lon": r["lon"],
                "intensity": 0.8,
                "city": r["city"],
                "scam_type": r["scam_type"],
                "snippet": r["message_snippet"][:75] + ("..." if len(r["message_snippet"]) > 75 else ""),
                "time": r["created_at"]
            })
        return points

def get_stats():
    """Calculates trending scam per city, total counts, and category breakdown."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM scam_reports")
        total_reports = cursor.fetchone()[0]

        # Top scam categories
        cursor.execute("""
            SELECT scam_type, COUNT(*) as count 
            FROM scam_reports 
            GROUP BY scam_type 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_categories = [dict(row) for row in cursor.fetchall()]

        # Top affected cities
        cursor.execute("""
            SELECT city, COUNT(*) as count 
            FROM scam_reports 
            GROUP BY city 
            ORDER BY count DESC 
            LIMIT 6
        """)
        top_cities = [dict(row) for row in cursor.fetchall()]

        # Trending alert calculation (scam with most reports in last 48 hours)
        cursor.execute("""
            SELECT city, scam_type, COUNT(*) as cnt 
            FROM scam_reports 
            GROUP BY city, scam_type 
            ORDER BY cnt DESC 
            LIMIT 1
        """)
        top_trend = cursor.fetchone()
        trending_banner = {
            "city": top_trend["city"] if top_trend else "National",
            "scam_type": top_trend["scam_type"] if top_trend else "Fake Electricity Bill Disconnection",
            "count": top_trend["cnt"] if top_trend else 12
        }

        return {
            "total_reports": total_reports,
            "top_categories": top_categories,
            "top_cities": top_cities,
            "trending": trending_banner
        }
