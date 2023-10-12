import pickle
from pathlib import Path

import streamlit_authenticator as stauth

names = ["admin1", "admin2", "admin3", "student1"]
usernames = ["admin1", "admin2", "admin3", "student1"]
passwords = ["admin123", "admin213", "admin321", "stu1"]

hashed_passwords = stauth.Hasher(passwords).generate()
file_path = Path(__file__).parent / "hashed_pw.pkl"

with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)
