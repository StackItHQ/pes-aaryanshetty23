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

# Get all employee names from MySQL
def get_mysql_employee_names():
    cursor = db.cursor()
    cursor.execute("SELECT employee_name FROM EmployeeData")
    return [row[0] for row in cursor.fetchall()]

# Function to check if a row with the same employee_name (or unique field) already exists
def get_row_by_employee_name(employee_name):
    cursor = db.cursor()
    query = "SELECT * FROM EmployeeData WHERE employee_name = %s"
    cursor.execute(query, (employee_name,))
    return cursor.fetchone()

def update_row(data, employee_name):
    cursor = db.cursor()
    query = "UPDATE EmployeeData SET role=%s, email=%s, salary=%s WHERE employee_name=%s"
    cursor.execute(query, data + (employee_name,))
    db.commit()

def delete_row_by_employee_name(employee_name):
    cursor = db.cursor()
    query = "DELETE FROM EmployeeData WHERE employee_name=%s"
    cursor.execute(query, (employee_name,))
    db.commit()

# Fetch data from Google Sheets
def fetch_sheet_data():
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    return result.get('values', [])

# Sync Google Sheets data to MySQL
def sync_sheet_to_db():
    logging.info("Syncing data from Google Sheets to MySQL...")
    
    # Get employee names from MySQL (to prevent re-insertion)
    mysql_employee_names = get_mysql_employee_names()

    rows = fetch_sheet_data()

    if not rows or len(rows) <= 1:
        logging.warning("No data found in Google Sheets to sync.")
        return

    google_sheet_employee_names = [row[1] for row in rows[1:] if len(row) > 1]  # Skipping the header row

    # Handle deletions from Google Sheets (remove from MySQL)
    for mysql_employee_name in mysql_employee_names:
        if mysql_employee_name not in google_sheet_employee_names:
            logging.info(f"Deleting row from MySQL: {mysql_employee_name} (deleted from Google Sheets)")
            delete_row_by_employee_name(mysql_employee_name)

    # Sync updates and additions from Google Sheets to MySQL
    for row in rows[1:]:  # Skip the header
        if len(row) < 4:  # Ensure the row has enough data
            logging.warning(f"Skipping row with insufficient data: {row}")
            continue
        
        employee_name, role, email, salary = row[1], row[2], row[3], row[4]
        
        # Check if the row already exists based on employee_name
        existing_row = get_row_by_employee_name(employee_name)
        
        if existing_row:
            # If row exists and values are different, update the row
            existing_role, existing_email, existing_salary = existing_row[2], existing_row[3], existing_row[4]
            if role != existing_role or email != existing_email or salary != existing_salary:
                logging.info(f"Updating row for employee: {employee_name}")
                update_row((role, email, salary), employee_name)
            else:
                logging.info(f"Row for employee: {employee_name} is unchanged, skipping.")
        else:
            # If the row doesn't exist, insert a new one
            logging.info(f"Inserting new row for employee: {employee_name}")
            create_row((employee_name, role, email, salary))

    logging.info("Data synchronized from Google Sheets to MySQL")

# Sync MySQL data to Google Sheets
def sync_db_to_sheet():
    logging.info("Syncing data from MySQL to Google Sheets...")
    mysql_rows = read_rows()
    google_sheet_rows = fetch_sheet_data()

    if not mysql_rows:
        logging.warning("No data found in MySQL to sync.")
        return

    # Convert each row to a list and handle Decimal types
    def convert_to_json_serializable(row):
        return [float(x) if isinstance(x, decimal.Decimal) else x for x in row]

    google_sheet_employee_names = [row[1] for row in google_sheet_rows[1:] if row]  # Skipping the header row

    # Identify rows that should be removed from Google Sheets (i.e., those that exist in Google Sheets but not in MySQL)
    mysql_employee_names = get_mysql_employee_names()

    # Compare Google Sheets rows with MySQL rows
    rows_to_remove = [i+2 for i, row in enumerate(google_sheet_rows[1:]) if row and row[1] not in mysql_employee_names]

    # Remove rows from Google Sheets that no longer exist in MySQL
    for row_num in rows_to_remove:
        sheet.values().clear(spreadsheetId=SPREADSHEET_ID, range=f"Sheet1!A{row_num}:E{row_num}").execute()
        logging.info(f"Deleted row {row_num} in Google Sheets as it no longer exists in MySQL.")

    # Insert data from MySQL back into Google Sheets
    body = {
        'values': [convert_to_json_serializable(row) for row in mysql_rows]
    }

    # Clear all rows in Google Sheets except the header, then update
    sheet.values().clear(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A2:E").execute()  # Clear rows below the header
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="Sheet1!A2",  # Start appending data from the second row
        valueInputOption="RAW",
        body=body
    ).execute()

    logging.info(f"{result.get('updatedCells')} cells updated in Google Sheets")

# Main function to manage synchronization in both directions
def continuous_sync(interval=20):
    while True:
        try:
            sync_sheet_to_db()  # Sync from Google Sheets to MySQL
            sync_db_to_sheet()  # Sync from MySQL to Google Sheets
        except Exception as e:
            logging.error(f"An error occurred during synchronization: {e}")
        time.sleep(interval)  # Wait for the next sync cycle

if __name__ == "__main__":
    # Start continuous sync every 20 seconds
    logging.info("Starting the continuous synchronization process...")
    continuous_sync(interval=20)
