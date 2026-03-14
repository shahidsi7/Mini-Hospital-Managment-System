import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'


def get_calendar_service():
    """
    Authorize and return a Google Calendar service object.
    On first run, opens a browser for OAuth login.
    After that, uses saved token.json automatically.
    """
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    "credentials.json not found. "
                    "Download it from Google Cloud Console and place it in the project root."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def create_calendar_event(slot, patient, doctor):
    """
    Create a Google Calendar event for a confirmed booking.
    Adds the event to the primary calendar with both attendees.
    """
    service = get_calendar_service()

    start_dt = datetime.datetime.combine(slot.date, slot.start_time)
    end_dt = datetime.datetime.combine(slot.date, slot.end_time)

    event = {
        'summary': f'Appointment with Dr. {doctor.username}',
        'description': (
            f'Patient: {patient.username}\n'
            f'Doctor: Dr. {doctor.username}\n'
            f'Date: {slot.date}\n'
            f'Time: {slot.start_time} - {slot.end_time}'
        ),
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'attendees': [
            {'email': patient.email, 'displayName': patient.username},
            {'email': doctor.email, 'displayName': f'Dr. {doctor.username}'},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 60},
                {'method': 'popup', 'minutes': 15},
            ],
        },
    }

    created_event = service.events().insert(
        calendarId='primary',
        body=event,
        sendUpdates='all'  # Sends invite emails to attendees
    ).execute()

    return created_event.get('htmlLink')
