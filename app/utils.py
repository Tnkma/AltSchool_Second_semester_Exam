import os
import requests
import re
from dotenv import load_dotenv
from typing import List
from typing import Optional
from fastapi import Request

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


# Validation Class
class InputForm:
    def __init__(self, request: Request):
        # print("Initializing InputForm...")
        self.request: Request = request
        self.errors: List = []
        self.name: Optional[str] = None
        self.email: Optional[str] = None
        self.message: Optional[str] = None
        self.feedback: Optional[str] = None
        
        
    async def load_data(self):
        form = await self.request.form()
        self.name = form.get("name")
        self.email = form.get("email")
        self.feedback = form.get("feedback")
        self.message = form.get("message")
        
    
    def is_valid(self):
        # Reset errors
        self.errors = []
        if not self.name or len(self.name.strip().split()) < 2:
            self.errors.append("Use at least two names (e.g., first and last name).")

        # Email validation
        if not self.email or not re.match(
            r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", 
            self.email
        ):
            self.errors.append("A valid email is required.")
        if not (self.email.__contains__("gmail.com") or self.email.endswith("@gmail.com")
        ):
            self.errors.append("Email must be a Gmail address (ending with @gmail.com).")
        
        # Message validation
        if self.message:
            if len(self.message.strip()) < 10:
                self.errors.append("Message must be at least 10 characters long.")
            if len(self.message.strip()) > 200:
                self.errors.append("Message is too long (max 200 characters).")
            
        # Feedback validation
        if self.feedback:
            if len(self.feedback.strip()) < 5:
                self.errors.append("Feedback must be at least 5 characters long")
            if len(self.feedback.strip()) > 500:
                self.errors.append("Feedback is too long (max 500 characters).")
        print("Validation errors:", self.errors)
        return not self.errors
