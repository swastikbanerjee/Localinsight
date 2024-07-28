from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
    UnstructuredExcelLoader,
    CSVLoader,
    JSONLoader,
)
import os
from typing import List
from langchain_core.documents import Document
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)
PERSIST_DIRECTORY = "./chroma_db"  

# returns a Chroma db object
def load_documents_into_database(model_name: str, documents_path: str):
    if os.path.exists(PERSIST_DIRECTORY):
        print("Loading embeddings from disk")
        db = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=OllamaEmbeddings(model=model_name))
    else:
        print("Loading documents")
        raw_documents = load_documents(documents_path)
        documents = TEXT_SPLITTER.split_documents(raw_documents)
        
        print("Creating embeddings and loading documents into Database")
        db = Chroma.from_documents(documents, OllamaEmbeddings(model=model_name), persist_directory=PERSIST_DIRECTORY)
        db.persist()  

    return db

# returns a List fo `Document` objects
def load_documents(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"The specified path does not exist: {path}")

    loaders = {
        ".pdf": DirectoryLoader(
            path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
            use_multithreading=True,
        ),
        ".md": DirectoryLoader(
            path,
            glob="**/*.md",
            loader_cls=TextLoader,
            show_progress=True,
        ),
        ".txt": DirectoryLoader(
            path,
            glob="**/*.txt",
            loader_cls=TextLoader,
            show_progress=True,
        ),
        ".docx": DirectoryLoader(
            path,
            glob="**/*.docx",
            loader_cls=UnstructuredWordDocumentLoader,
            show_progress=True,
        ),
        ".doc": DirectoryLoader(
            path,
            glob="**/*.doc",
            loader_cls=UnstructuredWordDocumentLoader,
            show_progress=True,
        ),
        ".pptx": DirectoryLoader(
            path,
            glob="**/*.pptx",
            loader_cls=UnstructuredPowerPointLoader,
            show_progress=True,
        ),
        ".ppt": DirectoryLoader(
            path,
            glob="**/*.ppt",
            loader_cls=UnstructuredPowerPointLoader,
            show_progress=True,
        ),
        ".xlsx": DirectoryLoader(
            path,
            glob="**/*.xlsx",
            loader_cls=UnstructuredExcelLoader,
            show_progress=True,
        ),
        ".xls": DirectoryLoader(
            path,
            glob="**/*.xls",
            loader_cls=UnstructuredExcelLoader,
            show_progress=True,
        ),
        ".csv": DirectoryLoader(
            path,
            glob="**/*.csv",
            loader_cls=CSVLoader,
            show_progress=True,
        ),
        ".json": DirectoryLoader(
            path,
            glob="**/*.json",
            loader_cls=JSONLoader,
            show_progress=True,
        ),
    }

    docs = []
    for file_type, loader in loaders.items():
        print(f"Loading {file_type} files")
        docs.extend(loader.load())
    return docs
