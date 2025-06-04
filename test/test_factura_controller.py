import unittest
from app.controller.factura_controller import FacturaController
from app.services.arca_service import ARCAService
from app.models.factura import Factura


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.factura_controller = FacturaController()
        self.arca_service = ARCAService()
        # Datos de prueba
        self.factura_test = {
            "actionToBeDone": "invoice.add",
            "client": "Macarena Algo",
            "items": [
                {"nombre": "Producto A", "precio_unitario": 100.0, "cantidad": 2,"total":23},
                {"nombre": "Producto B", "precio_unitario": 50.0, "cantidad": 3,"total":40}
            ]
        }

    def test_generar_factura(self):
        factura = self.factura_controller.crear_factura(self.factura_test, "5491134031128")
        print(factura)
        assert isinstance(factura, Factura)

    def test_agregar_cae(self):
        factura = Factura(**self.factura_test)
        factura_con_cae = self.arca_service.agregar_cae(factura)
        assert factura_con_cae.cae=="22334455886699"

if __name__ == '__main__':
    unittest.main()
