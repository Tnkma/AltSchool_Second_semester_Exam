import os
import requests
from dotenv import load_dotenv

load_dotenv()

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_SENDER = os.getenv("MAILGUN_SENDER")

def send_email(name: str, sender_email: str, message: str):
    # Email to admin
    admin_data = {
        "from": f"Tnkma Landing Page <{MAILGUN_SENDER}>",
        "to": ["onwusilikenonso@email.com"],
        "subject": f"📩 New Feedback from {name}",
        "text": f"""
You received a new feedback message:

Name: {name}
Email: {sender_email}

Message:
{message}
"""
    }

    # Thank you email to the user
    user_data = {
        "from": f"Tnkma Team <{MAILGUN_SENDER}>",
        "to": [sender_email],
        "subject": "✅ Thanks for Your Feedback!",
        "text": f"""
Hi {name},

Thank you for your feedback! We really appreciate you taking the time to share your thoughts.

Best regards,  
Tnkma Team
"""
    }

    # Send both emails
    for data in (admin_data, user_data):
        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data=data
        )

        if response.status_code != 200:
            print("❌ Failed to send email:", response.text)
