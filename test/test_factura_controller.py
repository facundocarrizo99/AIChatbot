import unittest
from app.controller.factura_controller import FacturaController
from app.models.cliente import Cliente
from app.models.monotributista import Monotributista
from app.services.arca_service import ARCAService
from app.models.factura import Factura


class TestFacturaController(unittest.TestCase):
    def setUp(self):
        self.factura_controller = FacturaController()
        self.arca_service = ARCAService()
        # Datos de prueba
        self.factura_test = {"_id": {"$oid": "6861dece641d2537d95f9dcf"}, "numero": {"$numberInt": "1"},
                             "fecha": "2025-06-30T00:43:31.124384", "tipo_factura": "C",
                             "emisor": {"nombreCompleto": "facundo carrizo", "telefono": "541134031128",
                                        "email": "facundocarrizo99@gmail.com", "condicionIva": None,
                                        "cuit": "20422148281", "domicilio": "urquiza 2271, florida",
                                        "razonSocial": None, "categoria_monotributo": "A", "actividad": "servicios",
                                        "punto_venta": {"$numberInt": "3"}, "ingresos_brutos": "20422148281",
                                        "fecha_inicio_actividad": {"$date": {"$numberLong": "1704078000000"}}},
                             "cliente": {"nombreCompleto": "Leo Messi", "telefono": "+5491112345678",
                                         "email": "leomessi@gmail.com", "condicionIva": "Consumidor Final",
                                         "cuit": "20123456781",
                                         "domicilio": "campeones 1234, belgrano, buenos aires argentina"},
                             "periodo_facturado_desde": "2025-06-30T00:43:31.124384",
                             "periodo_facturado_hasta": "2025-06-30T00:43:31.124384",
                             "fecha_vencimiento_pago": "2025-06-30T00:43:31.124384", "condicion_venta": "Contado",
                             "productos": [{"nombre": "miel", "precio_unitario": {"$numberInt": "3000"},
                                            "cantidad": {"$numberInt": "1"}, "total": {"$numberInt": "3000"}}],
                             "total": {"$numberInt": "3000"}, "cae": "48631696241273",
                             "fecha_vencimiento_cae": "2025-07-10T00:43:31Z"}

    def test_generar_factura(self):
        factura = self.factura_controller.crear_factura(self.factura_test, "5491134031128")
        print(factura)
        assert isinstance(factura, Factura)

    def test_agregar_cae(self):
        factura = Factura(**self.factura_test)
        factura_con_cae = self.arca_service.agregar_cae(factura)
        assert factura_con_cae.cae == "22334455886699"

    def test_generar_pdf(self):
        monotributista = Monotributista(**self.factura_test['emisor'])
        cliente = Cliente(**self.factura_test['cliente'])
        factura = Factura()
        factura = Factura(factura, monotributista, cliente, self.factura_test['productos'])
        res = factura.factura_to_pdf()
        print(res)
        assert isinstance(res, str)

if __name__ == '__main__':
    unittest.main()
