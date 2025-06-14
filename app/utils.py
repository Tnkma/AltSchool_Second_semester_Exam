import os
import requests
from dotenv import load_dotenv

# Option 1: .env inside this file's directory
env_path_local = os.path.join(os.path.dirname(__file__), '.env')

# Option 2: fallback to shared env
env_path_backup = '/home/ubuntu/shared_env/.env'

if os.path.exists(env_path_local):
    load_dotenv(env_path_local)
    print(f"✅ Loaded .env from: {env_path_local}")
elif os.path.exists(env_path_backup):
    load_dotenv(env_path_backup)
    print(f"✅ Loaded .env from: {env_path_backup}")
else:
    print("⚠️  No .env file found!")


# Load SendGrid API Key and sender email
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_SENDER = os.getenv("SENDGRID_SENDER")


async def send_email(subject: str, body: str, to_email: str):
    if not all([SENDGRID_API_KEY, SENDGRID_SENDER]):
        print("❌ SendGrid settings missing in .env")
        return

    response = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "personalizations": [{
                "to": [{"email": to_email}],
                "subject": subject
            }],
            "from": {"email": SENDGRID_SENDER},
            "content": [{
                "type": "text/plain",
                "value": body
            }]
        }
    )

    if response.status_code >= 400:
        print("❌ Failed to send email:", response.text)
    else:
        print("✅ Email sent successfully!")
