import os.path
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
    # token.json stored user access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Authentication if no valid credentials are available
    if not creds or not creds.valid:
        print("here1")
        if creds and creds.expired and creds.refresh_token:
            print("here2")
            creds.refresh(Request())
        else:
            print("here3")
            # This credentials.json is the credential you download from Google API portal when you
            # created the OAuth 2.0 Client IDs
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            # this is the redirect URI which should match your API setting, you can
            # find this setting in Credentials/Authorized redirect URIs at the API setting portal
            print("here4")
            creds = flow.run_local_server(port=49720)
            print("here5")
        # Save vouchers for later use
        with open('token.json', 'w') as token:
            print("write")
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
service = gmail_authenticate()
# send_message(service, "YOUR_ACCOUNT@XXX.com", "TARGET_ACCOUNT@XXX.com", "Test Email", "<h1>This is a test using Gmail API</h1>")
