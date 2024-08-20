import os
import tempfile
import streamlit as st

# Initialize session state variables
if 'folder_path' not in st.session_state:
    st.session_state['folder_path'] = None
if 'indexing_done' not in st.session_state:
    st.session_state['indexing_done'] = False
if 'mode' not in st.session_state:
    st.session_state['mode'] = 'Chat'
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Function to handle folder path selection
def set_folder_path():
    uploaded_file = st.file_uploader("Choose any file from the folder you want to index:", key="file_uploader_index")
    if uploaded_file is not None:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Extract folder path from file
            folder_path = os.path.dirname(temp_file_path)
            st.session_state['folder_path'] = folder_path
            st.write(f"Selected folder: {folder_path}")

            # No need to manually delete the file as TemporaryDirectory handles cleanup

        if st.button("Index Folder"):
            # Call the function to generate embeddings here
            generate_embeddings(folder_path)
            st.session_state['indexing_done'] = True
            st.experimental_rerun()

# Function to generate embeddings (Placeholder)
def generate_embeddings(folder_path):
    # Implement your embedding generation code here
    st.write(f"Generating embeddings for files in {folder_path}...")

# Function to handle file addition
def add_file():
    uploaded_file = st.file_uploader("Choose a file", key="file_uploader_add")
    if uploaded_file is not None:
        # Process the uploaded file
        st.write(f"Processing file: {uploaded_file.name}")

# Function to handle chatbot messages
def handle_chat():
    user_message = st.text_input("Type your message here:", key="chat_input")
    if st.button("Send"):
        if user_message:
            st.session_state['messages'].append({"role": "user", "content": user_message})
            st.session_state['messages'].append({"role": "bot", "content": "This is a placeholder response."})
            st.text_input("Type your message here:", value="", key="chat_input")  # Clear input field
            st.experimental_rerun()

# Function to display the chat messages
def display_chat():
    chat_container = st.container()
    with chat_container:
        for message in st.session_state['messages']:
            if message['role'] == 'user':
                st.write(f"You: {message['content']}")
            else:
                st.write(f"Bot: {message['content']}")

# Main interface
def main_interface():
    # Sidebar options
    st.sidebar.title("Options")
    st.sidebar.button("Change Folder Path", on_click=lambda: st.session_state.update({'folder_path': None, 'indexing_done': False}))

    # Toggle between Search and Chat
    toggle_label = "Switch to Chat Mode" if st.session_state['mode'] == 'Search' else "Switch to Search Mode"
    st.session_state['mode'] = 'Search' if st.toggle(toggle_label, value=(st.session_state['mode'] == 'Search')) else 'Chat'

    if st.session_state['mode'] == 'Search':
        st.header("Search Mode")
        st.write("Search within existing indexed files.")
        # Add "plus" symbol for file upload in search mode
        st.button("➕ Upload File", on_click=lambda: st.file_uploader("Choose a file", key="file_uploader_plus_search"))
        # Chatbot interface for Search mode
        chatbot_interface()
    else:
        st.header("Chat Mode")
        st.write("Interact with the chatbot here.")
        # Add "plus" symbol for file upload in chat mode
        st.button("➕ Upload File", on_click=lambda: st.file_uploader("Choose a file", key="file_uploader_plus_chat"))
        # Chatbot interface for Chat mode
        chatbot_interface()

    # Display the chat messages
    display_chat()

    # Handle user input and chatbot response
    handle_chat()

# Function to create chatbot interface
def chatbot_interface():
    st.text_area("Chat with the bot:", height=300, key="chat_area")

# Application Flow
if st.session_state['folder_path'] is None or not st.session_state['indexing_done']:
    set_folder_path()
else:
    main_interface()
