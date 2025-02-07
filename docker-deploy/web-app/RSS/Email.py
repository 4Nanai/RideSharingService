import os.path
import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Authentication and service creation
def gmail_authenticate():
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None
    current_dir = os.getcwd()
    current_dir = os.path.join(current_dir, 'RSS')
    tokenpath = os.path.join(current_dir, 'token.json')
    # token.json stored user access and refresh tokens
    if os.path.exists(tokenpath):
        creds = Credentials.from_authorized_user_file(tokenpath, SCOPES)
    # Authentication if no valid credentials are available
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This credentials.json is the credential you download from Google API portal when you
            # created the OAuth 2.0 Client IDs
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(current_dir ,'credentials.json'), SCOPES)
            # this is the redirect URI which should match your API setting, you can
            # find this setting in Credentials/Authorized redirect URIs at the API setting portal
            creds = flow.run_local_server(port=49720, open_browser=False)
        # Save vouchers for later use
        with open(tokenpath, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

# Create and send emails
def send_message(service, sender, to, subject, msg_html):
    message = MIMEMultipart('alternative')
    message['from'] = sender
    message['to'] = to
    message['subject'] = subject

    msg = MIMEText(msg_html, 'html')
    message.attach(msg)

    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}

    message = (service.users().messages().send(userId="me", body=body).execute())
    print(f"Message Id: {message['id']}")

# Using Gmail API
# service = gmail_authenticate()
# send_message(service, "4nanaiiyo@gmail.com", "yy465@duke.edu", "Test Email", "<h1>This is a test using Gmail API</h1>")
