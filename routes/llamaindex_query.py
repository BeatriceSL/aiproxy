from fastapi import APIRouter, HTTPException
import os
from llama_parse import LlamaParse
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import UnstructuredMarkdownLoader
import joblib
import nest_asyncio
from dotenv import load_dotenv

nest_asyncio.apply()
load_dotenv()

router = APIRouter()

def load_or_parse_data():
    data_file = "./data/parsed_data.pkl"
    llamaparse_api_key = os.environ.get("LLAMAPARSE_API_KEY")

    if not llamaparse_api_key:
        raise ValueError("LLAMAPARSE_API_KEY is not set in environment variables")

    if os.path.exists(data_file):
        # Load the parsed data from the file
        parsed_data = joblib.load(data_file)
    else:
        # Perform the parsing step and store the result in llama_parse_documents
        parsingInstructionSOC2 = """
SOC-2 Compliance Report Parsing Instruction.
"""
        parser = LlamaParse(api_key=llamaparse_api_key,
                            result_type="markdown",
                            parsing_instruction=parsingInstructionSOC2,
                            max_timeout=5000,)
        llama_parse_documents = parser.load_data("./data/aws-soc-2.pdf")

        # Save the parsed data to a file
        print("Saving the parse results in .pkl format ..........")
        joblib.dump(llama_parse_documents, data_file)

        # Set the parsed data to the variable
        parsed_data = llama_parse_documents

    return parsed_data

def create_vector_database():
    """
    Creates a vector database using document loaders and embeddings.
    """
    # Call the function to either load or parse the data
    llama_parse_documents = load_or_parse_data()
    print(llama_parse_documents[0].text[:300])

    with open('data/output.md', 'a') as f:  # Open the file in append mode ('a')
        for doc in llama_parse_documents:
            f.write(doc.text + '\n')

    markdown_path = "./data/output.md"
    loader = UnstructuredMarkdownLoader(markdown_path)

    documents = loader.load()
    # Split loaded documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    print(f"length of documents loaded: {len(documents)}")
    print(f"total number of document chunks generated :{len(docs)}")

    # Initialize Embeddings
    embed_model = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")

    # Create and persist a Chroma vector database from the chunked documents
    vs = Chroma.from_documents(
        documents=docs,
        embedding=embed_model,
        persist_directory="chroma_db_llamaparse1",
        collection_name="rag"
    )

    print('Vector DB created successfully !')
    return vs, embed_model

@router.post("/llamaindex_query")
async def create_vector_db():
    try:
        vs, embed_model = create_vector_database()
        return {"message": "Vector DB created successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))