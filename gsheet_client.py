from __future__ import print_function
import pickle
import os.path
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.


class GSheetClient:
    
    def __init__(self, spreadsheet_id, scopes):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.spreadsheet_id = spreadsheet_id
        self.service = build('sheets', 'v4', credentials=creds)
        self.sheet = self.service.spreadsheets()

    def get(self, range_name):
        result = self.sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                    range=range_name).execute()
        return result.get('values', [])

    def update(self, range_name, values):
        body = {
            'values': values
        }
        value_input_option = "RAW"
        result = self.sheet.values().update(spreadsheetId=self.spreadsheet_id, range=range_name, valueInputOption=value_input_option, body=body).execute()
