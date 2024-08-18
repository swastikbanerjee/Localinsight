import weaviate
from weaviate.classes.config import Configure 
import data_loader

class Database:
    
    def __init__(self):
        self.create_client()
        self.generate_collection()
        self.data_ingestion()
        self.initiate_interaction()
        self.close_connection()

    def create_client(self):
        self.client = weaviate.connect_to_local()

    def generate_collection(self):
        if self.client.collections.exists('TextCollection'):
            self.collection = self.client.collections.get('TextCollection')
            return
        self.collection = self.client.collections.create(
            name="TextCollection",
            vectorizer_config=Configure.Vectorizer.text2vec_ollama(
                api_endpoint="http://host.docker.internal:11434",
                model="nomic-embed-text"
            ),
            generative_config=Configure.Generative.ollama(
                api_endpoint="http://host.docker.internal:11434",
                model="llama3.1"
            )
        )
    
    def data_ingestion(self):
        object_list = data_loader.load_data()
        with self.collection.batch.dynamic() as batch:
            for object in object_list:
                batch.add_object(
                    properties=object
                )
    
    def search_with_text(self, query : str):
        return self.collection.query.hybrid(
            query=query,
            limit=3
        )

    def generate_with_text(self, query : str):
        return self.collection.generate.near_text(
            query=query,
            limit=3,
            grouped_task="You are an helpful AI Assistant who explains the given text",
            grouped_properties=['text']
        )

    def initiate_interaction(self):
        while True:
            print("-" * 20)
            choice = int(input("0 Exit, 1 Search, 2 Generate : "))
            if choice == 0:
                print("Exiting")
                break
            elif choice == 1:
                query = input("Query : ")
                response = self.search_with_text(query)
                for object in response.objects:
                    print(object.properties)
            elif choice == 2:
                query = input("Query : ")
                response = self.generate_with_text(query)
                print(response.generated)
                print("--SOURCE--")
                for object in response.objects:
                    print(object.properties)

    def close_connection(self):
        self.client.close()