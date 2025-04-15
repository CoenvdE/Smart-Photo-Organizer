"""
Google Drive authentication module
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PICKLE_FILE = 'token.pickle'
CREDENTIALS_FILE = os.path.join('drive_json', 'credentials.json')

def authenticate():
    """
    Authenticate with Google Drive API
    
    Returns:
        Credentials: Google API credentials
    """
    credentials = None
    
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            credentials = pickle.load(token)
    
    # If there are no valid credentials, let the user log in
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Credentials file '{CREDENTIALS_FILE}' not found. "
                    "Please create OAuth credentials in Google Cloud Console "
                    "and download the JSON file to the drive_json folder."
                )
            
            # Run the OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(TOKEN_PICKLE_FILE, 'wb') as token:
                pickle.dump(credentials, token)
    
    return credentials 