from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from document_loader import load_documents_into_database
import sys

from llm import getChatChain


def main(llm_model_name: str, embedding_model_name: str, documents_path: str):

    try:
        db = load_documents_into_database(embedding_model_name, documents_path)
    except FileNotFoundError as e:
        print(e)
        sys.exit()

    llm = Ollama(model=llm_model_name)
    chat = getChatChain(llm, db)

    while True:
        try:
            user_input = input("\n\nPlease enter your question (or type 'exit' to end): ")
            if user_input.lower() == "exit":
                break

            chat(user_input)
        except KeyboardInterrupt:
            break



if __name__ == "__main__":
    default_model = "tinyllama"
    default_embedding_model = "all-minilm"
    default_path = r"C\Users\Anush\Desktop\test"

    main(default_model, default_embedding_model, default_path)
