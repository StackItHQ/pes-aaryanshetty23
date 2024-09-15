from google.oauth2 import service_account
from googleapiclient.discovery import build

# Set up Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = '../credentials.json'

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
import mysql.connector

# Set up MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",     # Replace with your MySQL username
    password="aaryan", # Replace with your MySQL password
    database="SuperjoinDB"
)

# CRUD operations for MySQL
def create_row(data):
    cursor = db.cursor()
    query = "INSERT INTO EmployeeData (employee_name, role, email, salary) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, data)
    db.commit()

def read_rows():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM EmployeeData")
    return cursor.fetchall()

def update_row(data):
    cursor = db.cursor()
    query = "UPDATE EmployeeData SET employee_name=%s, role=%s, email=%s, salary=%s WHERE id=%s"
    cursor.execute(query, data)
    db.commit()

def delete_row(row_id):
    cursor = db.cursor()
    query = "DELETE FROM EmployeeData WHERE id=%s"
    cursor.execute(query, (row_id,))
    db.commit()

def sync_sheet_to_db():
    rows = fetch_sheet_data()
    for row in rows[1:]:  # Skip the header
        create_row(tuple(row))
    print("Data synchronized from Google Sheets to MySQL")

def sync_db_to_sheet():
    mysql_rows = read_rows()
    body = {'values': [list(row) for row in mysql_rows]}
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="RAW",
        body=body
    ).execute()
    print(f"{result.get('updatedCells')} cells updated in Google Sheets")
