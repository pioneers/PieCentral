'''if this isn't working, run "pip install --upgrade google-api-python-client"
   on the computer.'''


from __future__ import print_function
import httplib2
import os

from Utils import *

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_match(match_number):
    """
    A lot of this is adapted from google quickstart.
    Takes the match number and returns a dictionary with the teams names
    and team numbers for that match.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    spreadsheetId = CONSTANTS.SPREADSHEET_ID
    range_name = "qual_matches!A2:J"
    game_data = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=range_name).execute()
    match = game_data['values'][match_number-1]
    return {"b1name" : match[3], "b1#" : match[2],
             "b2name" : match[5], "b2#" : match[4],
             "g1name" : match[7], "g1#" : match[6],
             "g2name" : match[9], "g2#" : match[8]}

def write_scores(match_number,blue_score,gold_score):
    """
    A method that writes the scores to the sheet
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    spreadsheetId = CONSTANTS.SPREADSHEET_ID
    range_name = "qual_matches!K"+str(match_number+1)+":L"+str(match_number+1)
    game_scores = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=range_name).execute()
    game_scores['values'] = [[blue_score,gold_score]]
    service.spreadsheets().values().update(spreadsheetId=spreadsheetId, range=range_name, body=game_scores, valueInputOption="RAW").execute()
