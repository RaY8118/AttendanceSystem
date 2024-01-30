import streamlit as st
import sqlite3
import pandas as pd
import datetime
import shutil
import os

st.set_page_config(
    page_title="Edit Database",
    page_icon="📝"
)
# Connect to the database
conn = sqlite3.connect('../Database/attendance_database.db')
cursor = conn.cursor()

# Create the attendance table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY,
        name TEXT,
        start_time TEXT,
        end_time TEXT,
        date DATE,
        roll_no INTEGER,
        div TEXT,
        branch TEXT,
        reg_id TEXT
    )
''')
conn.commit()


def create_backup():
    # Get the current date and time
    current_datetime = datetime.datetime.now()
    backup_folder = "../backup"  # Specify the backup folder path

    # Create the backup folder if it doesn't exist
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    # Generate the backup file name using the current date and time
    backup_file = f"backup_{current_datetime.strftime('%Y-%m-%d_%H-%M-%S')}.db"

    # Copy the database file to the backup folder
    shutil.copyfile("../Database/attendance_database.db", os.path.join(backup_folder, backup_file))

    print("Backup created successfully.")


def schedule_backup():
    # Get the current day of the week
    current_day = datetime.datetime.now().weekday()

    # Check if it's Sunday (day 6) to perform the backup
    if current_day == 6:
        create_backup()


# Function to insert a new attendance record
def insert_record(name, start_time, end_time, date, roll_no, div, branch, reg_id):
    cursor.execute('''
        INSERT INTO attendance (name, start_time, end_time, date, roll_no, div, branch, reg_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, start_time, end_time, date, roll_no, div, branch, reg_id))
    conn.commit()


# Function to update an existing attendance record
def update_record(record_id, name, start_time, end_time, date, roll_no, div, branch, reg_id):
    cursor.execute('''
        UPDATE attendance
        SET name = ?, start_time = ?, end_time = ?, date = ?, roll_no = ?, div = ?, branch = ?, reg_id = ?
        WHERE id = ?
    ''', (name, start_time, end_time, date, roll_no, div, branch, reg_id, record_id))
    conn.commit()


# Function to delete an attendance record
def delete_record(record_id):
    cursor.execute('DELETE FROM attendance WHERE id = ?', (record_id,))
    conn.commit()


# Function to get attendance records for a specific date
def get_records_by_date(date):
    cursor.execute('SELECT * FROM attendance WHERE date = ?', (date,))
    records = cursor.fetchall()
    return records


# Streamlit app code
def main():
    st.title('Attendance Management App')

    # Sidebar options
    options = ['View Attendance', 'Add Record', 'Update Record', 'Delete Record']
    choice = st.sidebar.selectbox('Select Option', options)
    if st.sidebar.button("Create Backup"):
        create_backup()
    if choice == 'View Attendance':
        st.subheader('View Attendance')
        date = st.date_input('Enter Date (YYYY-MM-DD)')
        if st.button('View'):
            records = get_records_by_date(date)
            if records:
                df = pd.DataFrame(records, columns=['ID', 'Name', 'Start Time', 'End Time', 'Date',
                                                    'Roll No', 'Division', 'Branch', 'Reg ID', ])
                st.table(df)
            else:
                st.warning('No records found for the given date.')

    elif choice == 'Add Record':
        st.subheader('Add Record')
        name = st.text_input('Name')
        start_time = st.text_input('Start Time')
        end_time = st.text_input('End Time')
        date = st.date_input('Date')
        roll_no = st.text_input('Roll No')
        div = st.text_input('Division')
        branch = st.text_input('Branch')
        reg_id = st.text_input('Reg ID')

        if st.button('Add'):
            insert_record(name, start_time, end_time, date, roll_no, div, branch, reg_id)
            st.success('Record added successfully!')

    elif choice == 'Update Record':
        st.subheader('Update Record')
        df = pd.read_sql_query('SELECT * FROM attendance', conn)
        record_id = st.number_input('Record ID', min_value=1, max_value=len(df), step=1)
        record = df[df['id'] == record_id]

        if not record.empty:
            name = st.text_input('Name', value=record['name'].values[0])
            start_time = st.text_input('Start Time', value=record['start_time'].values[0])
            end_time = st.text_input('End Time', value=record['end_time'].values[0])
            date = st.text_input('Date', value=record['date'].values[0])
            roll_no = st.text_input('Roll No', value=record['roll_no'].values[0])
            div = st.text_input('Division', value=record['div'].values[0])
            branch = st.text_input('Branch', value=record['branch'].values[0])
            reg_id = st.text_input('Reg ID', value=record['reg_id'].values[0])

            if st.button('Update'):
                update_record(record_id, name, start_time, end_time, date, roll_no, div, branch, reg_id)
                st.success('Record updated successfully!')
        else:
            st.warning('Record not found!')

    elif choice == 'Delete Record':
        st.subheader('Delete Record')
        df = pd.read_sql_query('SELECT * FROM attendance', conn)
        max_id = conn.execute('SELECT MAX(id) FROM attendance').fetchone()[0]
        record_id = st.number_input('Record ID', min_value=1, max_value=max_id, step=1)

        if st.button('Delete'):
            delete_record(record_id)
            st.success('Record deleted successfully!')


# Run the app
if __name__ == '__main__':
    main()
