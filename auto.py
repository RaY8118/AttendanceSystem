import cv2
import pickle
import numpy as np
import face_recognition
import cvzone
import sqlite3
import json
from win32com.client import Dispatch
import datetime
from datetime import time as datetime_time
import time
import threading


def speak(str1):
    speak = Dispatch("SAPI.SpVoice")
    speak.speak(str1)


def morningattendance():
    time.sleep(2)
    speak("Starting Attendance recorded successfully")
    # Record start time and date
    start_time = datetime.datetime.now().strftime("%H:%M:%S")
    print("Start time:", start_time)

    # Check if an entry for the person, date, and start time already exists in the database
    cursor.execute("SELECT * FROM attendance WHERE name = ? AND date = ? AND start_time IS NOT NULL",
                   (name, current_date))
    existing_entry = cursor.fetchone()

    if not existing_entry:
        # Insert start time and student data into the attendance database
        cursor.execute("INSERT INTO attendance (name, start_time, date, roll_no, div, branch, reg_id)VALUES"
                       " (?, ?, ?, ?, ?, ?, ?)",
                       (name, start_time, current_date, roll_no, div, branch, reg_id))
        conn.commit()
        print("Start time and student data recorded in the database")
    else:
        print("Your Attendance is already been recorded before")


def eveningattendance():
    time.sleep(2)
    speak("Ending Attendance recorded successfully")
    # Record end time and date
    end_time = datetime.datetime.now().strftime("%H:%M:%S")
    print("End time:", end_time)

    # Check if an entry for the person, date, and end time already exists in the database
    cursor.execute("SELECT * FROM attendance WHERE name = ? AND date = ? AND end_time IS NOT NULL",
                   (name, current_date))
    existing_entry = cursor.fetchone()

    if not existing_entry:
        # Update the entry with end time
        cursor.execute("UPDATE attendance SET end_time = ? WHERE name = ? AND date = ?",
                       (end_time, name, current_date))
        conn.commit()
        print("End time recorded in the database")


recognized_students = set()
morn_time = datetime_time(20, 0)
even_time = datetime_time(23, 0)
curr_time = datetime.datetime.now().time()
if morn_time <= curr_time < even_time:
    morn_attendance = True
    even_attendance = False
else:
    even_attendance = True
    morn_attendance = False
# Load the student data from the JSON file
with open('Resources/student_data.json', 'r') as json_file:
    student_data = json.load(json_file)

# Connect to an SQLite database
conn = sqlite3.connect('Database/attendance_database.db')

# Create a cursor object
cursor = conn.cursor()

# Create a table in the database if it doesn't exist
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
webcam = True
if webcam:
    cap = cv2.VideoCapture(0)
else:
    cap = cv2.VideoCapture(1)
cap.set(3, 640)
cap.set(4, 480)
imgBackground = cv2.imread('Resources/background.png')

# Import the encoding file
file = open('Resources/EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
    imgBackground[162:162 + 480, 55:55 + 640] = img
    k = cv2.waitKey(1)

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        print("matches", matches)
        print("faceDis", faceDis)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            print("Known face detected")
            student_id = studentIds[matchIndex]  # ID from face recognition
            # Look up the student's name, roll_no, div, and branch from the JSON data using the ID
            student_info = student_data.get(student_id, {})
            name = student_info.get('name', '')  # Actual name from JSON
            roll_no = student_info.get('roll_no', '')
            div = student_info.get('div', '')
            branch = student_info.get('Branch', '')
            reg_id = student_id  # Use the same ID as "Reg ID"

            print(name)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
            cv2.putText(imgBackground, name, (bbox[0], bbox[1] - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                        (255, 255, 0), 3, lineType=cv2.LINE_AA)
            cv2.putText(imgBackground, reg_id, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

            current_date = datetime.datetime.now().date()
            if student_id and morn_attendance and student_id not in recognized_students:
                t = threading.Thread(target=morningattendance)
                t.start()
                recognized_students.add(student_id)
            if student_id and even_attendance and student_id not in recognized_students:
                t = threading.Thread(target=eveningattendance)
                t.start()
                recognized_students.add(student_id)
    if k == ord('q'):
        break

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)

# Close the database connection when done
conn.close()
