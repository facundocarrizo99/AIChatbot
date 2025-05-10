import os
import logging
from pymongo import MongoClient
from bson import ObjectId  # Importar ObjectId para manejar _id de MongoDB
from dotenv import load_dotenv
from app.db.models import Monotributista, ConsumidorFinal

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

    def eliminar_usuario(self, usuario_id):
        """Elimina un usuario por su _id de MongoDB."""
        try:
            result = self.usuarios_collection.delete_one({"_id": ObjectId(usuario_id)})
            if result.deleted_count > 0:
                logging.info(f"Usuario con _id '{usuario_id}' eliminado correctamente.")
                return True
            else:
                logging.warning(f"No se encontró un usuario con _id '{usuario_id}'.")
                return False
        except Exception as e:
            logging.error(f"Error al eliminar usuario: {e}")
            return False

    def modificar_usuario(self, usuario_id, nuevos_datos):
        """
        Modifica los datos de un usuario.
        
        Args:
            usuario_id (str): El _id del usuario a modificar.
            nuevos_datos (dict): Un diccionario con los datos a modificar.
        """
        try:
            result = self.usuarios_collection.update_one(
                {"_id": ObjectId(usuario_id)},
                {"$set": nuevos_datos}
            )
            if result.modified_count > 0:
                logging.info(f"Usuario con _id '{usuario_id}' modificado correctamente.")
                return True
            else:
                logging.warning(f"No se modificó el usuario con _id '{usuario_id}'. Verifique los datos.")
                return False
        except Exception as e:
            logging.error(f"Error al modificar usuario: {e}")
            return False

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
