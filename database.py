import weaviate
from weaviate.classes.config import Configure, Multi2VecField
from weaviate.classes.query import Filter
from data_loader import DataLoader
from IPython.display import Image
import base64

class DatabaseClient:
    
    def __init__(self, folder_path):
        self.create_client()
        self.generate_collection()
        self.data_ingestion(folder_path)
   
    def create_client(self):
        self.client = weaviate.connect_to_local()

    def generate_collection(self):
        if self.client.collections.exists('ClipCollection'):
            # collection = self.client.collections.get('ClipCollection')
            # return
            self.client.collections.delete('ClipCollection')

        self.collection = self.client.collections.create(
            name="ClipCollection",
            vectorizer_config=Configure.Vectorizer.multi2vec_clip(
                    image_fields=[
                        Multi2VecField(
                                name="image"
                        )
                    ],
                    text_fields=[
                        Multi2VecField(
                                name="text"
                        )
                    ]
            )#,
            # generative_config=Configure.Generative.ollama(
            #     api_endpoint="http://host.docker.internal:11434",
            #     model="llama3.1"
            # )
        )
    
    def data_ingestion(self, folder_path):
        loader = DataLoader(folder_path)
        object_list = loader.load_data()
        with self.collection.batch.dynamic() as batch:
            for object in object_list:
                batch.add_object(
                    properties=object
                )
    
    def search_with_text(self, query : str):
        response =  self.collection.query.near_text(
            query=query,
            limit=5
        )
        return [object.properties for object in response.objects]

    def search_with_image(self, image_path):
        def to_base64(path):
            with open(path, 'rb') as file:
                return base64.b64encode(file.read()).decode('utf-8')
        response = self.collection.query.near_image(
            near_image=to_base64(image_path),
            limit=5
        )
        return [object.properties for object in response.objects]

    # def generate_with_text(self, query : str):
    #     return self.collection.generate.near_text(
    #         query=query,
    #         grouped_task="You are an helpful AI Assistant who explains the given text",
    #         filters=Filter.by_property("media_type").equal("text")
    #     )
    
    # def display_response(self, response):
    #     for object in response.objects:
    #         if object.properties['media_type'] == "text":
    #             print(object.properties)
    #             print('-'*20)
    #         elif object.properties['media_type'] == "image":
    #             print(object.properties)
    #             display(Image(object.properties['path']))
    #             print('-'*20)
    
    # def initiate_interaction(self):
    #     while True:
    #         print("-" * 20)
    #         choice = int(input("0 Exit, 1 Search with Text, 2 Search with Image, 3 Generate with Text : "))
    #         if choice == 0:
    #             print("Exiting")
    #             break
    #         elif choice == 1:
    #             query = input("Query : ")
    #             response = self.search_with_text(query)
    #             self.display_response(response)
    #         elif choice == 2:
    #             image_path = input("Image Path: ")
    #             response = self.search_with_image(image_path)
    #             self.display_response(response)
    #         elif choice == 3:
    #             query = input("Query : ")
    #             response = self.generate_with_text(query)
    #             print(response.generated)
    #             print("--SOURCE--")
    #             for object in response.objects:
    #                 print(object.properties)

    def close_connection(self):
        self.client.close()