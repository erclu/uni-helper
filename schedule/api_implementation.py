#pylint: disable=E1101
import json
import os
# from datetime import datetime as dt

from google.oauth2.credentials import Credentials
# from google.oauth2 import id_token
# from google.auth.transport import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from courses import VALID_COURSES

CREDS_FOLDER = os.path.join(os.path.dirname(__file__), '.credentials')
CLIENT_SECRETS_FILE = os.path.join(CREDS_FOLDER, 'client_secret.json')
CREDS_FILENAME = os.path.join(CREDS_FOLDER, "refresh_token.json")

SCOPES = [
  'https://www.googleapis.com/auth/calendar',
  'https://www.googleapis.com/auth/drive.metadata.readonly',
  'https://www.googleapis.com/auth/spreadsheets.readonly'
]


def get_authenticated_service(api_name, api_version):

    if os.path.exists(CREDS_FILENAME):
        credentials = Credentials.from_authorized_user_file(CREDS_FILENAME)
        # TODO make request to the access token endpoint???

        # FIXME verifying token
        # credentials.refresh(requests.Request())
        # print(credentials.token, credentials.expiry)

        # idinfo = id_token.verify_oauth2_token(
        #   credentials.token, requests.Request(), credentials.client_id)

        # if idinfo['iss'] not in ['accounts.google.com',
        #                          'https://accounts.google.com']:
        #     # os.remove(CREDS_FILENAME)
        #     raise ValueError('Wrong issuer.')

    else:
        flow = InstalledAppFlow.from_client_secrets_file(
          CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_local_server(
          host='localhost',
          port=8080,
          authorization_prompt_message='Please visit this URL: {url}',
          success_message=
          'The auth flow is complete; you may close this window.',
          open_browser=True)

        creds_data = {
          'token': None, 'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri, 'client_id':
            credentials.client_id, 'client_secret': credentials.client_secret,
          'scopes': credentials.scopes
        }

        with open(CREDS_FILENAME, 'w') as outfile:
            json.dump(creds_data, outfile)

    return build(api_name, api_version, credentials=credentials)


UNI_CALENDAR_ID = 'frij0gsijkrjegt7nk18noiqrc@group.calendar.google.com'


class MyCalendarBatchInsert():

    def __init__(self, callback=None):

        self._service = get_authenticated_service('calendar', 'v3')
        self._batch = self._service.new_batch_http_request(callback=callback)

    def add(self, event, callback=None, request_id=None):
        request = self._service.events().insert(
          calendarId=UNI_CALENDAR_ID, body=event)
        self._batch.add(request, request_id, callback)

    def execute(self):
        return self._batch.execute()


# def print_upcoming_events(how_many):
#     """requests upcoming events"""

#     now = dt.utcnow().isoformat() + "Z"

#     service = get_authenticated_service('calendar', 'v3')

#     events_result = service.events().list(
#       calendarId=UNI_CALENDAR_ID,
#       timeMin=now,
#       maxResults=how_many,
#       singleEvents=True,
#       orderBy='startTime').execute()
#     # throws google.auth.exceptions.RefreshError when refresh token is bad
#     events = events_result.get('items', [])

#     if not events:
#         print('No upcoming events found.')

#     for event in events:
#         print(
#           event['id'], "|", event['start']['dateTime'][2:16], "|",
#           event['summary'])

# The ID and range of the ClassSchedule spreadsheet.
SPREADSHEET_ID = '12Bs9eSLuUO7gNTsiUTwERPo-KGZFfJjRkjWzEJ7t8Kk'
RANGE_NAME = 'Esami!B7:C21'


def get_last_modified():
    service = get_authenticated_service('drive', 'v3')
    response = service.files().get(
      fileId=SPREADSHEET_ID, fields="modifiedTime").execute()
    return response["modifiedTime"]


def get_table_content():
    with open(VALID_COURSES, "r", encoding="utf-8") as file:
        content = json.load(file)
    return content


def update_courses_colors():
    last_modified = get_last_modified()
    table = get_table_content()

    if last_modified > table["lastUpdated"]:
        print("getting file changes...")

        service = get_authenticated_service('sheets', 'v4')

        response = service.spreadsheets().values().get(
          spreadsheetId=SPREADSHEET_ID,
          range=RANGE_NAME,
          majorDimension="ROWS").execute()
        values = response["values"]

        for row in values:
            course = row[0].lower()
            try:
                color = row[1]
            except IndexError:
                color = None
            table["courses"][course]["color"] = color

        table["lastUpdated"] = last_modified

        with open(VALID_COURSES, "w", encoding="utf-8") as outfile:
            json.dump(table, outfile, ensure_ascii=False)

        print("table updated")
    else:
        print("table is up do date")


if __name__ == '__main__':
    # print_upcoming_events(5)
    # print("----------------------------------")
    update_courses_colors()
