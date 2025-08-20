import resend
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Resend API settings
RESEND_API_KEY = "re_9mNehCs9_BJhzbeyMLpiGdQ7Ckj77Jkd6"
FROM_EMAIL = "onboarding@resend.dev"

def send_email(to_email: str, subject: str, body: str) -> Optional[bool]:
    try:
        resend.api_key = RESEND_API_KEY
        
        response = resend.Emails.send({
            "from": FROM_EMAIL,
            "to": to_email,
            "subject": subject,
            "html": body
        })
        
        return True if response else False
        
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        return False

