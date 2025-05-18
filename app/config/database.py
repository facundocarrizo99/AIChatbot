import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener las variables de entorno
MONGODB_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
DB_NAME_TEST = os.getenv("DB_NAME_TEST")

# Conectar a MongoDB
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
db_test = client[DB_NAME_TEST]

def get_test_collection():
    return db["test"]