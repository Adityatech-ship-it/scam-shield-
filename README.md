# 🛡️ Scam Shield (Cybersecurity)

> **Paste or screenshot a suspicious SMS, WhatsApp message, or UPI request.**  
> Scam Shield diagnoses whether it's a fraud, explains *why* in simple jargon-free language, provides actionable advice, and lets you warn family members on WhatsApp with 1 click. Features an anonymous community reporting system and a **live interactive city scam heatmap & radar**.

---

## 🚀 Key Features

1. **🛡️ AI & Heuristic Scam Detector**
   - Detects real-world scams: **Fake Electricity Bill Disconnections**, **UPI 'Receive Money' PIN Fraud**, **Digital Arrest / Fake Customs Narcotics**, **Telegram / YouTube Task Scams**, **Bank KYC / PAN Phishing**, and **Remote Screen Share / Malicious APKs**.
   - **Screenshot OCR Support**: Drag & drop or upload a screenshot of an SMS, WhatsApp chat, or UPI prompt. Client-side OCR (`Tesseract.js`) automatically extracts the text with 0 server configuration.
   - **1-Click Demo Presets**: Test real-world scenarios immediately with pre-loaded samples.

2. **💡 Simple, Jargon-Free Explanations**
   - Explains the exact psychological trigger and technical trick used by the fraudster without confusing jargon.
   - Highlights red flags: urgency pressure, fake authority, unverified APK links, or reverse UPI collect requests.
   - Clear **What You Should Do** & **What You Should NEVER Do** checklists.

3. **🚨 "Warn a Family Member" (1-Click WhatsApp Sharing)**
   - Automatically generates a polite, clear, and urgent alert tailored for parents, grandparents, and family group chats.
   - Instant **Send via WhatsApp** (`https://wa.me/?text=...`) and **Copy Alert** buttons.

4. **🗺️ Live Scam Radar & Heatmap**
   - Interactive Dark Cyber Map (Leaflet.js + CartoDB Dark Matter + Leaflet.heat).
   - Shows heat intensity clusters and real-time incident markers across major cities (Delhi/NCR, Mumbai, Bengaluru, Hyderabad, Pune, Kolkata, Chennai, Jaipur, Ahmedabad, etc.).
   - Dynamic **"Trending Near You"** ticker (e.g., *"Fake Electricity Bill Disconnection trending near New Delhi with 12 reports today"*).
   - Filter by City or Scam Category.

5. **📢 100% Anonymous Community Reporting**
   - Anyone can report a suspicious message, phone number, UPI handle, or link anonymously.
   - Pinned immediately on the live community radar to warn neighbors.

6. **📖 Scam Playbooks & Cyber Helpline Hub**
   - Educational breakdown of the most common cyber scams.
   - Quick reference to the **National Cyber Crime Helpline: 1930**, **cybercrime.gov.in**, and the Chakshu Portal.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask, SQLite3 (Zero database configuration required)
- **Frontend**: HTML5, Tailwind CSS (via CDN), Leaflet.js, Leaflet.heat
- **OCR Engine**: Tesseract.js (Client-side in-browser OCR, no native C++ dependencies needed)
- **Icons & Styling**: Glassmorphism cyber UI, Lucide/Heroicons SVG

---

## 💻 How to Run Locally

### 1. Prerequisites
- Python 3.8+ installed

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Web App
```bash
python app.py
```

### 4. Open in Browser
Visit: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 📁 Project Structure

```
scam-shield-/
├── app.py                     # Flask application & REST API routes
├── detector.py                # Scam detection heuristics, red-flags & family alert generator
├── database.py                # SQLite database, seed data & geocoding
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── static/
│   ├── css/
│   │   └── custom.css         # Cyber glassmorphism styling & radar animations
│   └── js/
│       ├── main.js            # Tab switching, OCR, analysis, family share & reports
│       └── heatmap.js         # Leaflet map, heat layer, city markers & filters
└── templates/
    └── index.html             # Sleek single-page responsive UI
```

---

## 🛡️ License
Open-source community cybersecurity initiative.
