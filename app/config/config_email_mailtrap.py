import smtplib
from email.mime.text import MIMEText
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Mailtrap settings (Free tier)
SMTP_SERVER = "sandbox.smtp.mailtrap.io"
SMTP_PORT = 2525
SMTP_USER = "d902b5d9968ac6"    # Only username without 'username' suffix
SMTP_PASSWORD = "39215620cfcbb1" 

def send_email(to_email: str, subject: str, body: str) -> Optional[bool]:
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "notifications@foodsaveria.com"
    msg['To'] = to_email
    
    try:
        # Create server with debugging enabled
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1)
        
        # Start TLS encryption
        server.starttls()
        
        # Authenticate with PLAIN auth
        server.login(SMTP_USER, SMTP_PASSWORD)
        
        # Send message
        server.send_message(msg)
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"Authentication failed: {str(e)}")
        return False
    except smtplib.SMTPServerDisconnected as e:
        logging.error(f"Server disconnected: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return False