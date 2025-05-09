import os
import logging
from enum import Enum
from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Flask, jsonify

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Cargar variables de entorno
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# =======================
# Modelos de Usuario
# =======================
class TipoUsuario(Enum):
    MONOTRIBUTISTA = "Monotributista"
    CONSUMIDOR_FINAL = "ConsumidorFinal"

class Usuario:
    def __init__(self, userId, password, nombreCompleto, tipo, telefono, email, condicionIva):
        self.userId = userId
        self.password = password
        self.nombreCompleto = nombreCompleto
        self.tipo = tipo.value
        self.telefono = telefono
        self.email = email
        self.condicionIva = condicionIva

class Monotributista(Usuario):
    def __init__(self, userId, password, nombreCompleto, telefono, email, condicionIva,
                 cuit, razonSocial, categoria_monotributo, actividad, domicilioFiscal, punto_venta):
        super().__init__(userId, password, nombreCompleto, TipoUsuario.MONOTRIBUTISTA, telefono, email, condicionIva)
        self.dni = None
        self.cuit = cuit
        self.razonSocial = razonSocial
        self.categoria_monotributo = categoria_monotributo
        self.actividad = actividad
        self.domicilio = None
        self.domicilioFiscal = domicilioFiscal
        self.punto_venta = punto_venta

class ConsumidorFinal(Usuario):
    def __init__(self, userId, password, nombreCompleto, telefono, email, condicionIva,
                 dni, domicilio):
        super().__init__(userId, password, nombreCompleto, TipoUsuario.CONSUMIDOR_FINAL, telefono, email, condicionIva)
        self.dni = dni
        self.cuit = None
        self.razonSocial = None
        self.categoria_monotributo = None
        self.actividad = None
        self.domicilio = domicilio
        self.domicilioFiscal = None
        self.punto_venta = None

# =======================
# Controlador de Usuarios (MongoDB)
# =======================
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

# =======================
# Configuración de Flask
# =======================
app = Flask(__name__)
controller = UsuarioController()

@app.route("/agregar_monotributista", methods=["GET"])
def agregar_monotributista():
    monotributista = Monotributista(
        userId="juan1234",
        password="1234",
        nombreCompleto="Juan Random",
        telefono="1123457895",
        email="juanrandom@gmail.com",
        condicionIva="Inscripto",
        cuit="123456789",
        razonSocial="Juan Random",
        categoria_monotributo="A",
        actividad="Venta Tela",
        domicilioFiscal="Calle Random 1234",
        punto_venta="1"
    )
    result = controller.agregar_usuario(monotributista)
    return jsonify({"resultado": result})

@app.route("/agregar_consumidor", methods=["GET"])
def agregar_consumidor():
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
    result = controller.agregar_usuario(consumidor)
    return jsonify({"resultado": result})

# =======================
# Iniciar Servidor Flask
# =======================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)