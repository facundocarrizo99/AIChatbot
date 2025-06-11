import os
import unittest

from app.models.factura import Factura
from app.services.factura_service import FacturaService
from app.controller.factura_controller import FacturaController
from app.utils.whatsapp_utils import send_document_message
from app import create_app

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
        factura = self.factura_service.obtener_factura_por_numero("0")
        factura.factura_to_pdf()
        assert (os.path.exists("factura_generada"), "El archivo PDF no fue creado")

    def test_send_document(self):
        current_dir = os.path.dirname(__file__)
        pdf_path = os.path.join(current_dir, "factura_generada.pdf")
        recipient_number = "541128234936"
        app = create_app()
        with app.app_context():
            response, status_code = send_document_message(recipient_number, pdf_path, "factura_generada.pdf")
            print(response.get_json())
            self.assertEqual(status_code, 200)
            self.assertEqual(response.get_json()["status"], "success")

if __name__ == '__main__':
    unittest.main()