"""
Setup script for Google OAuth2 authentication for Gmail and Calendar APIs.
This script will:
1. Request authorization for Gmail and Calendar APIs
2. Save tokens for future use
3. Configure with your email addresses
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json

# Scopes for both Gmail and Calendar
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar'
]

def setup_google_auth():
    """
    Set up Google OAuth2 authentication and save tokens.
    This will open a browser window for authorization.
    """
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), '..', 'token.json')
    credentials_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')
    
    # Load existing token
    if os.path.exists(token_path):
        print("Loading existing token...")
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"Credentials file not found at {credentials_path}. "
                    "Please download OAuth2 credentials from Google Cloud Console."
                )
            
            print("Starting OAuth flow...")
            print("A browser window will open. Please authorize the application.")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        print(f"Saving token to {token_path}...")
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        print("✓ Authentication successful! Token saved.")
    else:
        print("✓ Valid token found. Authentication ready.")
    
    return creds

if __name__ == "__main__":
    print("=" * 60)
    print("Google OAuth2 Setup for Gmail and Calendar APIs")
    print("=" * 60)
    print()
    
    try:
        creds = setup_google_auth()
        print()
        print("Setup complete! You can now use Gmail and Calendar APIs.")
        print()
        print("Your email addresses:")
        print(f"  Sender: {os.getenv('GOOGLE_USER_EMAIL', 'anmolsureka006@gmail.com')}")
        print(f"  Receiver: {os.getenv('GOOGLE_RECEIVER_EMAIL', 'arnav.prasad999918@gmail.com')}")
        print()
    except Exception as e:
        print(f"✗ Error during setup: {e}")
        print()
        print("Please make sure:")
        print("1. credentials.json exists in the backend directory")
        print("2. You have enabled Gmail API and Calendar API in Google Cloud Console")
        print("3. You have created OAuth2 credentials (Desktop app type)")
        exit(1)