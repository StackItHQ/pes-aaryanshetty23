from google.oauth2 import service_account
from googleapiclient.discovery import build

# Set up Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials/credentials.json'

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

# Define your spreadsheet ID and range
SPREADSHEET_ID = '1keOQMSypM2ge8d4otnuRN0TG6GORaNWs6BtxxouK0JY'  # Replace this with your actual Google Sheet ID
RANGE_NAME = 'Sheet1!A1:E'  # Adjust the range to your needs

# Fetch data from Google Sheets
def fetch_sheet_data():
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    return result.get('values', [])
