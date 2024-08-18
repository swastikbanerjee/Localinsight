import os
from langchain.document_loaders import TextLoader, PyPDFLoader, UnstructuredPowerPointLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pprint import pprint
import pandas as pd

def process_text_file(file_path):
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()

    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=0 
    )
    chunks = text_splitter.split_documents(documents)

    # Convert chunks into the desired dictionary format, including chunk length
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

def process_pdf_file(file_path):
    # Load the PDF file
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Split the PDF text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=0 
    )
    chunks = text_splitter.split_documents(documents)

    # Convert chunks into the desired dictionary format, including chunk length
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

def process_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension in ['.txt', '.md', '.csv', '.json']: # For example. Can include more as and when required :)
        return process_text_file(file_path)
    elif file_extension in ['.pdf']:  
        return process_pdf_file(file_path)
    elif file_extension in ['.ppt','.pptx']:
        return process_pptx_file(file_path)
    elif file_extension in ['.xlsx','.xls']:
        return process_xlsx_file(file_path)
    else:
        return [{
            "media_type": "unknown",
            "class": "UnknownFile", 
            "properties": {"path": file_path}
        }]

# Example usage
file_paths = [
    # "C:/Users/Anushka/OneDrive/Desktop/alice.txt", 
    # "C:/Users/Anushka/Downloads/NIPS-2017-attention-is-all-you-need-Paper.pdf",
    # "C:/Users/Anushka/Downloads/markdown-sample.md",
    # "C:/Users/Anushka/Downloads/Geographicaldata.csv",
    # "C:/Users/Anushka/Downloads/example_1.json",
    #"C:/Users/Anushka/Downloads/Local_Insight_PPT.pptx",
    "C:/Users/Anushka/Downloads/file_example_XLSX_10.xlsx"
]

all_documents = []
for path in file_paths:
    all_documents.extend(process_file(path))

# Pretty print the result
pprint(all_documents, indent=2)
