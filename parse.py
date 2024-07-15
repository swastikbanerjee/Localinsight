import zipfile
from pathlib import Path
from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredPowerPointLoader,
    UnstructuredImageLoader
)
import os
from typing import List
from langchain_core.documents import Document
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

# If unstructured package is available, import the loader for DOCX
try:
    from langchain_community.document_loaders import UnstructuredDocxLoader
except ImportError:
    UnstructuredDocxLoader = None

TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

def load_documents_into_database(model_name: str, documents_path: str) -> Chroma:
    print("Loading documents")
    raw_documents = load_documents(documents_path)
    documents = TEXT_SPLITTER.split_documents(raw_documents)

    print("Creating embeddings and loading documents into Chroma")
    db = Chroma.from_documents(
        documents,
        OllamaEmbeddings(model=model_name),
    )
    return db

def unzip_files(zip_path: str, extract_to: str):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    return extract_to

def load_documents(path: str) -> List[Document]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"The specified path does not exist: {path}")

    temp_extract_dir = os.path.join(path, "extracted")
    os.makedirs(temp_extract_dir, exist_ok=True)

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
        ".csv": DirectoryLoader(
            path,
            glob="**/*.csv",
            loader_cls=CSVLoader,
            show_progress=True,
        ),
        ".docx": DirectoryLoader(
            path,
            glob="**/*.docx",
            loader_cls=UnstructuredDocxLoader if UnstructuredDocxLoader else TextLoader,
            show_progress=True,
        ),
        ".png": DirectoryLoader(
            path,
            glob="**/*.png",
            loader_cls=UnstructuredImageLoader,
            show_progress=True,
        ),
        ".jpg": DirectoryLoader(
            path,
            glob="**/*.jpg",
            loader_cls=UnstructuredImageLoader,
            show_progress=True,
        ),
        ".jpeg": DirectoryLoader(
            path,
            glob="**/*.jpeg",
            loader_cls=UnstructuredImageLoader,
            show_progress=True,
        ),
        ".pptx": DirectoryLoader(
            path,
            glob="**/*.pptx",
            loader_cls=UnstructuredPowerPointLoader,
            show_progress=True,
        ),
        ".zip": DirectoryLoader(
            path,
            glob="**/*.zip",
            loader_cls=lambda x: [],
            show_progress=True,
        ),
    }

    docs = []
    for file_type, loader in loaders.items():
        print(f"Loading {file_type} files")
        if file_type == ".zip":
            zip_files = [file for file in Path(path).rglob("*.zip")]
            for zip_file in zip_files:
                extract_path = unzip_files(zip_file, temp_extract_dir)
                docs.extend(load_documents(extract_path))
        else:
            docs.extend(loader.load())
    return docs
