import asyncio
import logging

from app.controller.monotributista_controller import MonotributistaController
from app.models.cliente import Cliente
from app.models.factura import Factura
from app.models.monotributista import Monotributista
from app.services.arca_service import ARCAService
from app.services.factura_service import FacturaService
from app.utils import whatsapp_utils

# app/controller/factura_controller.py
from fastapi import APIRouter, HTTPException
from typing import Dict
from app.services.arca_service import InvoiceService

router = APIRouter()
invoice_service = InvoiceService()


@router.post("/api/invoices/request-cae")
async def request_cae(invoice_data: Dict):
    """
    Request CAE for an invoice

    Expected invoice_data format:
    {
        "tipo_cbte": int,  # 1: Factura A, 6: Factura B
        "punto_vta": int,  # Punto de venta
        "cbte_nro": int,   # Número de comprobante
        "importe_total": float  # Total amount
        # ... other invoice details
    }
    """
    try:
        result = invoice_service.request_cae(invoice_data)
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Unknown error'))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class FacturaController:
    def __init__(self):
        self.service = FacturaService()
        self.monotributista_controler = MonotributistaController()
        self.arca_service = ARCAService()

    def crear_factura(self, tele_monotributista, cliente, productos):
        monotributista = Monotributista.from_dict(self.monotributista_controler.obtener_por_telefono(tele_monotributista))
        cliente = monotributista.buscar_clientes_por_valor(cliente)[0]

        factura = Factura()
        factura = factura.completar_factura(monotributista, cliente, productos)
        factura = self.arca_service.get_cae(factura)

        try:
            self.service.crear_factura(factura)
            asyncio.create_task(self.crear_pdf_y_enviar(factura))
            return factura
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

    def crear_pdf_y_enviar(self, factura):
        pdf = '/Users/facundocarrizo/Downloads/factura_generada.pdf'
        whatsapp_utils.send_document_message(factura.emisor.telefono, pdf, "factura-20250611-0001.pdf")

