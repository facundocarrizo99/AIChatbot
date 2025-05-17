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

    @pytest.fixture
    def service(self):
        return ClienteService(MONGO_URI, DB_NAME)

    def test_agregar_cliente(service):
        datos = {
            "nombreCompleto": "Cliente Directo",
            "telefono": "cliente_directo",
            "email": "cliente@directo.com",
            "condicionIva": "Monotributo",
            "cuit": "20999999991",
            "domicilio": "Calle 123",
            "razonSocial": "Cliente Directo S.A."
        }
        inserted_id = service.agregar_cliente(datos)
        assert ObjectId.is_valid(inserted_id)

    def test_buscar_cliente(service):
        cliente = service.buscar_por_telefono("cliente_directo")
        assert cliente is not None

    def test_modificar_cliente(service):
        modificado = service.modificar_cliente("cliente_directo", {"razonSocial": "Cliente Modificado"})
        assert modificado

    def test_eliminar_cliente(service):
        eliminado = service.eliminar_cliente("cliente_directo")
        assert eliminado