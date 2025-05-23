import os
import unittest
from app.services.factura_service import FacturaService
from app.controller.factura_controller import FacturaController

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.factura_service = FacturaService(True)
        self.factura_controller = FacturaController()
        # Datos de prueba
        self.factura_test = {
            "numero": "0",
            "fecha": "2025-05-18T14:00:00Z",
            "cuit_emisor": "20422148281",
            "cuit_cliente": "5491112341234",
            "productos": [
                {"nombre": "Producto A", "precio_unitario": 100.0, "cantidad": 2,"total":23},
                {"nombre": "Producto B", "precio_unitario": 50.0, "cantidad": 3,"total":40}
            ]
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
        self.factura_service.crear_factura(self.factura_test)
        factura = self.factura_service.obtener_factura_por_numero("0")
        assert factura is not None
        assert factura["cuit_cliente"] == "27112233445"

    def test_modificar_factura(self):
        self.factura_service.crear_factura(self.factura_test)
        modificado = self.factura_service.modificar_factura("0", {
            "cuit_cliente": "20999888777"
        })
        assert modificado
        factura = self.factura_service.obtener_factura_por_numero("0")
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
        self.factura_controller.crear_pdf(self.factura_test)
        assert (os.path.exists("factura_generada"), "El archivo PDF no fue creado")

if __name__ == '__main__':
    unittest.main()