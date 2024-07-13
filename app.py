import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([("system",""),("user","")])
llm = Ollama(model="llama3")
op = StrOutputParser()


chain = prompt | llm | op