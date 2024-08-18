import os
import base64
import pandas as pd
from docx import Document
import win32com.client as win32
import speech_recognition as sr
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredPowerPointLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pprint import pprint

# Function to process text files
def process_text_file(file_path):
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    chunks = text_splitter.split_documents(documents)
    chunked_documents = [
        {
            "media_type": "text",
            "class": "TextChunk",
            "properties": {
                "path": file_path,
                "text": chunk.page_content,
                "chunk_length": len(chunk.page_content),
            }
        }
        for chunk in chunks
    ]
    return chunked_documents

# Function to process PDF files
def process_pdf_file(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    chunks = text_splitter.split_documents(documents)
    chunked_documents = [
        {
            "media_type": "pdf",
            "class": "PDFChunk",
            "properties": {
                "path": file_path,
                "text": chunk.page_content,
                "chunk_length": len(chunk.page_content),
            }
        }
        for chunk in chunks
    ]
    return chunked_documents

# Function to process PPTX files
def process_pptx_file(file_path):
    loader = UnstructuredPowerPointLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    chunks = text_splitter.split_documents(documents)
    chunked_documents = [
        {
            "media_type": "pptx",
            "class": "PPTXChunk",
            "properties": {
                "path": file_path,
                "text": chunk.page_content,
                "chunk_length": len(chunk.page_content),
            }
        }
        for chunk in chunks
    ]
    return chunked_documents

# Function to process XLSX files
def process_xlsx_file(file_path):
    xls = pd.ExcelFile(file_path)
    chunked_documents = []
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        chunked_documents.append({
            "media_type": "table",
            "class": "TableData",
            "properties": {
                "path": file_path,
                "sheet_name": sheet_name,
                "content": df.to_dict(),
                "chunk_length": len(df)
            }
        })
    return chunked_documents



# Function to read DOC files
def read_doc_file(file_path):
    word = win32.Dispatch("Word.Application")
    doc = word.Documents.Open(file_path)
    text = doc.Range().Text
    doc.Close(False)  # Ensure the document is closed without saving
    word.Quit()
    return text

# Function to read DOCX files
def read_docx_file(file_path):
    doc = Document(file_path)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text

# Function to process DOC files
def process_doc_file(file_path):
    try:
        text = read_doc_file(file_path)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        pages = text_splitter.split_text(text)
        chunks = text_splitter.create_documents(pages)
        chunked_documents = [
            {
                "media_type": "doc",
                "class": "DocChunk",
                "properties": {
                    "path": file_path,
                    "text": chunk.page_content,
                    "chunk_length": len(chunk.page_content),
                }
            }
            for chunk in chunks
        ]
    except Exception as e:
        print(f"Error processing DOC file {file_path}: {e}")
        return [{
            "media_type": "unknown",
            "class": "UnknownFile",
            "properties": {"path": file_path}
        }]
    
    return chunked_documents

# Function to process DOCX files
def process_docx_file(file_path):
    try:
        text = read_docx_file(file_path)
        text_splitter = RecursiveCharacterTextSplitter(separators= [" "],chunk_size=1000, chunk_overlap=0)
        pages = text_splitter.split_text(text)
        chunks = text_splitter.create_documents(pages)
        chunked_documents = [
            {
                "media_type": "docx",
                "class": "DocxChunk",
                "properties": {
                    "path": file_path,
                    "text": chunk.page_content,
                    "chunk_length": len(chunk.page_content),
                }
            }
            for chunk in chunks
        ]
    except Exception as e:
        print(f"Error processing DOCX file {file_path}: {e}")
        return [{
            "media_type": "unknown",
            "class": "UnknownFile",
            "properties": {"path": file_path}
        }]
    
    return chunked_documents

# Function to process audio files
def process_audio_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension not in ['.wav', '.mp3']:
        return [{
            "media_type": "unknown",
            "class": "UnknownFile",
            "properties": {"path": file_path}
        }]
    
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        chunk_size = 1000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

        def to_base64(path):
            with open(path, 'rb') as file:
                return base64.b64encode(file.read()).decode('utf-8')
        
        audio_base64 = to_base64(file_path)
        
        chunked_documents = [
            {
                "media_type": "audio",
                "class": "AudioTextChunk",
                "properties": {
                    "path": file_path,
                    "text": chunk,
                    "audio": audio_base64,
                    "chunk_length": len(chunk),
                }
            }
            for chunk in chunks
        ]
    except Exception as e:
        print(f"Error processing audio file {file_path}: {e}")
        return [{
            "media_type": "unknown",
            "class": "UnknownFile",
            "properties": {"path": file_path}
        }]
    
    return chunked_documents

# Function to process image files
def process_image_file(file_path):
    try:
        def to_base64(path):
            with open(path, 'rb') as file:
                return base64.b64encode(file.read()).decode('utf-8')
        
        image_base64 = to_base64(file_path)
        
        result = {
            "path": file_path,
            "image": image_base64,
            "mediaType": "image",
        }
        
    except Exception as e:
        print(f"Error processing image file {file_path}: {e}")
        result = {
            "path": file_path,
            "mediaType": "unknown",
            "error": str(e),
        }
    
    return result

# Function to process video files
def process_video_file(file_path):
    try:
        def to_base64(path):
            with open(path, 'rb') as file:
                return base64.b64encode(file.read()).decode('utf-8')
        
        video_base64 = to_base64(file_path)
        
        result = {
            "path": file_path,
            "video": video_base64,
            "mediaType": "Video",
        }
        
    except Exception as e:
        print(f"Error processing image file {file_path}: {e}")
        result = {
            "path": file_path,
            "mediaType": "unknown",
            "error": str(e),
        }
    
    return result


# Main function to determine file type and process accordingly
def process_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    
    print(f"Processing file: {file_path} with extension: {file_extension}")

    if file_extension in ['.txt', '.md', '.csv', '.json']:
        return process_text_file(file_path)
    elif file_extension in ['.pdf']:
        return process_pdf_file(file_path)
    elif file_extension in ['.ppt', '.pptx']:
        return process_pptx_file(file_path)
    elif file_extension in ['.xlsx', '.xls']:
        return process_xlsx_file(file_path)
    elif file_extension in ['.wav', '.mp3']:
        return process_audio_file(file_path)
    elif file_extension in ['.docx']:
        return process_docx_file(file_path)
    elif file_extension in ['.doc']:
        return process_doc_file(file_path)
    elif file_extension in ['.jpg', '.png']:
       return process_image_file(file_path)
    elif file_extension in ['.mp4']:
        return process_video_file(file_path)
    else:
        return [{
            "media_type": "unknown",
            "class": "UnknownFile",
            "properties": {"path": file_path}
        }]

# Example usage
file_paths = [
#     "C:/Users/Anushka/OneDrive/Desktop/alice.txt", 
#     "C:/Users/Anushka/Downloads/NIPS-2017-attention-is-all-you-need-Paper.pdf",
#     "C:/Users/Anushka/Downloads/markdown-sample.md",
#     "C:/Users/Anushka/Downloads/Geographicaldata.csv",
#     "C:/Users/Anushka/Downloads/example_1.json",
#     "C:/Users/Anushka/Downloads/Local_Insight_PPT.pptx",
#    "C:/Users/Anushka/Downloads/file_example_XLSX_10.xlsx",
#    "C:/Users/Anushka/Downloads/speech_output.mp3",
#   "C:/Users/Anushka/Downloads/female.wav",
 "C:/Users/Anushka/Downloads/Travel Itinerary Generator Project report.docx",
#   "C:/Users/Anushka/OneDrive/Pictures/Saved Pictures/img7.jpg"


#"C:/Users/Anushka/Downloads/mixkit-times-square-during-a-sunny-day-4442-hd-ready.mp4"
]

all_documents = []
for path in file_paths:
    processed_files = process_file(path)
    pprint(processed_files, indent=2)  
    all_documents.extend(processed_files)

# Pretty print the result
print("All documents processed")
