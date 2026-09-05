from fastapi import FastAPI
# Path is used to work with file paths in a clean and cross-platform way.
from pathlib import Path

# PyPDFLoader reads and extracts text from PDF files.
from langchain_community.document_loaders import PyPDFLoader

# RecursiveCharacterTextSplitter breaks large documents into smaller chunks.
from langchain_text_splitters import RecursiveCharacterTextSplitter

# OpenAIEmbeddings converts text into numerical vectors (embeddings).
from langchain_community.embeddings import OpenAIEmbeddings

# os is used here to read environment variables,
# such as our OPENAI_API_KEY.
import os

# Loads variables from a .env file into the environment.
from dotenv import load_dotenv

# QdrantClient is used to connect to our Qdrant vector database.
from qdrant_client import QdrantClient

# QdrantVectorStore connects LangChain with Qdrant
# and allows us to store and search document embeddings.
from langchain_qdrant import QdrantVectorStore

from Routes.rag_route import router
# ---------------------------------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------

# Reads the .env file and loads variables such as:
# OPENAI_API_KEY=your_api_key
load_dotenv()


# ---------------------------------------------------------
# 2. DEFINE THE PDF FILE PATH
# ---------------------------------------------------------

# Path to the PDF that we want to process.
pdf_path = Path("Data/data.pdf")


# ---------------------------------------------------------
# 3. LOAD THE PDF
# ---------------------------------------------------------

# Create a PDF loader.
# PyPDFLoader reads the PDF and extracts its text.
loader = PyPDFLoader(pdf_path)

# Load the PDF.
#
# The result is a list of LangChain Document objects.
# Each Document generally contains:
#   - page_content -> the actual text
#   - metadata     -> information such as page number/source
documents = loader.load()


# ---------------------------------------------------------
# 4. SPLIT THE PDF INTO SMALLER CHUNKS
# ---------------------------------------------------------

# Create a text splitter.
#
# chunk_size=1000:
# Each chunk will contain approximately 1000 characters.
#
# chunk_overlap=200:
# 200 characters from the previous chunk are
# repeated in the next chunk.
#
# Overlap helps preserve context between chunks.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# Split all the PDF documents into smaller pieces.
#
# Example:
#
# Original PDF
#      |
#      v
# Large document
#      |
#      v
# +---------+
# | Chunk 1 | 1000 characters
# +---------+
# | Chunk 2 | 1000 characters
# +---------+
# | Chunk 3 | 1000 characters
# +---------+
#
# These chunks will later be converted into embeddings.
chunks = text_splitter.split_documents(documents)


# ---------------------------------------------------------
# 5. CREATE THE EMBEDDING MODEL
# ---------------------------------------------------------

# OpenAIEmbeddings converts text into numerical vectors.
#
# For example:
#
# "Python is a programming language"
#              |
#              v
#       Embedding model
#              |
#              v
# [0.021, -0.342, 0.891, ...]
#
# These vectors allow us to perform semantic/vector searches.
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",

    # Get the OpenAI API key from the environment.
    #
    # The key should be stored in your .env file:
    #
    # OPENAI_API_KEY=your_api_key
    #
    # Never hard-code your API key directly in your Python file.
    api_key=os.getenv("OPENAI_API_KEY")
)


# ---------------------------------------------------------
# 6. CONNECT TO QDRANT
# ---------------------------------------------------------

# Create a Qdrant client.
#
# Qdrant is our vector database.
#
# Here we are assuming Qdrant is running locally
# on port 6333.
#
# Example:
#
# http://localhost:6333
#
client = QdrantClient(
    host="localhost",
    port=6333
)


# ---------------------------------------------------------
# 7. STORE DOCUMENTS + EMBEDDINGS IN QDRANT
# ---------------------------------------------------------

# Create a Qdrant vector store from our PDF chunks.
#
# This step performs several things:
#
# 1. Takes every chunk
# 2. Sends the chunk to OpenAI's embedding model
# 3. Gets a vector/embedding for that chunk
# 4. Stores the vector in Qdrant
# 5. Stores the original document information/metadata
#
# The collection will be called "pdf_data".
#
# Conceptually:
#
# PDF
#  |
#  v
# Documents
#  |
#  v
# Chunks
#  |
#  v
# Embeddings
#  |
#  v
# Qdrant
#
vectorstore = QdrantVectorStore.from_documents(
    chunks,
    embeddings,

    # URL of the Qdrant server.
    url="http://localhost:6333",

    # Name of the collection inside Qdrant.
    collection_name="pdf_data",
)


# ---------------------------------------------------------
# 8. PRINT THE VECTOR STORE
# ---------------------------------------------------------

# Print the Qdrant vector store object.
#
# This mainly confirms that the vector store object
# was successfully created.


app = FastAPI()
app.include_router(router, prefix="/api/rag")

