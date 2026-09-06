from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["vakil_vision"]

contracts_collection = db["contracts"]
analyses_collection = db["analyses"]

def initialize_database():
    contracts_collection.create_index("id", unique=True)
    analyses_collection.create_index("id")


def get_database():
    return db