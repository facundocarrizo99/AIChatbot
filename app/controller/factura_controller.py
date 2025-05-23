import logging
from app.services.factura_service import FacturaService
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from app.controller.cliente_controller import ClienteController
from app.controller.monotributista_controller import MonotributistaController

class FacturaController:
    def __init__(self):
        self.service = FacturaService()
        self.cliente_controller = ClienteController()
        self.monotributista_controller = MonotributistaController()

    def crear_factura(self, datos_factura):
        try:
            return self.service.crear_factura(datos_factura)
        except Exception as e:
            logging.error(f"Error al crear factura: {e}")
            return None

    def crear_pdf(self,datos_factura):
        c = canvas.Canvas("factura_generada.pdf", pagesize=A4)
        width, height = A4
        def agregar_texto(texto, x, y, size=10, bold=False):
            c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
            c.drawString(x * mm, (height - y * mm), texto)

        emisor = self.monotributista_controller.obtener_por_cuit(datos_factura["cuit_emisor"])
        receptor = self.cliente_controller.obtener_por_cuit(datos_factura["cuit_cliente"])

        # Encabezado
        agregar_texto("FACTURA C", 10, 10, size=14, bold=True)
        agregar_texto("COD. 011", 50, 10, size=10)

        # Datos del emisor
        agregar_texto(emisor["nombreCompleto"], 10, 20, bold=True)
        agregar_texto(emisor["domicilio"], 10, 25)

        # Datos del receptor
        agregar_texto("CARRIZO FACUNDO MARTIN", 10, 40, bold=True)
        agregar_texto("DNI: 42214828", 10, 45)
        agregar_texto("Condición frente al IVA: Consumidor Final", 10, 50)

        # Detalle del producto/servicio
        agregar_texto("Detalle", 10, 70, bold=True)
        agregar_texto("sesion de psicoterapia 12-2", 10, 75)
        agregar_texto("Cantidad: 1", 10, 80)
        agregar_texto("Precio Unitario: $25000,00", 10, 85)
        agregar_texto("Subtotal: $25000,00", 10, 90)
        agregar_texto("Importe Total: $25000,00", 10, 100, bold=True)

        # CAE y autorización
        agregar_texto("CAE N°: 75098916627090", 10, 120)
        agregar_texto("Fecha de Vto. de CAE: 09/03/2025", 10, 125)
        agregar_texto("Comprobante Autorizado", 10, 130)

        # Pie de página
        agregar_texto("Esta Agencia no se responsabiliza por los datos ingresados en el detalle de la operación", 10,
                      270, size=8)

        return c.save()
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