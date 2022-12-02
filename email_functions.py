from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import os

# Credit: https://developers.google.com/gmail/api/guides/sending#recommendations-link
def create_message(sender, to, subject, message_text):
	message = MIMEText(message_text)
	message['to'] = to
	message['from'] = sender
	message['subject'] = subject
	b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
	b64_string = b64_bytes.decode()
	return {'raw': b64_string}

# Credit: https://developers.google.com/gmail/api/guides/sending#recommendations-link
def send_message(service, user_id, message):
	try:
		message = (service.users().messages().send(userId=user_id, body=message)
								 .execute())
		print('Message Id: %s' % message['id'])
		return message
	except HttpError as error:
		print('An error occurred: %s' % error)

# Build API service 
# Credit: https://developers.google.com/gmail/api/quickstart/python
def create_api_service_object (path_to_api_files):
	path_to_token = os.path.join(path_to_api_files, 'token.json')
	path_to_creds = os.path.join(path_to_api_files, 'credentials.json')
	# If modifying these scopes, delete the file token.json.	
	scopes = ['https://www.googleapis.com/auth/gmail.send']
	creds = None
	if os.path.exists(path_to_token):
		creds = Credentials.from_authorized_user_file(path_to_token, scopes)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
								path_to_creds, scopes)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open(path_to_token, 'w') as token:
			token.write(creds.to_json())
	try:
		# Call the Gmail API
		service = build('gmail', 'v1', credentials=creds)
		return service
	except HttpError as error:
		# TODO(developer) - Handle errors from gmail API.
		print(f'An error occurred: {error}')

def gen_email(body, recip_addresses, sender_address, path_to_api_files):
	subject = "ASP: FATAL WRECK"
	for recip in recip_addresses:
		message = create_message(sender_address, recip, subject, body)
		send_message(create_api_service_object (path_to_api_files), sender_address, message)