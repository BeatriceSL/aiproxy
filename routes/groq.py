import os
from groq import Groq
from langchain_groq import ChatGroq
import json
from llama_parse import LlamaParse
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import nest_asyncio  # noqa: E402
nest_asyncio.apply()
from dotenv import load_dotenv

load_dotenv()

def get_query_from_user(prompt_text):
    GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
    # Initialize Embeddings
    embed_model = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")

    chat_model = ChatGroq(temperature=0,
                          model_name="llama3-70b-8192",
                          api_key=GROQ_API_KEY)

    vectorstore = Chroma(embedding_function=embed_model,
                          persist_directory="chroma_db_llamaparse1",
                          collection_name="rag")
    
    retriever=vectorstore.as_retriever(search_kwargs={'k': 3})

    custom_prompt_template = """Use the following pieces of information to answer the user's question.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.

    Context: {context}
    Question: {question}

    Only return the helpful answer below and nothing else.
    Helpful answer:
    """

    def set_custom_prompt():
        """
        Prompt template for QA retrieval for each vectorstore
        """
        prompt = PromptTemplate(template=custom_prompt_template,
                                input_variables=['context', 'question'])
        return prompt
    #
    prompt = set_custom_prompt()
    prompt

    ########################### RESPONSE ###########################
    PromptTemplate(input_variables=['context', 'question'], template="Use the following pieces of information to answer the user's question.\nIf you don't know the answer, just say that you don't know, don't try to make up an answer.\n\nContext: {context}\nQuestion: {question}\n\nOnly return the helpful answer below and nothing else.\nHelpful answer:\n")

    qa = RetrievalQA.from_chain_type(llm=chat_model,
                                   chain_type="stuff",
                                   retriever=retriever,
                                   return_source_documents=True,
                                   chain_type_kwargs={"prompt": prompt})

    response = qa.invoke({"query": prompt_text})
