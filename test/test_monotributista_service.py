import unittest
import pytest
import os
from dotenv import load_dotenv
from app.services.monotributista_service import MonotributistaService
from bson import ObjectId

monotribustistaService = MonotributistaService()

class MyTestCase(unittest.TestCase): # add assertion here
    def test_agregar_monotributista(self):
        datos = {
            "nombreCompleto": "Juan Test",
            "telefono": "test_telefono",
            "email": "test@email.com",
            "condicionIva": "Inscripto",
            "cuit": "20999999998",
            "domicilio": "Test 123",
            "razonSocial": "Test S.A.",
            "categoria_monotributo": "B",
            "actividad": "Servicios",
            "punto_venta": "002"
        }
        inserted_id = monotribustistaService.agregar_monotributista(datos)
        assert isinstance(inserted_id, str)

    def test_buscar_por_telefono(self):
        monotributista = monotribustistaService.buscar_por_telefono("test_telefono")
        assert monotributista is not None
        assert monotributista["nombreCompleto"] == "Juan Test"

    def test_modificar_monotributista(self):
        modificado = monotribustistaService.modificar_monotributista("test_telefono", {"razonSocial": "Nueva Razón"})
        assert modificado

    def test_agregar_cliente(self):
        cliente_data = {
            "nombreCompleto": "Cliente Uno",
            "telefono": "cliente_test",
            "email": "cliente@uno.com",
            "condicionIva": "Consumidor Final",
            "cuit": "20999999990",
            "domicilio": "Cliente 123"
        }
        result = monotribustistaService.agregar_cliente_a_monotributista("test_telefono", cliente_data)
        assert result

    def test_modificar_cliente(self):
        modificado = monotribustistaService.modificar_cliente_de_monotributista(
            "test_telefono",
            {"telefono": "cliente_test"},
            {"nombreCompleto": "Cliente Uno Actualizado"}
        )
        assert modificado

    def test_eliminar_monotributista(self):
        eliminado = monotribustistaService.eliminar_monotributista("test_telefono")
        assert eliminado