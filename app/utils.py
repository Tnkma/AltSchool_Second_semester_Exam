import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_SENDER = os.getenv("MAILGUN_SENDER")

def send_email(name: str, sender_email: str, message: str):
    if not all([MAILGUN_API_KEY, MAILGUN_DOMAIN, MAILGUN_SENDER]):
        print("❌ Missing Mailgun environment variables.")
        return

    # Email to admin
    admin_email_data = {
        "from": f"Feedback Bot <{MAILGUN_SENDER}>",
        "to": ["onwusilikenonso@email.com"],
        "subject": f"📬 New Feedback from {name}",
        "text": f"""
You received a new feedback message:

Name: {name}
Email: {sender_email}

Message:
{message}
"""
    }

    # Thank you email to user
    user_email_data = {
        "from": f"Tnkma Team <{MAILGUN_SENDER}>",
        "to": [sender_email],
        "subject": "✅ Thanks for Your Feedback!",
        "text": f"""
Hi {name},

Thank you for your feedback! We truly appreciate your support.

Best regards,  
Tnkma Team
"""
    }

    # Send both emails
    for email_data in [admin_email_data, user_email_data]:
        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data=email_data
        )

        if response.status_code != 200:
            print("❌ Failed to send email:", response.text)
        else:
            print("✅ Email sent successfully.")
