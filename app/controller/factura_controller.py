import logging

from app.controller.monotributista_controller import MonotributistaController
from app.models.cliente import Cliente
from app.models.factura import Factura
from app.models.monotributista import Monotributista
from app.services.arca_service import ARCAService
from app.services.factura_service import FacturaService
from datetime import datetime
from app.controller.cliente_controller import ClienteController


class FacturaController:
    def __init__(self):
        self.service = FacturaService()
        self.monotributista_controler = MonotributistaController()
        self.arca_service = ARCAService()

    def crear_factura(self, datos_factura, tele_monotributista):
        monotributista = Monotributista(**self.monotributista_controler.obtener_por_telefono(tele_monotributista))
        # TODO: refactorizar para que no rompa y para que quede prolijo
        for cliente in monotributista.clientes:
            if cliente.nombreCompleto == datos_factura["nombreCompleto"]:
                cliente_factura = cliente
            elif cliente.cuit == datos_factura["cuit"]:
                cliente_factura = cliente
            elif cliente.email == datos_factura["email"]:
                cliente_factura = cliente
            elif cliente.telefono == datos_factura["telefono"]:
                cliente_factura = cliente
            else:
                cliente_factura = None

        factura = Factura.completar_factura(datos_factura, monotributista, cliente_factura)
        factura = self.arca_service.get_cae(factura)

        try:
            return self.service.crear_factura(factura)
        except Exception as e:
            logging.error(f"Error al crear factura: {e}")
            return None

    def obtener_factura(self, numero):
        try:
            return self.service.obtener_factura_por_numero(numero)
        except Exception as e:
            logging.error(f"Error al obtener factura: {e}")
            return None

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