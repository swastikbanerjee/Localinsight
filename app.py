from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

import sys

from rag import getChatChain
from parser import load_documents_into_database


def main(llm_model_name, embedding_model_name, documents_path):
    try:
        db = load_documents_into_database(embedding_model_name, documents_path)
    except FileNotFoundError as e:
        print(e)
        sys.exit()

    llm = Ollama(model=llm_model_name)
    chat = getChatChain(llm, db)
    
    while True:
        try:
            user_input = input(
                "\n\nQuestion: "
            )
            if user_input.lower() == "exit":
                break

            chat(user_input)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main("tinyllama", "all-minilm", "documents")
