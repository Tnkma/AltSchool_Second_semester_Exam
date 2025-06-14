import os
import requests
from dotenv import load_dotenv

load_dotenv()

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_SENDER = os.getenv("MAILGUN_SENDER")

async def send_email(subject: str, body: str, to_email: str):
    if not all([MAILGUN_API_KEY, MAILGUN_DOMAIN, MAILGUN_SENDER]):
        print("❌ Mailgun settings missing in .env")
        return

    response = requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": f"Tnkma Team <{MAILGUN_SENDER}>",
            "to": [to_email],
            "subject": subject,
            "text": body
        }
    )

    if response.status_code != 200:
        print("❌ Failed to send email:", response.text)
