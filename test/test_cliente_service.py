import unittest
import os
from dotenv import load_dotenv
from app.services.cliente_service import ClienteService

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME_TEST")

class TestClienteService(unittest.TestCase):
    def setUp(self):
        self.cliente_servicio = ClienteService(True)

    def test_agregar_cliente(self):
        datos = {
            "nombreCompleto": "Cliente Directo",
            "telefono": "cliente_directo",
            "email": "cliente@directo.com",
            "condicionIva": "Monotributo",
            "cuit": "20999999991",
            "domicilio": "Calle 123"
        }
        inserted_id = self.cliente_servicio.agregar_cliente(datos)
        assert isinstance(inserted_id, str)

    def test_buscar_cliente(self):
        cliente = self.cliente_servicio.buscar_por_telefono("cliente_directo")
        assert cliente is not None

    def test_modificar_cliente(self):
        modificado = self.cliente_servicio.modificar_cliente("cliente_directo", {"razonSocial": "Cliente Modificado"})
        assert modificado

    def test_eliminar_cliente(self):
        eliminado = self.cliente_servicio.eliminar_cliente("cliente_directo")
        assert eliminado