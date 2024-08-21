import os
import json
import streamlit as st

if 'folder_path' not in st.session_state:
    st.session_state['folder_path'] = None
if 'indexing_done' not in st.session_state:
    st.session_state['indexing_done'] = False
if 'mode' not in st.session_state:
    st.session_state['mode'] = 'Chat'
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

CREDENTIALS_FILE = "user_credentials.json"

def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_credentials(credentials):
    with open(CREDENTIALS_FILE, 'w') as file:
        json.dump(credentials, file)

def login(username, password):
    credentials = load_credentials()
    if username in credentials and credentials[username] == password:
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
        return True
    return False

def signup(username, password):
    credentials = load_credentials()
    if username not in credentials:
        credentials[username] = password
        save_credentials(credentials)
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
        return True
    return False

def login_signup_interface():
    st.title("Login / Signup")

    login_tab, signup_tab = st.tabs(["Login", "Signup"])

    with login_tab:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if login(username, password):
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with signup_tab:
        username = st.text_input("New Username", key="signup_username")
        password = st.text_input("New Password", type="password", key="signup_password")
        if st.button("Signup"):
            if signup(username, password):
                st.success("Signed up and logged in successfully!")
                st.session_state['folder_path'] = None
                st.session_state['indexing_done'] = False
                st.rerun()
            else:
                st.error("Username already exists.")

# Folder Path Setting
def set_folder_path():
    folder_path = st.text_input("Enter the folder path to index:", key="folder_path_input")
    if folder_path:
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            st.session_state['folder_path'] = folder_path
            st.write(f"Selected folder: {folder_path}")
            files = os.listdir(folder_path)
            st.write("Folder contents:", files)
            if st.button("Index Folder"):
                generate_embeddings(folder_path)
                st.session_state['indexing_done'] = True
                st.rerun()
        else:
            st.error("Invalid folder path. Please enter a valid path.")

# Function to generate embeddings (Placeholder)
def generate_embeddings(folder_path):
    st.write(f"Generating embeddings for files in {folder_path}...")

def add_file():
    uploaded_file = st.file_uploader("Choose a file", key="file_uploader_add")
    if uploaded_file is not None:
        st.write(f"Processing file: {uploaded_file.name}")

def handle_chat():
    user_message = st.text_input("Type your message here:", key="chat_input")
    if st.button("Send"):
        if user_message:
            st.session_state['messages'].append({"role": "user", "content": user_message})
            st.session_state['messages'].append({"role": "bot", "content": "This is a placeholder response."})
            st.rerun()

def display_chat():
    chat_container = st.container()
    with chat_container:
        for message in st.session_state['messages']:
            if message['role'] == 'user':
                st.write(f"You: {message['content']}")
            else:
                st.write(f"Bot: {message['content']}")

def main_interface():
    st.sidebar.title("Options")
    st.sidebar.button("Change Folder Path", on_click=lambda: st.session_state.update({'folder_path': None, 'indexing_done': False}))

    st.session_state['mode'] = st.sidebar.radio("Select Mode", options=["Search", "Chat"])

    if st.session_state['mode'] == 'Search':
        st.header("Search Mode")
        st.write("Search within existing indexed files.")
        st.button("➕ Upload File", on_click=add_file)
    else:
        st.header("Chat Mode")
        st.write("Interact with the chatbot here.")
        display_chat()
        handle_chat()

    if st.sidebar.button("Online Mode"):
        st.write("Triggering video inferencing function...")
        video_inferencing()

# Video Inferencing Function (Placeholder)
def video_inferencing():
    st.write("Video inferencing triggered.")

if not st.session_state['logged_in']:
    login_signup_interface()
elif st.session_state['folder_path'] is None or not st.session_state['indexing_done']:
    set_folder_path()
else:
    main_interface()