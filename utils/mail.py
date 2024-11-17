from fastapi import HTTPException
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GRequest

def generate_refresh_token():
    # Define the scopes your application needs
    scopes = ["https://www.googleapis.com/auth/gmail.send"]

    # Create the flow using the client secrets file
    flow = InstalledAppFlow.from_client_secrets_file("mail_credentials.json", scopes=scopes)
    creds = flow.run_local_server(port=0)

    # Print or save the refresh token for reuse
    print("Refresh Token:", creds.refresh_token)
    return creds.refresh_token

# Run this function to get a refresh token



async def send_email(to: str, password: str):
    try:
        # Initialize credentials with your client ID, client secret, and refresh token
        creds_data = {
            "client_id": "833293870800-puu5b3bj4h1frtl2rvlaol1abg9ce6h7.apps.googleusercontent.com",
            "client_secret": "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",
            "refresh_token": "1//0guu87dTjeq9mCgYIARAAGBASNwF-L9IrSV8YbxsebI20gBhC8SXtGlpct58EZZMGMqWrC0PWubN335bHdbyBgrJDHMlhTe0EcZM",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
        creds = Credentials.from_authorized_user_info(creds_data, ["https://www.googleapis.com/auth/gmail.send"])

        # Check if the credentials are valid; refresh if necessary
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GRequest())

        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)

        # Create email message
        message = MIMEText('<h4>Your new password is : '+ password + "</h4>", "html")
        message['to'] = to
        message['subject'] = 'SETAHub Acount Password Reset'
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message_body = {'raw': raw_message}
        
        # Send email
        service.users().messages().send(userId='me', body=message_body).execute()
    
    except Exception as e:
        raise HTTPException(status_code=400, detail="Fail to send email due to Internal Server Error")
# {
#   "success": "1//0guu87dTjeq9mCgYIARAAGBASNwF-L9IrSV8YbxsebI20gBhC8SXtGlpct58EZZMGMqWrC0PWubN335bHdbyBgrJDHMlhTe0EcZM"
# }