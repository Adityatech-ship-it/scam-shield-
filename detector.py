"""
Scam Shield - Intelligent Scam Detection & Explanation Engine
Analyzes suspicious messages (SMS, WhatsApp, UPI, Email, Telegram)
and produces simple, jargon-free explanations and family warnings.
"""

import re
from typing import Dict, Any, List

class ScamDetector:
    def __init__(self):
        # High-risk scam definitions with patterns, signals, and explanations
        self.scam_archetypes = [
            {
                "id": "electricity_bill",
                "name": "Fake Electricity Bill Disconnection",
                "patterns": [
                    r"(electricity|power|bijli)\s+(will\s+be\s+)?(disconnect|cut|stop)",
                    r"(bill|payment)\s+(was\s+not|not)\s+(update|received|paid)",
                    r"(contact|call)\s+(electricity\s+officer|power\s+office|helpline|\d{10})",
                    r"tonight\s+at\s+\d{1,2}(:\d{2})?\s*(pm|am)?"
                ],
                "min_matches": 2,
                "risk_score": 96,
                "verdict": "HIGH RISK SCAM",
                "explanation": "Threatening immediate electricity disconnection tonight is a notorious nationwide scam. Electricity boards never use private 10-digit mobile numbers or WhatsApp to demand immediate payment.",
                "red_flags": [
                    "Artificial urgency ('power cut tonight')",
                    "Demands calling a personal 10-digit mobile number",
                    "Fake authority claiming to be an electricity officer"
                ],
                "action_do": [
                    "Check your electricity bill status only on the official state electricity board app or website.",
                    "Pay only through authorized platforms (official portal or verified biller in PhonePe/GooglePay/Paytm)."
                ],
                "action_dont": [
                    "NEVER call the phone number provided in the message.",
                    "NEVER install any app (like QuickSupport or AnyDesk) if instructed."
                ]
            },
            {
                "id": "upi_pin_fraud",
                "name": "UPI 'Receive Money' PIN Fraud",
                "patterns": [
                    r"(enter|input|type)\s+(your\s+)?(upi\s+)?pin\s+to\s+(receive|get|claim|accept|credit)",
                    r"pay\s+request\s+of\s+rs",
                    r"(click\s+to\s+receive|accept\s+money|credited\s+after\s+pin)",
                    r"olx\s+(buyer|payment|army)",
                    r"cashback\s+of\s+rs\.?\s*\d+\s+approved"
                ],
                "min_matches": 1,
                "risk_score": 98,
                "verdict": "HIGH RISK SCAM",
                "explanation": "Entering a UPI PIN NEVER receives or credits money. Your UPI PIN is strictly used to DEDUCT money from your bank account.",
                "red_flags": [
                    "Asks you to enter your UPI PIN to 'receive' or 'credit' money",
                    "Pretends to be a buyer on OLX, Facebook Marketplace, or an army personnel",
                    "Sends a 'Collect Request' disguised as a payment receipt"
                ],
                "action_do": [
                    "Decline and reject any collect request received on your UPI app (Google Pay, PhonePe, Paytm).",
                    "Remember: Receiving money requires ZERO passwords or PINs."
                ],
                "action_dont": [
                    "NEVER enter your 4-digit or 6-digit UPI PIN to claim money.",
                    "Do not scan any QR code sent by a buyer to receive payment."
                ]
            },
            {
                "id": "digital_arrest",
                "name": "Digital Arrest / Fake Police & Customs Scam",
                "patterns": [
                    r"(narcotics|drugs|contraband|illegal\s+passports|customs|parcel\s+seized)",
                    r"(digital\s+arrest|mumbai\s+police|cbi|ed|crime\s+branch|rbi)",
                    r"(skype|video\s+call)\s+(verification|interrogation|investigation)",
                    r"(transfer|deposit)\s+(funds|money)\s+to\s+(rbi|government|verification)\s+account",
                    r"fedex|dhl|courier\s+(delivery\s+failed|package\s+held)"
                ],
                "min_matches": 2,
                "risk_score": 99,
                "verdict": "HIGH RISK SCAM",
                "explanation": "There is NO legal concept of 'Digital Arrest' in Indian or international law. Genuine police, CBI, or Customs officers never interrogate citizens over video call or ask for funds to be transferred for 'verification'.",
                "red_flags": [
                    "Claims your Aadhaar was used to send illegal packages (drugs/passports)",
                    "Threatens immediate arrest unless you join a Skype/WhatsApp video call",
                    "Demands transferring money to a 'temporary RBI security account' for clearance"
                ],
                "action_do": [
                    "Immediately disconnect the call.",
                    "Report the incident on the official National Cyber Crime Reporting Portal (cybercrime.gov.in) or call 1930."
                ],
                "action_dont": [
                    "NEVER transfer money under fear of arrest.",
                    "Do not show your bank statements, Aadhaar card, or face on video calls with unverified callers."
                ]
            },
            {
                "id": "telegram_task_scam",
                "name": "Part-Time Job / Video Like / Telegram Scam",
                "patterns": [
                    r"(part\s*time\s*job|work\s*from\s*home|daily\s*income|earn\s*(rs\.?|\$)\s*\d+)",
                    r"(like|subscribe)\s+(youtube|instagram|google\s*maps|hotel\s*review)",
                    r"(telegram|whatsapp\s+hr|contact\s+recruiter|t\.me/)",
                    r"(prepaid\s+task|vip\s+task|recharge\s+commission|crypto\s+trading)",
                    r"earn\s+\d{3,5}\s*(per\s*day|daily)"
                ],
                "min_matches": 2,
                "risk_score": 95,
                "verdict": "HIGH RISK SCAM",
                "explanation": "Fraudsters offer easy money for liking videos or rating hotels. After paying small amounts (₹150-₹500) to win trust, they trap victims into 'prepaid tasks' demanding thousands or lakhs to withdraw profits.",
                "red_flags": [
                    "Absurdly high payouts for trivial tasks (e.g. ₹3000/day for liking YouTube clips)",
                    "Directs you to join a Telegram group with fake 'members' posting screenshots of earnings",
                    "Requires depositing money to unlock earnings or complete 'orders'"
                ],
                "action_do": [
                    "Block the sender and report the contact on WhatsApp/Telegram.",
                    "Warn peers that legitimate companies never recruit via random unsolicited WhatsApp messages."
                ],
                "action_dont": [
                    "NEVER deposit any money into 'prepaid' or 'merchant' accounts.",
                    "Do not share bank or UPI details with unknown Telegram admins."
                ]
            },
            {
                "id": "kyc_bank_phishing",
                "name": "Bank KYC / PAN Card / Account Block Scam",
                "patterns": [
                    r"(sbi|hdfc|icici|axis|pnb|canara|bank)\s+(account|yono|netbanking)",
                    r"(blocked|suspended|deactivated|closed|restricted)\s+(today|within\s+\d+\s+hours|temporarily)",
                    r"(update|link|verify)\s+(your\s+)?(pan|aadhaar|kyc|identity)",
                    r"(http|https|bit\.ly|tinyurl|ngrok|\.xyz|\.top|\.club|\.online)",
                    r"click\s+(here|link|to\s+activate)"
                ],
                "min_matches": 3,
                "risk_score": 97,
                "verdict": "HIGH RISK SCAM",
                "explanation": "Banks never send SMS containing shortened links or demanding immediate PAN/Aadhaar updates under threat of account deactivation.",
                "red_flags": [
                    "Includes an unverified link or suspicious URL (e.g., bit.ly, .xyz, or ngrok)",
                    "Creates panic with threats of immediate account freeze",
                    "Attempts to harvest NetBanking usernames, passwords, and OTPs"
                ],
                "action_do": [
                    "Open your official mobile banking app directly from your app store or visit your branch.",
                    "Forward the phishing SMS to 1909 or report it to your bank's fraud desk."
                ],
                "action_dont": [
                    "NEVER click on links received via SMS claiming to update KYC.",
                    "NEVER share net banking passwords or OTPs with anyone."
                ]
            },
            {
                "id": "malicious_apk",
                "name": "Malicious APK / Remote Screen Share App Scam",
                "patterns": [
                    r"(\.apk|install\s+app|download\s+file)",
                    r"(anydesk|teamviewer|quicksupport|rustdesk|screen\s*share)",
                    r"(pm\s*kisan|loan\s*approval|gift\s*card|free\s*recharge|update\s*app)",
                    r"(allow\s+permission|accessibility\s+service|sms\s+permission)"
                ],
                "min_matches": 2,
                "risk_score": 98,
                "verdict": "HIGH RISK SCAM",
                "explanation": "Asking you to download an '.apk' file or install screen-sharing software (AnyDesk, QuickSupport) allows attackers to mirror your screen and intercept bank OTPs silently.",
                "red_flags": [
                    "Provides a direct link to download an unofficial Android app (.apk)",
                    "Instructs you to install remote control or screen-sharing tools",
                    "Demands SMS and Accessibility permissions"
                ],
                "action_do": [
                    "Install apps ONLY from the Google Play Store or Apple App Store.",
                    "Uninstall any unknown apps immediately and disconnect from Wi-Fi/Mobile Data if already downloaded."
                ],
                "action_dont": [
                    "NEVER download `.apk` files sent over WhatsApp or SMS.",
                    "NEVER grant Accessibility or Screen Recording permissions to unknown callers."
                ]
            },
            {
                "id": "lottery_kbc",
                "name": "Lottery / KBC / Lucky Draw Advance Fee Scam",
                "patterns": [
                    r"(congratulations|lucky\s*winner|won|selected)",
                    r"(kbc|kaun\s*banega\s*crorepati|jio|lottery|draw|prize)",
                    r"rs\.?\s*\d+\s*(lakh|crore)",
                    r"(claim|processing\s*fee|registration\s*charge|tax\s*amount)"
                ],
                "min_matches": 2,
                "risk_score": 93,
                "verdict": "HIGH RISK SCAM",
                "explanation": "You cannot win a lottery or contest you never purchased a ticket for. Scammers demand an 'advance processing fee' or 'GST' to claim a non-existent multi-lakh prize.",
                "red_flags": [
                    "Announces a prize for a contest you never entered",
                    "Uses official brand logos (KBC, Jio, Tata) without verification",
                    "Demands advance fees or taxes before releasing the prize money"
                ],
                "action_do": [
                    "Ignore, delete, and report the message as spam."
                ],
                "action_dont": [
                    "NEVER pay any 'advance fee', 'GST', or 'clearance charge' to claim prizes."
                ]
            }
        ]

        # General red flag triggers
        self.urgency_words = [
            "immediately", "urgent", "tonight", "within 2 hours", "within 24 hours",
            "last chance", "final notice", "hurry", "expire today", "account suspended"
        ]
        self.sensitive_keywords = [
            "upi pin", "atm pin", "otp", "password", "cvv", "card number",
            "aadhaar", "pan card", "netbanking"
        ]
        self.suspicious_domains = [
            r"bit\.ly", r"tinyurl\.com", r"t\.co", r"\.xyz", r"\.top", r"\.club",
            r"\.live", r"\.online", r"ngrok\.io", r"\.ru", r"goo\.gl", r"is\.gd"
        ]

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze a suspicious message text and return structured verdict,
        evidence, risk score, plain English explanation, and family warning card.
        """
        if not text or not text.strip():
            return {
                "verdict": "UNKNOWN",
                "risk_score": 0,
                "risk_level": "none",
                "category": "None",
                "summary": "No text provided for analysis.",
                "explanation": "Please paste a message snippet or upload a screenshot to inspect.",
                "red_flags": [],
                "action_do": [],
                "action_dont": [],
                "family_warning": ""
            }

        text_clean = text.lower()
        matched_archetype = None
        highest_score = 0
        detected_red_flags: List[str] = []

        # 1. Match against known archetypes
        for arch in self.scam_archetypes:
            matches_count = 0
            for pat in arch["patterns"]:
                if re.search(pat, text_clean):
                    matches_count += 1

            if matches_count >= arch["min_matches"]:
                if arch["risk_score"] > highest_score:
                    highest_score = arch["risk_score"]
                    matched_archetype = arch

        # 2. General heuristic red flag inspection
        found_urgency = [w for w in self.urgency_words if w in text_clean]
        if found_urgency:
            detected_red_flags.append(f"Pressure & Urgency tactics: phrases like '{found_urgency[0]}'")

        found_sensitive = [w for w in self.sensitive_keywords if w in text_clean]
        if found_sensitive:
            detected_red_flags.append(f"Solicitation of sensitive credentials: mentions '{found_sensitive[0].upper()}'")

        found_links = []
        for dom in self.suspicious_domains:
            if re.search(dom, text_clean):
                found_links.append(dom.replace("\\", ""))
        if found_links:
            detected_red_flags.append("Suspicious short link or unverified domain")

        # Check phone numbers
        phone_matches = re.findall(r"(?:(?:\+|0{0,2})91[\s-]?)?[6789]\d{9}", text)
        if phone_matches and ("officer" in text_clean or "helpline" in text_clean or "call" in text_clean or "contact" in text_clean):
            detected_red_flags.append(f"Directs call to personal mobile number ({phone_matches[0]}) masquerading as official helpline")

        # 3. Determine final risk score & verdict
        if matched_archetype:
            score = max(highest_score, 85)
            verdict = matched_archetype["verdict"]
            category = matched_archetype["name"]
            explanation = matched_archetype["explanation"]
            red_flags = list(dict.fromkeys(matched_archetype["red_flags"] + detected_red_flags))
            action_do = matched_archetype["action_do"]
            action_dont = matched_archetype["action_dont"]
        else:
            # Check heuristic signals
            heuristics_count = len(detected_red_flags)
            if heuristics_count >= 2:
                score = 75
                verdict = "SUSPICIOUS / POTENTIAL SCAM"
                category = "Suspicious Communication"
                explanation = "This message contains multiple common indicators of fraud, including urgency pressure or suspicious links. Treat with extreme caution."
                red_flags = detected_red_flags
                action_do = ["Verify independently with the sender using known official channels."]
                action_dont = ["Do not click links or share personal info."]
            elif heuristics_count == 1:
                score = 45
                verdict = "MILD CONCERN"
                category = "Unverified Notice"
                explanation = "This message has some suspicious phrasing. It may be unsolicited marketing or spam, but verify before taking action."
                red_flags = detected_red_flags
                action_do = ["Double-check sender credentials."]
                action_dont = ["Avoid opening links or sharing credentials."]
            else:
                score = 10
                verdict = "LIKELY SAFE / LOW RISK"
                category = "Normal Message"
                explanation = "No standard scam triggers, urgency tactics, or phishing links were detected in this message."
                red_flags = []
                action_do = ["Continue to remain vigilant."]
                action_dont = ["Never share your passwords or OTPs with anyone."]

        # Risk level string for CSS badge styling
        if score >= 80:
            risk_level = "danger"
        elif score >= 50:
            risk_level = "warning"
        else:
            risk_level = "safe"

        # Generate Family Warning message for WhatsApp / SMS
        family_warning = self._generate_family_warning(category, verdict, explanation, action_dont, text)

        return {
            "verdict": verdict,
            "risk_score": score,
            "risk_level": risk_level,
            "category": category,
            "summary": f"{verdict} ({score}% confidence)",
            "explanation": explanation,
            "red_flags": red_flags,
            "action_do": action_do,
            "action_dont": action_dont,
            "family_warning": family_warning
        }

    def _generate_family_warning(self, category: str, verdict: str, explanation: str, action_dont: List[str], original_text: str) -> str:
        """
        Creates a pre-formatted, polite, easy-to-read warning for family members (parents, elders, siblings)
        ready to send on WhatsApp with 1 tap.
        """
        short_snippet = original_text.strip().replace("\n", " ")
        if len(short_snippet) > 80:
            short_snippet = short_snippet[:77] + "..."

        dont_advice = action_dont[0] if action_dont else "Do not click any link or send money."

        msg = (
            f"🚨 *SCAM ALERT FOR FAMILY / FRIENDS* 🚨\n\n"
            f"Please be careful! If you receive a message like:\n"
            f"👉 _\"{short_snippet}\"_\n\n"
            f"⚠️ *Scam Type:* {category}\n"
            f"❌ *Why it's fake:* {explanation}\n\n"
            f"🛑 *Golden Rule:* {dont_advice}\n\n"
            f"Verified via *Scam Shield* (Cybersecurity). Stay safe and never share OTP or UPI PIN!"
        )
        return msg


# Global detector instance
detector = ScamDetector()
