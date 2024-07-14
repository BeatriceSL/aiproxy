from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from langchain_groq import ChatGroq
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import nest_asyncio
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class QueryRequest(BaseModel):
    prompt_text: str

@router.post("/groq_query")
async def groq_query(request: QueryRequest):
    try:
        GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
        if not GROQ_API_KEY:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY is not set in environment variables")

        # Initialize Embeddings
        embed_model = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")

        chat_model = ChatGroq(temperature=0, model_name="llama3-70b-8192", api_key=GROQ_API_KEY)

        vectorstore = Chroma(embedding_function=embed_model, persist_directory="chroma_db_llamaparse1", collection_name="rag")

        retriever = vectorstore.as_retriever(search_kwargs={'k': 3})

        custom_prompt_template = """Use the following pieces of information to answer the user's question.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.

        Context: {context}
        Question: {question}

        Only return the helpful answer below and nothing else.
        Helpful answer:
        """

        prompt = PromptTemplate(template=custom_prompt_template, input_variables=['context', 'question'])

        qa = RetrievalQA.from_chain_type(llm=chat_model, chain_type="stuff", retriever=retriever, return_source_documents=True, chain_type_kwargs={"prompt": prompt})

        response = qa.invoke({"query": request.prompt_text})

        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))