import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

# Cargar variables de entorno
load_dotenv()

# Configuración de MongoDB
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")

# Crear URL de conexión
MONGO_URL = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"

# Cliente MongoDB
client = MongoClient(MONGO_URL)

# Función para obtener la base de datos
def get_database(db_name: str) -> Database:
    """
    Obtiene una instancia de la base de datos MongoDB.
    """
    return client[db_name]

# Función para obtener una colección
def get_collection(db_name: str, collection_name: str) -> Collection:
    """
    Obtiene una instancia de una colección MongoDB.
    """
    db = get_database(db_name)
    return db[collection_name] 