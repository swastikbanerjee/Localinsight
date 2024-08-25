# Imports 
import os
import json
import hashlib
import streamlit as st
from chat import OnlineChat, OfflineChat
from retriever import RetrieverClient

# Session State Initializations
if 'folder_path' not in st.session_state:
    st.session_state['folder_path'] = None
if 'indexing_done' not in st.session_state:
    st.session_state['indexing_done'] = False
if 'main_mode' not in st.session_state:
    st.session_state['main_mode'] = 'Chat'
if 'chat_mode' not in st.session_state:
    st.session_state['chat_mode'] = 'offline'
if 'chat_messages' not in st.session_state:
    st.session_state['chat_messages'] = []
if 'search_messages' not in st.session_state:
    st.session_state['search_messages'] = []
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'change_folder_mode' not in st.session_state:
    st.session_state['change_folder_mode'] = False
if 'retriever' not in st.session_state:
    st.session_state['retriever'] = None
if 'chat' not in st.session_state:
    st.session_state['chat'] = None

CREDENTIALS_FILE = "user_credentials.json"

# Password Hash Function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Parse Json File to load credentials
def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

# Save Providded credentials back into the Json file
def save_credentials(credentials):
    with open(CREDENTIALS_FILE, 'w') as file:
        json.dump(credentials, file)

# Login Function
def login(username, password):
    credentials = load_credentials()
    hashed_password = hash_password(password)
    if username in credentials and credentials[username]['password'] == hashed_password:
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
        st.session_state['folder_path'] = credentials[username]['folder_path']
        initialize_clients(st.session_state['folder_path'])
        return True
    return False

# Signup Function
def signup(username, password, folder_path):
    credentials = load_credentials()
    if username not in credentials:
        hashed_password = hash_password(password)
        credentials[username] = {'password': hashed_password, 'folder_path': folder_path}
        save_credentials(credentials)
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
        st.session_state['folder_path'] = folder_path
        initialize_clients(st.session_state['folder_path'])
        return True
    return False

# Logout Function
def logout():
    st.session_state.clear()
    st.session_state['logged_in'] = False

# UI for Login/Signup
def login_signup_interface():
    st.title("LocalInsight - Document Search and Chat")
    st.write("Welcome to LocalInsight, your personal document assistant!")  
    login_tab, signup_tab = st.tabs(["Login", "Signup"])   
    with login_tab:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_button"):
            if login(username, password):
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    with signup_tab:
        new_username = st.text_input("New Username", key="signup_username")
        new_password = st.text_input("New Password", type="password", key="signup_password")
        folder_path = st.text_input("Initial Folder Path", key="signup_folder_path")
        if st.button("Signup", key="signup_button"):
            if signup(new_username, new_password, folder_path):
                st.success("Signed up and logged in successfully!")
                st.session_state['indexing_done'] = False
                st.rerun()
            else:
                st.error("Username already exists.")

# Lets user change document directory
def set_folder_path():
    st.header("Change Folder Path")
    folder_path = st.text_input("Enter the folder path to index:", key="folder_path_input")
    if folder_path:
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            st.session_state['folder_path'] = folder_path
            update_folder_path(st.session_state['username'], folder_path)
            initialize_clients(folder_path)
            st.session_state['indexing_done'] = True
            st.session_state['change_folder_mode'] = False
            st.success("Folder path updated successfully!")
            st.rerun()
        else:
            st.error("Invalid folder path. Please enter a valid path.")
    if st.button("Back"):
        st.session_state['change_folder_mode'] = False
        st.rerun()

# Overwrite changed folder path content into the json file
def update_folder_path(username, folder_path):
    credentials = load_credentials()
    if username in credentials:
        credentials[username]['folder_path'] = folder_path
        save_credentials(credentials)

# Initialize Retriever & Chat Clients
def initialize_clients(folder_path):
    st.session_state['retriever'] = RetrieverClient(folder_path)
    # if st.session_state['chat_mode'] == 'offline':
    #     st.session_state['chat'] = OfflineChat()
    # else:
    #     st.session_state['chat'] = OnlineChat()
    st.session_state['offline_chat'] = OfflineChat()
    st.session_state['online_chat'] = OnlineChat(#api_key="AIzaSyBP1ylGlIC6HqNP1OLw6BYooZht6Pk84jo"
        )

# Chat Interactions - 
def handle_chat():
    for message in st.session_state['chat_messages']:
        if message['role'] == 'user':
            with st.chat_message("user"):
                st.write(message['content'])
        else:
            with st.chat_message("assistant"):
                st.write(message['content'])
    user_message = st.chat_input("Type your message here:")
    if user_message:
        st.session_state['chat_messages'].append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.write(user_message)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                search_results = st.session_state['retriever'].search(text=user_message, image_path=None)
                response = handle_offline_response(st.session_state['offline_chat'] ,user_message, search_results) if st.session_state['chat_mode'] == "offline" \
                else handle_online_response(st.session_state['online_chat'], user_message, search_results)
        st.session_state['chat_messages'].append({"role": "assistant", "content": response})

