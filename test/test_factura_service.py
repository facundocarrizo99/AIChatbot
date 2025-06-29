import os
import unittest

from app.models.factura import Factura
from app.services.factura_service import FacturaService
from app.controller.factura_controller import FacturaController

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.factura_service = FacturaService()
        self.factura_controller = FacturaController()
        # Datos de prueba
        self.factura_test = {
            "numero": "0",
            "fecha": "2025-05-18T14:00:00Z",
            "cuit_emisor": "20422148281",
            "cuit_cliente": "23123412347",
            "productos": [
                {"nombre": "Producto A", "precio_unitario": 100.0, "cantidad": 2,"total":23},
                {"nombre": "Producto B", "precio_unitario": 50.0, "cantidad": 3,"total":40}
            ],
        }
        # Asegurarse de que la colección esté limpia
        self.factura_service.eliminar_factura({"numero": "0"})

    def test_agregar_factura(self):
        inserted_id = self.factura_service.crear_factura(self.factura_test)
        assert isinstance(inserted_id, str)
        factura = self.factura_service.obtener_factura_por_numero("0")
        assert factura is not None
        assert factura["numero"] == "0"

    def test_buscar_factura(self):
        #self.factura_service.crear_factura(self.factura_test)
        factura = self.factura_service.obtener_factura_por_numero("4")
        assert factura is not None
        assert factura["cuit_cliente"] == "23123412347"

    def test_modificar_factura(self):
        self.factura_service.crear_factura(self.factura_test)
        modificado = self.factura_service.modificar_factura("0", {
            "cuit_cliente": "20999888777"
        })
        assert modificado
        factura = self.factura_service.obtener_factura_por_numero("4")
        assert factura["cuit_cliente"] == "20999888777"

    def test_eliminar_factura(self):
        self.factura_service.crear_factura(self.factura_test)
        eliminado = self.factura_service.eliminar_factura("0")
        assert eliminado
        factura = self.factura_service.obtener_factura_por_numero("0")
        assert factura is None

    def test_obtener_todas_las_facturas(self):
        self.factura_service.crear_factura(self.factura_test)
        facturas = self.factura_service.obtener_todas()
        assert isinstance(facturas, list)
        assert any(f["numero"] == "0" for f in facturas)

    def test_generar_pdf(self):
        factura = self.factura_service.obtener_factura_por_numero(1)
        factura.factura_to_pdf()
        assert (os.path.exists("factura_generada"), "El archivo PDF no fue creado")

    def test_enviar_pdf(self):
        factura = self.factura_service.obtener_factura_por_numero(1)
        self.factura_controller.crear_pdf_y_enviar(factura)
        #assert (os.path.exists("factura_generada"), "El archivo PDF no fue creado")

if __name__ == '__main__':
    unittest.main()