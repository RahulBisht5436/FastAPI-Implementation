# os is used to read environment variables, such as OPENAI_API_KEY.
import os

# Loads variables from a .env file into the environment.
from dotenv import load_dotenv

# APIRouter groups related endpoints into a reusable route module.
from fastapi import APIRouter

# In LangChain 1.x, chain helpers live in langchain_classic (not langchain.chains).
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

# OpenAIEmbeddings converts text into vectors for similarity search.
from langchain_community.embeddings import OpenAIEmbeddings

# ChatPromptTemplate defines the system + user messages sent to the LLM.
from langchain_core.prompts import ChatPromptTemplate

# ChatOpenAI is the LangChain wrapper around OpenAI's chat models.
from langchain_openai import ChatOpenAI

# QdrantVectorStore connects LangChain to our Qdrant vector database.
from langchain_qdrant import QdrantVectorStore

from Models.rag_model import RAGModelQuery, RAGModelResponse

# ---------------------------------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------

# Reads the .env file and loads variables such as:
# OPENAI_API_KEY=your_api_key
load_dotenv()

router = APIRouter()


# ---------------------------------------------------------
# 2. SET UP EMBEDDINGS (must match the model used during indexing)
# ---------------------------------------------------------

# The same embedding model used in main.py when storing PDF chunks.
# If this model differs from the one used during ingestion, retrieval
# quality will be poor because query vectors won't align with stored vectors.
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.getenv("OPENAI_API_KEY"),
)


# ---------------------------------------------------------
# 3. CONNECT TO EXISTING QDRANT COLLECTION
# ---------------------------------------------------------

# from_existing_collection connects to a collection that was already
# populated by main.py — it does NOT re-ingest or re-embed documents.
vector_store = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="pdf_data",
    embedding=embeddings,
)


# ---------------------------------------------------------
# 4. CREATE RETRIEVER
# ---------------------------------------------------------

# The retriever performs similarity search: given a user question,
# it returns the k most relevant document chunks from Qdrant.
retriever = vector_store.as_retriever(search_kwargs={"k": 4})


# ---------------------------------------------------------
# 5. CREATE LLM AND PROMPT
# ---------------------------------------------------------

# temperature=0 keeps answers deterministic and grounded in context.
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# {context} is filled with retrieved chunks; {input} is the user's question.
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Answer the question using only the context below. "
        "If you don't know, say you don't know.\n\n{context}",
    ),
    ("human", "{input}"),
])


# ---------------------------------------------------------
# 6. BUILD THE RAG CHAIN
# ---------------------------------------------------------

# document_chain: stuffs retrieved chunks into the prompt and calls the LLM.
document_chain = create_stuff_documents_chain(llm, prompt)

# rag_chain: retrieve relevant chunks → pass them to document_chain → answer.
#
# Flow:
#   User question
#        ↓
#   Embed query → Qdrant similarity search (top-k chunks)
#        ↓
#   Prompt (context + question) → ChatOpenAI → answer
rag_chain = create_retrieval_chain(retriever, document_chain)


# ---------------------------------------------------------
# 7. RAG ENDPOINT
# ---------------------------------------------------------

@router.post("/")
async def rag(body: RAGModelQuery):
    # Run the full RAG pipeline for the user's question.
    # Returns a dict with "answer" (str) and "context" (list of Documents).
    result = rag_chain.invoke({"input": body.query})

    # Extract source file paths from each retrieved chunk's metadata.
    sources = [
        doc.metadata.get("source", "unknown")
        for doc in result.get("context", [])
    ]

    return RAGModelResponse(
        response=result["answer"],
        source=sources,
    )
