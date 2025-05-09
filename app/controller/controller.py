import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
from db.models import Monotributista, ConsumidorFinal

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Cargar variables de entorno
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

class UsuarioController:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URI)
            self.db = self.client[DB_NAME]
            self.usuarios_collection = self.db["Usuario"]
            logging.info("Conexión a la base de datos exitosa.")
            self.agregar_usuario_ejemplo()
        except Exception as e:
            logging.error(f"Error de conexión a la base de datos: {e}")

    def agregar_usuario(self, usuario):
        try:
            usuario_dict = usuario.__dict__
            result = self.usuarios_collection.insert_one(usuario_dict)
            logging.info(f"Usuario insertado con _id: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logging.error(f"Error al insertar usuario: {e}")
            return None

    def agregar_usuario_ejemplo(self):
        """Agrega un usuario de ejemplo al iniciar la aplicación."""
        usuario_ejemplo = Monotributista(
            userId="ejemplo123",
            password="1234",
            nombreCompleto="Usuario Ejemplo",
            telefono="1100000000",
            email="ejemplo@correo.com",
            condicionIva="Inscripto",
            cuit="20304050607",
            razonSocial="Ejemplo S.A.",
            categoria_monotributo="A",
            actividad="Comercio",
            domicilioFiscal="Calle Ejemplo 123",
            punto_venta="1"
        )
        
        if self.usuarios_collection.find_one({"userId": "ejemplo123"}):
            logging.info("Usuario de ejemplo ya existe en la base de datos.")
        else:
            self.agregar_usuario(usuario_ejemplo)
            logging.info("Usuario de ejemplo agregado a la base de datos.")
