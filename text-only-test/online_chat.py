import google.generativeai as genai
from IPython.display import Image

class OnlineChat:
    def __init__(self, retriver):
        self.__chat = self.__initiate_chat(api_key="AIzaSyCM1Iq3bgBHDiKVLM1cocsk6ygjJOx5qPU")
        self.__retriever = retriver
         
    def __initiate_chat(self, api_key, model_name="gemini-1.5-flash-001"):
        genai.configure(api_key)
        model = genai.GenerativeModel(model_name=model_name)
        return model.start_chat()
    
    def __create_user_message(self, user_text, search_result):
        content = ""
        images = []
        for text_properties in search_result['text']:
            content += text_properties['text'] + "\n"
        for image_properties in search_result['image']:
            images.append(Image(image_properties['path']))
        query_with_context = f"""Given Context: {content}
                                 Query: {user_text}"""
        return [query_with_context, images]
    
    def get_assistant_response(self, user_text=None, user_image_path=None):
        search_result = self.__retriever.search(text=user_text, image_path=user_image_path)
        return self.__chat(self.__create_user_message(user_text, search_result))    