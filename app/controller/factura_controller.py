import logging
from multiprocessing import Process

from app.controller.monotributista_controller import MonotributistaController
from app.models.factura import Factura
from app.models.monotributista import Monotributista
from app.services.arca_service import ARCAService
from app.services.factura_service import FacturaService
from app.utils import whatsapp_utils

class FacturaController:
    def __init__(self):
        self.service = FacturaService()
        self.monotributista_controller = MonotributistaController()
        self.arca_service = ARCAService()

    def crear_factura(self, tele_monotributista, cliente, productos):
        monotributista = Monotributista.from_dict(self.monotributista_controller.obtener_por_telefono(tele_monotributista))
        cliente = monotributista.buscar_clientes_por_valor(cliente)[0]

        factura = Factura()
        factura = factura.completar_factura(monotributista, cliente, productos)

        try:
            res = self.service.crear_factura(factura)
            Process(target=self.issue_invoice, args=(factura,)).start()
            return res
        except Exception as e:
            logging.error(f"Error al crear factura: {e}")
            return e

    def obtener_factura(self, numero):
        try:
            return self.service.obtener_factura_por_numero(numero)
        except Exception as e:
            logging.error(f"Error al obtener factura: {e}")
            return e

    def eliminar_factura(self, numero):
        try:
            return self.service.eliminar_factura(numero)
        except Exception as e:
            logging.error(f"Error al eliminar factura: {e}")
            return False

    def modificar_factura(self, numero, nuevos_datos):
        try:
            return self.service.modificar_factura(numero, nuevos_datos)
        except Exception as e:
            logging.error(f"Error al modificar factura: {e}")
            return False

    def obtener_todas_las_facturas(self):
        try:
            return self.service.obtener_todas()
        except Exception as e:
            logging.error(f"Error al obtener todas las facturas: {e}")
            return []

    def issue_invoice(self, factura):
        factura = self.arca_service.agregar_cae(factura)
        self.service.modificar_factura(factura.numero, factura.to_dict())
        pdf = factura.factura_to_pdf()
        whatsapp_utils.send_document_message(factura.emisor.telefono, pdf[0], pdf[-1])
        whatsapp_utils.send_document_message(factura.cliente.telefono, pdf[0], pdf[-1])

