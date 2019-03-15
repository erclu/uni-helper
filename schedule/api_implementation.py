"""wrapper for relevant google python api methods"""
# pylint: disable=E1101
import json
from pathlib import Path

# from datetime import datetime

from google.oauth2.credentials import Credentials

# from google.oauth2 import id_token
# from google.auth.transport import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from courses import VALID_COURSES, get_table_content

CREDS_FOLDER: Path = Path(__file__).resolve().parents[1].joinpath(".credentials")
CLIENT_SECRETS_FILE: Path = CREDS_FOLDER/"client_secret.json"
CREDS_FILENAME: Path = CREDS_FOLDER/"refresh_token.json"

SCOPES = [
  "https://www.googleapis.com/auth/calendar",
  "https://www.googleapis.com/auth/drive.metadata.readonly",
  "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def get_authenticated_service(api_name: str, api_version: str):
    """returns specified google api service

    Args:
        api_name (str): can be one of sheets, calendar, drive
        api_version (str)

    Returns:
        [type]: [description]
    """

    if CREDS_FILENAME.exists():
        credentials = Credentials.from_authorized_user_file(str(CREDS_FILENAME))
        # TODO make request to the access token endpoint???

        # FIXME verifying token
        # credentials.refresh(requests.Request())
        # print(credentials.token, credentials.expiry)

        # idinfo = id_token.verify_oauth2_token(
        #   credentials.token, requests.Request(), credentials.client_id)

        # if idinfo['iss'] not in ['accounts.google.com',
        #                          'https://accounts.google.com']:
        #     # CREDS_FILENAME.unlink()
        #     raise ValueError('Wrong issuer.')

    else:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_local_server(
          host="localhost",
          port=8080,
          authorization_prompt_message="Please visit this URL: {url}",
          success_message="The auth flow is complete; you may close this window.",
          open_browser=True,
        )

        creds_data = {
          "token": None,
          "refresh_token": credentials.refresh_token,
          "token_uri": credentials.token_uri,
          "client_id": credentials.client_id,
          "client_secret": credentials.client_secret,
          "scopes": credentials.scopes,
        }

        with CREDS_FILENAME.open("w") as outfile:
            json.dump(creds_data, outfile)

    return build(api_name, api_version, credentials=credentials)


UNI_CALENDAR_ID = "frij0gsijkrjegt7nk18noiqrc@group.calendar.google.com"


class MyCalendarBatchInsert:
    """google api calendar service to insert events via a batch request"""

    def __init__(self, callback=None):

        self._service = get_authenticated_service("calendar", "v3")
        self._batch = self._service.new_batch_http_request(callback=callback)

    def add(self, event, callback=None, request_id=None):
        """adds an event to be inserted by the request"""
        request = self._service.events().insert(calendarId=UNI_CALENDAR_ID, body=event)
        self._batch.add(request, request_id, callback)

    def execute(self):
        """executes the batch request"""
        return self._batch.execute()


# def print_upcoming_events(how_many):
#     """requests upcoming events"""

#     now = datetime.utcnow().isoformat() + "Z"

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
SPREADSHEET_ID = "12Bs9eSLuUO7gNTsiUTwERPo-KGZFfJjRkjWzEJ7t8Kk"
RANGE_NAME = "Esami!B7:C21"


def get_last_modified() -> str:
    """get the last modified time for the spreadsheet containing classes info

    Returns:
        str: string containing time of last modification in isoformat
    """
    service = get_authenticated_service("drive", "v3")
    response = (
      service.files().get(fileId=SPREADSHEET_ID, fields="modifiedTime").execute()
    )
    return response["modifiedTime"]


def update_courses_colors():
    """updates the local file by requesting the content of the google sheet with
    the courses colors
    """
    last_modified = get_last_modified()
    table = get_table_content()

    if last_modified > table["lastUpdated"]:
        print("getting file changes...")

        service = get_authenticated_service("sheets", "v4")

        response = (
          service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME, majorDimension="ROWS"
          ).execute()
        )
        values = response["values"]

        for row in values:
            course = row[0].lower()
            try:
                color = row[1]
            except IndexError:
                color = None
            table["courses"][course]["color"] = color

        table["lastUpdated"] = last_modified

        with VALID_COURSES.open("w", encoding="utf-8") as outfile:
            json.dump(table, outfile, ensure_ascii=False)

        print("table updated")
    else:
        print("table is up do date")


if __name__ == "__main__":
    # print_upcoming_events(5)
    # print("----------------------------------")
    update_courses_colors()
