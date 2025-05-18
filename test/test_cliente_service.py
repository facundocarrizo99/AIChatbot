import unittest
import pytest
import os
from dotenv import load_dotenv
from app.services.cliente_service import ClienteService
from bson import ObjectId

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME_TEST")

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def setUp(self):
        self.cliente_servicio = ClienteService()

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