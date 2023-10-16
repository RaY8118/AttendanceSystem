import streamlit as st
import json
import os
# Load the existing student data
with open('../Resources/student_data.json', 'r') as json_file:
    student_data = json.load(json_file)
uploadDir = '../images'
# Streamlit UI for adding new student data
st.title("Add New Student Data")
st.write("Use this app to add new students' data to the JSON file.")
# Input fields for new student data
name = st.text_input("Name")
branch = st.text_input("Branch")
div = st.text_input("Division")
roll_no = st.number_input("Roll Number", min_value=1)
reg_id = st.text_input("Reg ID")
uploadedImg = st.file_uploader("Upload the Student Image", type=["jpg"])
# Button to add the new student
if st.button("Add Student"):
    # Generate a new student ID (you can customize this logic)
    new_student_id = str(reg_id)

    # Create a new student entry
    new_student = {
        "name": name,
        "Branch": branch,
        "div": div,
        "roll_no": roll_no
    }

    # Add the new student data to the JSON file
    student_data[new_student_id] = new_student
    if uploadedImg is not None:
        filename = os.path.join(uploadDir, f"{reg_id}.jpg")
        with open(filename, 'wb') as f:
            f.write(uploadedImg.read())
        st.success(f"Image saved as {filename}")
    sorted_data = dict(sorted(student_data.items()))

    # Update the JSON file
    with open('../Resources/student_data.json', 'w') as json_file:
        json.dump(sorted_data, json_file, indent=4)

    st.success("New student data added successfully!")
    # Clear input values and refresh the page
if st.button("Clear"):
    name = ""
    branch = ""
    div = ""
    roll_no = 0
    reg_id = ""
    uploadedImg = None

selected_student_id = st.selectbox("Select a student to delete:", list(student_data.keys()))

# Button to delete the selected student
if st.button("Delete Student"):
    if selected_student_id in student_data:
        del student_data[selected_student_id]

        # Update the JSON file
        with open('../Resources/student_data.json', 'w') as json_file:
            json.dump(student_data, json_file, indent=4)

        st.success(f"Student with ID {selected_student_id} has been deleted.")
# Display the updated student data
st.title("Updated Student Data")
st.write("Here is the updated student data:")
st.write(student_data)
