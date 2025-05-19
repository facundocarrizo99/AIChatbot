import unittest
from app.services.factura_service import FacturaService

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.factura_service = FacturaService(True)
        # Datos de prueba
        self.factura_test = {
            "numero": "F-TEST-001",
            "fecha": "2025-05-18T14:00:00Z",
            "cuit_emisor": "20304050607",
            "cuit_cliente": "27112233445",
            "productos": [
                {"nombre": "Producto A", "precio_unitario": 100.0, "cantidad": 2,"total":23},
                {"nombre": "Producto B", "precio_unitario": 50.0, "cantidad": 3,"total":40}
            ]
        }
        # Asegurarse de que la colección esté limpia
        self.factura_service.eliminar_factura({"numero": "F-TEST-001"})

    def test_agregar_factura(self):
        inserted_id = self.factura_service.crear_factura(self.factura_test)
        assert isinstance(inserted_id, str)
        factura = self.factura_service.obtener_factura_por_numero("F-TEST-001")
        assert factura is not None
        assert factura["numero"] == "F-TEST-001"

    def test_buscar_factura(self):
        self.factura_service.crear_factura(self.factura_test)
        factura = self.factura_service.obtener_factura_por_numero("F-TEST-001")
        assert factura is not None
        assert factura["cuit_cliente"] == "27112233445"

    def test_modificar_factura(self):
        self.factura_service.crear_factura(self.factura_test)
        modificado = self.factura_service.modificar_factura("F-TEST-001", {
            "cuit_cliente": "20999888777"
        })
        assert modificado
        factura = self.factura_service.obtener_factura_por_numero("F-TEST-001")
        assert factura["cuit_cliente"] == "20999888777"

    def test_eliminar_factura(self):
        self.factura_service.crear_factura(self.factura_test)
        eliminado = self.factura_service.eliminar_factura("F-TEST-001")
        assert eliminado
        factura = self.factura_service.obtener_factura_por_numero("F-TEST-001")
        assert factura is None

    def test_obtener_todas_las_facturas(self):
        self.factura_service.crear_factura(self.factura_test)
        facturas = self.factura_service.obtener_todas()
        assert isinstance(facturas, list)
        assert any(f["numero"] == "F-TEST-001" for f in facturas)


if __name__ == '__main__':
    unittest.main()