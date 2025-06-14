import os
import requests
from dotenv import load_dotenv

# Option 1: .env inside the same directory as this file
env_path_local = os.path.join(os.path.dirname(__file__), '.env')

# Option 2: fallback to shared system-wide .env
env_path_backup = '/home/ubuntu/shared_env/.env'

if os.path.exists(env_path_local):
    load_dotenv(env_path_local)
    print(f"✅ Loaded .env from: {env_path_local}")
elif os.path.exists(env_path_backup):
    load_dotenv(env_path_backup)
    print(f"✅ Loaded .env from: {env_path_backup}")
else:
    print("⚠️  No .env file found!")




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
