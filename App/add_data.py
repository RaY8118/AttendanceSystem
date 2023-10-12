import streamlit as st
import json

# Load the existing student data
with open('../Resources/student_data.json', 'r') as json_file:
    student_data = json.load(json_file)

# Streamlit UI for adding new student data
st.title("Add New Student Data")
st.write("Use this app to add new students' data to the JSON file.")

# Input fields for new student data
name = st.text_input("Name")
branch = st.text_input("Branch")
div = st.text_input("Division")
roll_no = st.number_input("Roll Number", min_value=1)

# Button to add the new student
if st.button("Add Student"):
    # Generate a new student ID (you can customize this logic)
    new_student_id = str(max(map(int, student_data.keys())) + 1)

    # Create a new student entry
    new_student = {
        "name": name,
        "Branch": branch,
        "div": div,
        "roll_no": roll_no
    }

    # Add the new student data to the JSON file
    student_data[new_student_id] = new_student

    # Update the JSON file
    with open('../Resources/student_data.json', 'w') as json_file:
        json.dump(student_data, json_file, indent=4)

    st.success("New student data added successfully!")

# Display the updated student data
st.title("Updated Student Data")
st.write("Here is the updated student data:")
st.write(student_data)
