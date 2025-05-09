import os
from pymongo import MongoClient
from dotenv import load_dotenv
from db.userModel import Monotributista, ConsumidorFinal


# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la URI de MongoDB desde la variable de entorno
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

class UsuarioController:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.usuarios_collection = self.db["usuarios"]

    def agregar_usuario(self, usuario):
        usuario_dict = {
            "userId": usuario.userId,
            "password": usuario.password,
            "nombreCompleto": usuario.nombreCompleto,
            "tipo": usuario.tipo,
            "dni": usuario.dni,
            "cuit": usuario.cuit,
            "razonSocial": usuario.razonSocial,
            "categoria_monotributo": usuario.categoria_monotributo,
            "actividad": usuario.actividad,
            "domicilio": usuario.domicilio,
            "domicilioFiscal": usuario.domicilioFiscal,
            "telefono": usuario.telefono,
            "email": usuario.email,
            "condicionIva": usuario.condicionIva,
            "punto_venta": usuario.punto_venta
        }
        result = self.usuarios_collection.insert_one(usuario_dict)
        print(f"Usuario insertado con _id: {result.inserted_id}")
        return str(result.inserted_id)


# Ejemplo de uso:
if __name__ == "__main__":
    controller = UsuarioController(MONGO_URI, DB_NAME)

    # Crear un Monotributista
    monotributista = Monotributista(
        userId="juan1234",
        password="1234",
        nombreCompleto="Juan Random",
        telefono="1123457895",
        email="juanrandom@gmail.com",
        condicionIva="nose",
        cuit="1234",
        razonSocial="Juan Random",
        categoria_monotributo="A",
        actividad="Venta Tela",
        domicilioFiscal="Calle Random 1234",
        punto_venta="1"
    )

    # Crear un Consumidor Final
    consumidor = ConsumidorFinal(
        userId="ana4567",
        password="5678",
        nombreCompleto="Ana Consumidor",
        telefono="1145678901",
        email="ana.consumidor@email.com",
        condicionIva="Final",
        dni="40123456",
        domicilio="Calle Real 456"
    )

    # Agregar usuarios a la base de datos
    controller.agregar_usuario(monotributista)
    controller.agregar_usuario(consumidor)