from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view
from googleapiclient.discovery import build
import google_auth_oauthlib.flow

OAUTH_CREDS = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

BASE_URL = 'https://convin-assignment.sayakongit.repl.co'
REDIRECT_URI = BASE_URL + '/rest/v1/calendar/redirect/'


@api_view(['GET'])
def GoogleCalendarInitView(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        OAUTH_CREDS, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        include_granted_SCOPES='true', access_type='offline')
    request.session['state'] = state

    return redirect(authorization_url)


@api_view(['GET'])
def GoogleCalendarRedirectView(request):
    state = request.session.get('state')

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        OAUTH_CREDS, scopes=SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URI

    authorization_response = request.get_full_path()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    try:
        service = build('calendar', 'v3', credentials=credentials, static_discovery=False)
        all_events_result = service.events().list(
            calendarId='primary').execute()
        all_events = all_events_result.get('items', [])
    
        if not all_events:
            return Response({'Message': 'No events found.'})
        else:
            return Response(all_events)

    except Exception as error:
        return Response({'Message': f'Found an Error : {error}'})
