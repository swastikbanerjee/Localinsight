from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain.chains import create_history_aware_retriever, create_retrieval_chain, ConversationalRetrievalChain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain.memory import ConversationBufferMemory

from langchain_community.chat_message_histories import ChatMessageHistory

# with query re-writing
def getChatChain(llm, db):
    retriever = db.as_retriever(search_type = "similarity", search_kwargs={"k": 3})

    prompt = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
        Question: {question} 
        Context: {context} 
        Answer:"""
    
    def format_docs(docs):c
        return "\n\n".join(doc.page_content for doc in docs)
    
    contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    store = {}

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]


    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    def chat(input : str):
        for chunk in conversational_rag_chain.stream({"input": input}, config = {"configurable": {"session_id": "abc123"}},):
            if 'answer' in chunk: print(chunk['answer'], end="", flush=True)

    return chat


# --------------------------------------------------------
# some other attempts
# def getChatChain(llm, db):
#     retriever = db.as_retriever(search_type = "similarity", search_kwargs={"k": 3})

#     system_prompt = (
#         "You are an assistant for question-answering tasks. "
#         "Use the following pieces of retrieved context to answer "
#         "the question. If you don't know the answer, say that you "
#         "don't know. Use three sentences maximum and keep the "
#         "answer concise."
#         "\n\n"
#         "{context}"
#     )

#     prompt = ChatPromptTemplate.from_messages(
#         [
#             ("system", system_prompt),
#             ("human", "{input}"),
#         ]
#     )


#     question_answer_chain = create_stuff_documents_chain(llm, prompt)
#     rag_chain = create_retrieval_chain(retriever, question_answer_chain)

#     def chat(input : str):
#         result = rag_chain.invoke({'input' : input})
#         # print(result['context'])
#         print(result['answer'])
        
#     return chat

# not working
# def getChatChain(llm, db):
    
#     retriever = db.as_retriever(search_type = "similarity", search_kwargs={"k": 3})

#     def format_docs(docs):
#         return "\n\n".join(doc.page_content for doc in docs)
    
#     template = """Use the following pieces of context to answer the question at the end.
#     If you don't know the answer, just say that you don't know, don't try to make up an answer.
#     Use three sentences maximum and keep the answer as concise as possible.
#     Always say "thanks for asking!" at the end of the answer.

#     {context}

#     Question: {question}

#     Helpful Answer:"""
#     prompt = PromptTemplate.from_template(template)

#     rag_chain = (
#         {"context": retriever | format_docs, "question": RunnablePassthrough()}
#         | prompt
#         | llm
#         | StrOutputParser()
#     )

#     def chat(input : str):
#         print("Answer: ", end='')
#         for chunk in rag_chain.stream(input):
#             print(chunk, end="", flush=True)
            
#     return chat

