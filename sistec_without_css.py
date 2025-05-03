import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

@st.cache_data
def load_docs():
    url = 'https://www.sistec.ac.in/'
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs[0].page_content

page_content = load_docs()

prompt = PromptTemplate(
    template='Answer the following:\n{question}\nBased on the following text:\n{text}',
    input_variables=['question', 'text']
)

model = ChatGoogleGenerativeAI(model='gemini-2.0-flash')
parser = StrOutputParser()
chain = prompt | model | parser

st.title("SISTec Q&A with Gemini AI")
st.markdown("Ask any question about [SISTec](https://www.sistec.ac.in/) and get answers powered by Gemini")

user_input = st.text_input("Enter your question:")
if user_input:
    with st.spinner("Getting answer..."):
        result = chain.invoke({'question': user_input, 'text': page_content})
        st.success("Answer:")
        st.write(result)  