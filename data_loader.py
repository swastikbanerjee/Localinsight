import os
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def process_text_file(file_path):
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50 
    )
    chunks = text_splitter.split_documents(documents)
    chunked_documents = [
        {
            "chunk_no": idx + 1,
            "text": chunk.page_content,
            "file_path": file_path,
            "media_type": "text"
        }
        for idx, chunk in enumerate(chunks)
    ]
    return chunked_documents

def process_pdf_file(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=250, 
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    chunked_documents = [
        {
            "chunk_no": idx + 1,
            "text": chunk.page_content,
            "file_path": file_path,
            "media_type": "pdf"
        }
        for idx, chunk in enumerate(chunks)
    ]
    return chunked_documents

def process_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension in ['.txt', '.md', '.csv', '.json']:
        return process_text_file(file_path)
    elif file_extension in ['.pdf']:
        return process_pdf_file(file_path)
    else:
        return [{
            "chunk_no": 1,
            "text": "",
            "file_path": file_path,
            "media_type": "unknown"
        }]

def load_data():
    file_paths = [
        r"c:\Users\swast\OneDrive\Desktop\files_working\topics.txt",
        r"C:\Users\swast\OneDrive\Desktop\files_working\Swastik_Banerjee_Resume.pdf"
    ]
    all_documents = []
    for path in file_paths:
        all_documents.extend(process_file(path))
    
    return all_documents
    