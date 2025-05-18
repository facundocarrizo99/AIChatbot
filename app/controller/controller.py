import os
import logging
from pymongo import MongoClient
from bson import ObjectId  # Importar ObjectId para manejar _id de MongoDB
from dotenv import load_dotenv
from app.models.monotributista import Monotributista

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Cargar variables de entorno
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

from app.models.usuario import Usuario
#from app.views.usuario_view import UsuarioView

from app.controller.monotributista_controller import MonotributistaController
from app.controller.cliente_controller import ClienteController

class UsuarioController:
    def __init__(self, mongo_uri, db_name):
        self.monotributista_controller = MonotributistaController(mongo_uri, db_name)
        self.cliente_controller = ClienteController()
    def __init__(self, mongo_uri, db_name):
        self.usuario_model = Usuario(mongo_uri, db_name)
        self.view = UsuarioView()
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URI)
            self.db = self.client[DB_NAME]
            self.usuarios_collection = self.db["Usuario"]
            logging.info("Conexión a la base de datos exitosa.")
            #self.agregar_usuario_ejemplo()
        except Exception as e:
            logging.error(f"Error de conexión a la base de datos: {e}")

    def agregar_usuario(self, usuario):
        try:
            # Verificar si el usuario ya existe por teléfono o CUIT
            usuario_existente = self.usuarios_collection.find_one({
                "$or": [
                    {"telefono": usuario.telefono},
                    {"cuit": usuario.cuit}
                ]
            })

            if usuario_existente:
                logging.info("El usuario ya existe en la colección.")
                return str(usuario_existente.get("_id"))

            # Insertar el nuevo usuario
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

    def modificar_usuario(self, telefono, nuevos_datos):
        try:
            result = self.usuarios_collection.update_one(
                {"telefono": telefono},
                {"$set": nuevos_datos}
            )
            if result.modified_count > 0:
                logging.info(f"Usuario con el telefono '{telefono}' modificado correctamente.")
                return True
            else:
                logging.warning(f"No se modificó el usuario con telefono '{telefono}'. Verifique los datos.")
                return False
        except Exception as e:
            logging.error(f"Error al modificar usuario: {e}")
            return False
        
    def agregar_cliente_a_monotributista(self, telefono, cliente):
        """
        Agrega un cliente a la lista de clientes de un Monotributista.
        - telefono: El telefono del Monotributista (str).
        - cliente_data: Diccionario con los datos del cliente.
        """
        try:
            # Verificar que el Monotributista existe
            monotributista = self.usuarios_collection.find_one({"telefono": telefono})
            if not monotributista or monotributista.get("categoria_monotributo") is None:
                logging.error("El usuario no es un Monotributista o no existe.")
                return False
            # Verificar si el cliente ya existe en la lista del Monotributista
            if any(c.get("cuit") == cliente.cuit or c.get("email") == cliente.email for c in monotributista.get("clientes", [])):
                logging.info("El cliente ya existe en la lista del Monotributista.")
                return True

            # Agregar el cliente directamente a la lista del Monotributista
            self.usuarios_collection.update_one(
                {"telefono": telefono},
                {"$addToSet": {"clientes": cliente}}  # Guardar el cliente directamente
            )

            logging.info("Cliente agregado a la lista del Monotributista.")
            return True

        except Exception as e:
            logging.error(f"Error al agregar cliente al Monotributista: {e}")
            return False
    def agregar_cliente_a_monotributista(self, telefono, cliente):
        """
        Agrega un cliente a la lista de clientes de un Monotributista.
        - telefono: El telefono del Monotributista (str).
        - cliente_data: Diccionario con los datos del cliente.
        """
        try:
            # Verificar que el Monotributista existe
            monotributista = self.usuarios_collection.find_one({"telefono": telefono})
            if not monotributista or monotributista.get("categoria_monotributo") is None:
                logging.error("El usuario no es un Monotributista o no existe.")
                return False

            # Verificar si el cliente ya existe en la lista del Monotributista
            if any(c.get("cuit") == cliente.cuit or c.get("email") == cliente.email for c in monotributista.get("clientes", [])):
                logging.info("El cliente ya existe en la lista del Monotributista.")
                return True

            # Agregar el cliente directamente a la lista del Monotributista
            self.usuarios_collection.update_one(
                {"telefono": telefono},
                {"$addToSet": {"clientes": cliente}}  # Guardar el cliente directamente
            )
            logging.info("Cliente agregado a la lista del Monotributista.")
            return True

        except Exception as e:
            logging.error(f"Error al agregar cliente al Monotributista: {e}")
            return False

    def buscar_cliente_por_nombre(self, telefono, nombre_completo):
        return self._buscar_cliente(telefono, {"nombreCompleto": nombre_completo})

    def buscar_cliente_por_email(self, telefono, email):
        return self._buscar_cliente(telefono, {"email": email})

    def buscar_cliente_por_cuit(self, telefono, cuit):
        return self._buscar_cliente(telefono, {"cuit": cuit})

    def buscar_cliente_por_telefono(self, telefono, telefonoc):
        return self._buscar_cliente(telefono, {"telefono": telefonoc})

    def buscar_cliente_por_domicilio(self, telefono, domicilio):
        return self._buscar_cliente(telefono, {"domicilio": domicilio})

    def _buscar_cliente(self, telefono, filtro):
        try:
            # Verificar que el Monotributista existe
            monotributista = self.usuarios_collection.find_one({"telefono": telefono})
            if not monotributista or monotributista.get("categoria_monotributo") is None:
                logging.error("El usuario no es un Monotributista o no existe.")
                return None

            # Buscar el cliente en la lista de clientes del Monotributista
            clientes = monotributista.get("clientes", [])
            for cliente in clientes:
                if any(cliente.get(key) == value for key, value in filtro.items()):
                    logging.info(f"Cliente encontrado: {cliente}")
                    return cliente

            logging.warning("Cliente no encontrado en la lista del Monotributista.")
            return None

        except Exception as e:
            logging.error(f"Error al buscar cliente del Monotributista: {e}")
            return None
    
    def modificar_cliente_de_monotributista(self, telefono, cliente_identificador, nuevos_datos):
        """
        Modifica un cliente de la lista de clientes de un Monotributista.
        - monotributista_id: El _id del Monotributista (str).
        - cliente_identificador: Diccionario con cualquier atributo del cliente (ej: {"email": "cliente@correo.com"}).
        - nuevos_datos: Diccionario con los atributos a modificar del cliente.
        """
        try:
            # Verificar que el Monotributista existe
            monotributista = self.usuarios_collection.find_one({"telefono": telefono})
            if not monotributista or monotributista.get("categoria_monotributo") is None:
                logging.error("El usuario no es un Monotributista o no existe.")
                return False

            # Buscar el cliente en la lista de clientes del Monotributista
            clientes = monotributista.get("clientes", [])
            cliente_encontrado = None

            for cliente in clientes:
                if any(cliente.get(key) == value for key, value in cliente_identificador.items()):
                    cliente_encontrado = cliente
                    break

            if not cliente_encontrado:
                logging.error("El cliente no está en la lista del Monotributista.")
                return False

            # Actualizar los datos del cliente encontrado
            for key, value in nuevos_datos.items():
                cliente_encontrado[key] = value

            # Actualizar la lista de clientes en la base de datos
            self.usuarios_collection.update_one(
                {"telefono": telefono},
                {"$set": {"clientes": clientes}}
            )
            logging.info("Cliente modificado correctamente.")
            return True

        except Exception as e:
            logging.error(f"Error al modificar cliente del Monotributista: {e}")
            return False
    
    def agregar_usuario_ejemplo(self):
        """Agrega un usuario de ejemplo al iniciar la aplicación."""
        usuario_ejemplo = Monotributista(
            nombreCompleto="Usuario Ejemplo",
            telefono="1100000000",
            email="ejemplo@correo.com",
            condicionIva="Inscripto",
            cuit="20304050607",
            domicilio="Ejemplo 1223",
            razonSocial="Ejemplo S.A.",
            categoria_monotributo="A",
            actividad="Comercio",
            punto_venta="1"
        )
        
        if self.usuarios_collection.find_one({"cuit": "20304050607"}):
            logging.info("Usuario de ejemplo ya existe en la base de datos.")
        else:
            self.agregar_usuario(usuario_ejemplo)
            logging.info("Usuario de ejemplo agregado a la base de datos.") 
