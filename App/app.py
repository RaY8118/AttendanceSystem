import sqlite3
import streamlit as st
import pandas as pd
import subprocess
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import datetime
import os
import shutil


def create_backup():
    # Get the current date and time
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.date()
    backup_folder = "../backup"  # Specify the backup folder path

    # Create the backup folder if it doesn't exist
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    if not os.path.exists(f"backup_{current_date.strftime('%Y-%m-%d')}.db"):
        # Generate the backup file name using the current date and time
        backup_file = f"backup_{current_date.strftime('%Y-%m-%d')}.db"

        # Copy the database file to the backup folder
        shutil.copyfile("../Database/attendance_database.db", os.path.join(backup_folder, backup_file))

        print("Backup created successfully.")
        st.success("Backup created successfully.")
    else:
        print(f"Backup for {current_date} already exists")
        st.error(f"Backup for {current_date} already exists")


def schedule_backup():
    # Get the current day of the week
    current_day = datetime.datetime.now().weekday()

    # Check if it's Sunday (day 6) to perform the backup
    if current_day == 6:
        create_backup()


# Set Streamlit page configuration
st.set_page_config(
    page_title="Student Attendance",
    page_icon="🎓",
)

# Define authentication credentials
names = ["admin1", "admin2","student1"]
usernames = ["admin1", "admin2", "student1"]

# Load hashed passwords from a pickle file
file_path = Path(__file__).parent / "../Resources/hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

# Authenticate the user
authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "attendance_dashboard", "abcdef",
                                    cookie_expiry_days=30)
name, authentication_status, username = authenticator.login("Login", "main")

# Check authentication status
if not authentication_status:
    st.error("Username/password is incorrect")

if authentication_status is None:
    st.error("Please enter your username and password")

if authentication_status:
    # Display the main page
    st.title("Student Attendance")
    st.write("Use the filter below to search for student attendance")

    # Connect to the SQLite database
    conn = sqlite3.connect('../Database/attendance_database.db')
    cursor = conn.cursor()

    # Create a logout button in the sidebar
    authenticator.logout("Logout", "sidebar")

    # Define filter options in the sidebar
    st.sidebar.header("Filter Options")
    name_filter = st.sidebar.text_input('Enter the student name')
    roll_no_filter = st.sidebar.text_input('Enter the roll number')
    reg_id_filter = st.sidebar.text_input('Enter the Registration ID')
    date_filter = st.sidebar.date_input('Enter the date', value=None)

    filter_button = st.sidebar.button("Apply Filters")
    show_all = st.sidebar.button("Show all records")
    if st.sidebar.button("Create Backup"):
        create_backup()

    # Add a button to edit the database using a separate Streamlit app
    if st.sidebar.button('Edit the Database'):
        subprocess.Popen(['streamlit', 'run', 'edit.py'])

    # Handle filter button click
    if filter_button:
        # Build the SQL query based on selected filters
        query = "SELECT * FROM attendance WHERE 1=1"

        if name_filter:
            query += f" AND name = '{name_filter}'"
        if roll_no_filter:
            query += f" AND roll_no ='{roll_no_filter}'"
        if reg_id_filter:
            query += f" AND reg_id = '{reg_id_filter}'"
        if date_filter:
            query += f" AND date = '{date_filter}'"

        # Execute the query and fetch data
        cursor.execute(query)
        data = cursor.fetchall()

        # Display filtered data in a DataFrame
        if data:
            df = pd.DataFrame(data,
                              columns=['ID', 'Name', 'Start time', 'End time', 'Date', 'Roll No', 'Div', 'Branch',
                                       'Reg ID'])
            st.write("Filtered Students Records: ")
            st.dataframe(df, width=None, use_container_width=True)
            filename = str(date_filter) + ".csv"
            st.download_button("Download the Attendance", df.to_csv(), file_name=filename, mime='text/csv')
        else:
            st.warning("No data found!")

    # Handle "Show all records" button click
    if show_all:
        query = "SELECT * FROM attendance WHERE 1=1"
        cursor.execute(query)
        data = cursor.fetchall()

        if data:
            df = pd.DataFrame(data,
                              columns=['ID', 'Name', 'Start time', 'End time', 'Date', 'Roll No', 'Div', 'Branch',
                                       'Reg ID'])
            st.write("Filtered Students Records: ")
            st.dataframe(df, width=None)
            filename = str(date_filter) + ".csv"
            st.download_button("Download the Attendance", df.to_csv(), file_name=filename, mime='text/csv')
        else:
            st.warning("No data found!")

    # Close the database connection
    conn.close()
# Schedule the backup function
schedule_backup()