# Search Interactions 
# Main Streamlit App

# Function to open files with better error handling
def open_file(path):
    try:
        # Ensure the path exists
        if not os.path.exists(path):
            st.error(f"File not found: {path}")
            return

        # Attempt to open the file with the default application
        if os.name == 'nt':  # For Windows
            os.startfile(path)
        elif os.name == 'posix':  # For macOS or Linux
            os.system(f'open "{path}"' if 'darwin' in os.uname().sysname.lower() else f'xdg-open "{path}"')
        else:
            st.warning("Your operating system may not support this operation.")
    except Exception as e:
        st.error(f"Failed to open the file: {e}")

# Search Interaction Handler with Session State
def handle_search():
    # Text input for search query
    user_query = st.text_input("Type your search query here:", key="search_input")
    
    # Image upload input
    uploaded_image = st.file_uploader("Or upload an image to search:", type=["png", "jpg", "jpeg"], key="image_uploader")
    
    if st.button("Search", key="search_send"):
        with st.spinner("Searching..."):
            if user_query or uploaded_image:
                image_path = None
                if uploaded_image:
                    # Save the uploaded image to a temporary path
                    image_path = f"temp_uploaded_image.{uploaded_image.name.split('.')[-1]}"
                    with open(image_path, "wb") as f:
                        f.write(uploaded_image.getbuffer())

                search_results = st.session_state['retriever'].search(text=user_query, image_path=image_path)
                
                # Store the search results in session state
                st.session_state['search_results'] = search_results
                
                # Clean up the temporary image file after search
                if uploaded_image and os.path.exists(image_path):
                    os.remove(image_path)

    # Display search results if they exist in session state
    if 'search_results' in st.session_state:
        search_results = st.session_state['search_results']
        st.subheader("Search Results:")
        
        file_paths = []
        image_paths = []
        for result in search_results['text']:
            if result['path'] not in file_paths:
                file_paths.append(result['path'])
        for result in search_results['image']:
            if result['path'] not in image_paths:
                image_paths.append(result['path'])

        # Display text files
        for path in file_paths:
            st.write(f"**Found:** {os.path.basename(path)}")
            if st.button(f"Open: {os.path.basename(path)}", key=f"open_{path}"):
                open_file(path)
        
        # Display images
        for image_path in image_paths:
            st.image(image_path, caption=os.path.basename(image_path), use_column_width=True)




def handle_offline_response(chat_object:OfflineChat, user_text, search_results):
    # assistant_response = ""
    # for chunk in chat_object.get_assistant_response(user_text, search_results):
    #     # assistant_response += chunk["message"]["content"]
    #     st.write(chunk['message']['content'], end="", flush=True)
    response_generator = chat_object.get_assistant_response(user_text, search_result=search_results)
    response_list = list(response_generator)
    response = response_list[0]["message"]["content"]  # Adjust indexing based on your expected structure

    #response = chat_object.get_assistant_response(user_text, search_result=search_results)["message"]["content"]
    st.write(response)
    st.write(str(search_results))
    chat_object.append_assistant_message(response)
    return response
    

def handle_online_response(chat_object:OnlineChat, user_text, search_results):
    # for chunk in chat_object.get_assistant_response(user_text, search_results):
    #     st.write_stream(chunk)
    response = chat_object.get_assistant_response(user_text, search_results).text
    st.write(response)
    st.write(str(search_results))
    return response

# UI for main page
def main_interface():
    st.sidebar.title("Options")
    st.sidebar.button("Change Folder Path", on_click=lambda: st.session_state.update({'change_folder_mode': True}))
    st.sidebar.button("Logout", on_click=logout)
    
    # Main mode selection
    st.session_state['main_mode'] = st.sidebar.radio("Select Mode", options=["Search", "Chat"])
    
    # Conditionally show chat mode options only in Chat mode
    if st.session_state['main_mode'] == 'Chat':
        st.session_state['chat_mode'] = st.sidebar.radio("Select Chat Mode", options=["offline", "online"])
    
    st.title("LocalInsight")
    st.write(f"Current Folder: {st.session_state['folder_path']}")
    
    if st.session_state['main_mode'] == 'Search':
        st.header("Search Mode")
        handle_search()
    else:
        st.header("Chat Mode")
        handle_chat()

def main():
    st.set_page_config(page_title="LocalInsight", page_icon="🔍", layout="wide")
    if not st.session_state['logged_in']:
        login_signup_interface()
    elif st.session_state['change_folder_mode']:
        set_folder_path()
    else:
        main_interface()

if __name__ == "__main__":
    main()
