
import os
import base64
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DataLoader:

    def __init__(self, folder_path):
        self.folder_path = folder_path

    def process_text_file(self, file_path):
        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
        chunks = text_splitter.split_documents(documents)
        return [
            {
                "media_type": "text",
                "path": file_path,
                "text": chunk.page_content,
                "chunk_index": idx 
            }
            for idx, chunk in enumerate(chunks)
        ]
    
    def process_image_file(self, file_path):
        def to_base64(path):
            with open(path, 'rb') as file:
                return base64.b64encode(file.read()).decode('utf-8')
            
        return {
            "mediaType": "image",
            "path": file_path,
            "image": to_base64(file_path)
            }
    
    def load_data(self):
        object_list = []
        for root, dirs, files in os.walk(self.folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)

                if file_name.lower().endswith(".txt"):
                    object_list.append(self.process_text_file(file_path))
                elif file_name.lower().endswith(".jpg"):
                    object_list.append(self.process_image_file(file_path))
        return object_list
    
        