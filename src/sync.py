import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import mysql.connector
import logging
import decimal

# Set up logging for the application
logging.basicConfig(level=logging.INFO)

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

# Fetch data from Google Sheets
def fetch_sheet_data():
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    return result.get('values', [])

# Check if row already exists in the database
def row_exists_in_db(row):
    cursor = db.cursor()
    query = "SELECT * FROM EmployeeData WHERE employee_name = %s AND role = %s AND email = %s AND salary = %s"
    cursor.execute(query, tuple(row))
    return cursor.fetchone() is not None

# Sync Google Sheets data to MySQL
def sync_sheet_to_db():
    logging.info("Syncing data from Google Sheets to MySQL...")
    rows = fetch_sheet_data()

    if not rows or len(rows) <= 1:
        logging.warning("No data found in Google Sheets to sync.")
        return
    
    for row in rows[1:]:  # Skip the header
        if len(row) < 4:  # Ensure the row has enough data
            logging.warning(f"Skipping row with insufficient data: {row}")
            continue
        print("monster",row)
        # Check if the row already exists in the database
        if not row_exists_in_db(row[1::]):
            
            create_row(tuple(row[1::]))  # Insert the row if it doesn't exist
        else:
            logging.info(f"Row already exists in database, skipping: {row}")

    logging.info("Data synchronized from Google Sheets to MySQL")

# Sync MySQL data to Google Sheets
def sync_db_to_sheet():
    logging.info("Syncing data from MySQL to Google Sheets...")
    mysql_rows = read_rows()
    
    if not mysql_rows:
        logging.warning("No data found in MySQL to sync.")
        return
    
    # Convert each row to a list and handle Decimal types
    def convert_to_json_serializable(row):
        return [float(x) if isinstance(x, decimal.Decimal) else x for x in row]
    
    body = {
        'values': [convert_to_json_serializable(row) for row in mysql_rows]
    }

    # Use append to prevent overwriting the header
    sheet.values().clear(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A2:E").execute()  # Clear rows below the header
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="Sheet1!A2",  # Start appending data from the second row
        valueInputOption="RAW",
        body=body
    ).execute()
    
    logging.info(f"{result.get('updatedCells')} cells updated in Google Sheets")

# Main function to manage synchronization in both directions
def continuous_sync(interval=30):
    while True:
        try:
            sync_sheet_to_db()  # Sync from Google Sheets to MySQL
            sync_db_to_sheet()  # Sync from MySQL to Google Sheets
        except Exception as e:
            logging.error(f"An error occurred during synchronization: {e}")
        time.sleep(interval)  # Wait for the next sync cycle

if __name__ == "__main__":
    # Start continuous sync every 30 seconds
    logging.info("Starting the continuous synchronization process...")
    continuous_sync(interval=30)