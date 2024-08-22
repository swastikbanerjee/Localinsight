from ollama import chat

class OfflineChat:
    
    def __init__(self, retriever, model="phi3"):
        self.__messages = []
        self.__model = model
        self.__retriever = retriever
    
    def __append_user_message(self, user_query, search_result):
        content = ""
        image_paths = []
        for text_properties in search_result['text']:
            content += text_properties['text'] + "\n"
        for image_properties in search_result['image']:
            image_paths.append(image_properties['path'])
        query_with_context = f"""Given Context: {content}
                                 Query: {user_query}"""
        self.__messages.append({"role": "user", "content": query_with_context, "images": image_paths})
    
    def append_assistant_message(self, content):
        self.__messages.append({"role": "assistant", "content" : content})  
         
    def get_assistant_response(self, user_text=None, user_image_path=None):
        """
        Usage:
            for chunk in get_assistant_response(...):
                assistant_response += chunk["message"]["content"]
                print(chunk["message"]["content"], end="", flush=True)
            offline_chat.append_assistant_message(assistant_response)
        """
        search_result = self.__retriever.search(text=user_text, image_path=user_image_path)
        self.__append_user_message(user_text, search_result)
        return chat(self.__model, self.__messages, stream=True, options={"temperature":0})
