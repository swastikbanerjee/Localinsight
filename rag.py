import os
import numpy as np
import faiss
import streamlit as st
from langchain_community.llms import CTransformers

# Parse text files
def parse_text_files(directory):
    text_data = {}
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            with open(os.path.join(directory, filename), 'r') as file:
                text_data[filename] = file.read()
    return text_data

# Generate a simulated text embedding using Llama2-7b model
def generate_embeddings(text_data, model):
    embeddings = {}
    for filename, text in text_data.items():
        # Generate a text completion
        outputs = model(text)
        # Create a dummy embedding from the text completion
        dummy_embedding = np.mean([ord(c) for c in outputs], axis=0)  # This is a placeholder
        embeddings[filename] = np.array([dummy_embedding])
    return embeddings

# Get the answer to the query
def get_answer(query, model, index, text_data, filenames):
    # Generate a text completion for the query
    query_output = model(query)
    # Create a dummy query embedding
    query_embedding = np.mean([ord(c) for c in query_output], axis=0)
    query_embedding = np.array([query_embedding])
    # Search for the closest document
    D, I = index.search(query_embedding, k=1)
    closest_filename = filenames[I[0][0]]
    return text_data[closest_filename]

# Main function to run the Streamlit app
def main():
    st.title('RAG Chatbot')
    st.write('Ask a question about the text files.')

    # Specify the directory containing the text files
    directory = 'C:/Users/Anushka/OneDrive/Desktop'
    
    # Parse the text files
    text_data = parse_text_files(directory)
    st.write("Parsed text files:", text_data)

    # Load the Llama2-7b model from the .bin file
    model_path = 'C:/Users/Anushka/Downloads/Documents/Project 1- LLM/Blog Generation/models/llama-2-7b-chat.ggmlv3.q8_0.bin'
    model = CTransformers(model=model_path, model_type='llama', config={'max_new_tokens': 256, 'temperature': 0.01})
    st.write("Loaded Llama2-7b model")

    # Generate dummy embeddings for the text files
    embeddings = generate_embeddings(text_data, model)
    
    # Check if embeddings are generated
    if not embeddings:
        st.write("No embeddings generated. Please check the text files and model.")
        return
    
    # Store embeddings in a FAISS index
    d = len(next(iter(embeddings.values()))[0])  # Dimension of embeddings
    index = faiss.IndexFlatL2(d)
    
    filenames = list(embeddings.keys())
    embedding_matrix = np.vstack([embedding[0] for embedding in embeddings.values()])  # Convert to 2D array
    index.add(embedding_matrix)
    st.write("Stored embeddings in FAISS index")

    user_query = st.text_input('Your query:')

    if st.button('Submit'):
        if user_query:
            answer = get_answer(user_query, model, index, text_data, filenames)
            st.write(answer)
        else:
            st.write('Please enter a query.')

if __name__ == '__main__':
    main()
