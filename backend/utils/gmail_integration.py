"""
Gmail API integration utilities for sending emails with medical reports.
"""
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google API credentials should be set in environment variables
# GOOGLE_CLIENT_ID
# GOOGLE_CLIENT_SECRET
# GOOGLE_REFRESH_TOKEN
# GOOGLE_USER_EMAIL

try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    logger.warning("Google API client libraries not installed. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


# Use combined scopes for both Gmail and Calendar (same token)
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar'
]


def get_gmail_service():
    """
    Get authenticated Gmail service instance.
    Requires credentials to be set up via OAuth2 flow.
    """
    if not GMAIL_AVAILABLE:
        raise ImportError("Google API client libraries not installed")
    
    creds = None
    # Use absolute path from backend directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    token_path = os.path.join(backend_dir, "token.json")
    credentials_path = os.path.join(backend_dir, "credentials.json")
    
    # Load existing token
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"Credentials file not found at {credentials_path}. "
                    "Please set up OAuth2 credentials from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    service = build('gmail', 'v1', credentials=creds)
    return service


def create_message_with_attachment(
    sender: str,
    to: str,
    subject: str,
    body_text: str,
    attachment_paths: Optional[List[str]] = None
) -> dict:
    """Create a message with optional attachments."""
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    # Add body
    message.attach(MIMEText(body_text, 'plain'))
    
    # Add attachments
    if attachment_paths:
        for file_path in attachment_paths:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(file_path)}'
                    )
                    message.attach(part)
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}


def send_email(
    to: str,
    subject: str,
    body: str,
    attachment_paths: Optional[List[str]] = None,
    sender: Optional[str] = None
) -> dict:
    """
    Send an email via Gmail API.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body text
        attachment_paths: List of file paths to attach
        sender: Sender email (uses GOOGLE_USER_EMAIL env var if not provided)
    
    Returns:
        Dictionary with success status and message details
    """
    try:
        if not GMAIL_AVAILABLE:
            return {
                "success": False,
                "error": "Gmail API libraries not installed. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            }
        
        # Default sender email if not provided
        sender = sender or os.getenv("GOOGLE_USER_EMAIL", "anmolsureka006@gmail.com")
        
        service = get_gmail_service()
        message = create_message_with_attachment(
            sender=sender,
            to=to,
            subject=subject,
            body_text=body,
            attachment_paths=attachment_paths
        )
        
        result = service.users().messages().send(
            userId='me',
            body=message
        ).execute()
        
        logger.info(f"Email sent successfully. Message ID: {result.get('id')}")
        
        return {
            "success": True,
            "message_id": result.get('id'),
            "to": to,
            "subject": subject
        }
    
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }