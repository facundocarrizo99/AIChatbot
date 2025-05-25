import logging

from app.controller.monotributista_controller import MonotributistaController
from app.models.factura import Factura
from app.models.monotributista import Monotributista
from app.services.arca_service import ARCAService
from app.services.factura_service import FacturaService
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
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

    def crear_pdf(self, numero):
        c = canvas.Canvas("factura_generada.pdf", pagesize=A4)
        width, height = A4

        def agregar_texto(texto, x, y, size=10, bold=False):
            c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
            c.drawString(x * mm, (height - y * mm), texto)

        def dibujar_linea(x1, y1, x2, y2):
            c.line(x1 * mm, (height - y1 * mm), x2 * mm, (height - y2 * mm))

        datos_factura = self.obtener_factura(numero)
        # Datos dinámicos
        emisor = self.monotributista_controller.obtener_por_cuit(datos_factura["cuit_emisor"])
        receptor = self.cliente_controller.obtener_por_cuit(datos_factura["cuit_cliente"])
        productos = datos_factura["productos"]

        # ================= ENCABEZADO GENERAL =================
        agregar_texto("ORIGINAL", 100, 10, size=12, bold=True)
        agregar_texto(emisor["nombreCompleto"], 10, 20, bold=True)
        agregar_texto(f"Razón Social: {emisor['nombreCompleto']}", 10, 25)
        agregar_texto(f"Domicilio Comercial: {emisor['domicilio']}", 10, 30)
        agregar_texto(f"Condición frente al IVA: {emisor['condicionIva']}", 10, 35)

        agregar_texto("C", 100, 20, size=18, bold=True)
        agregar_texto("COD. 011", 110, 25)
        agregar_texto("FACTURA", 120, 20, size=14, bold=True)
        agregar_texto(f"Punto de Venta: 00001", 120, 25)
        agregar_texto(f"Comp. Nro: {int(datos_factura['numero']):08d}", 120, 30)
        agregar_texto(f"Fecha de Emisión: {datos_factura['fecha'][:10]}", 120, 35)
        agregar_texto(f"CUIT: {emisor['cuit']}", 120, 40)
        agregar_texto(f"Ingresos Brutos: {emisor['cuit']}", 120, 45)
        agregar_texto(f"Fecha de Inicio de Actividades: {emisor.get('inicioActividades', '01/01/2000')}", 120, 50)

        # ================= DATOS DEL PERÍODO =================
        agregar_texto("Periodo Facturado Desde: 27/02/2025  Hasta: 27/02/2025  Fecha de Vto. para el pago: 27/02/2025", 10, 60, size=9)

        # ================= DATOS DEL RECEPTOR =================
        #agregar_texto(f"DNI: {receptor['dni']}", 10, 70)
        agregar_texto(f"Apellido y Nombre / Razón Social: {receptor['nombreCompleto']}", 10, 75)
        agregar_texto(f"Condición frente al IVA: {receptor['condicionIva']}", 10, 80)
        agregar_texto(f"Condición de venta: Contado", 10, 85)
        agregar_texto(f"Domicilio: {receptor['domicilio']}", 10, 90)

        # ================= TABLA DE PRODUCTOS =================
        table_y = 100
        columnas = ["Código", "Producto / Servicio", "Cantidad", "U. Medida", "Precio Unit.", "% Bonif.", "Imp. Bonif.", "Subtotal"]
        col_x = [10, 40, 90, 110, 130, 150, 170, 190]
        for i, col in enumerate(columnas):
            agregar_texto(col, col_x[i], table_y, size=8, bold=True)

        row_y = table_y + 5
        for prod in productos:
            agregar_texto(prod["nombre"], 40, row_y)
            agregar_texto(f"{prod['cantidad']:.2f}", 90, row_y)
            agregar_texto("unidades", 110, row_y)
            agregar_texto(f"{prod['precio_unitario']:.2f}", 130, row_y)
            agregar_texto("0.0", 150, row_y)
            agregar_texto("0.0", 170, row_y)
            agregar_texto(f"{prod['total']:.2f}", 190, row_y)
            row_y += 5

        # ================= TOTALES =================
        total = datos_factura["total"]
        agregar_texto(f"Subtotal: $ {total:.2f}", 150, row_y + 10)
        agregar_texto("Importe Otros Tributos: $ 0,00", 150, row_y + 15)
        agregar_texto(f"Importe Total: $ {total:.2f}", 150, row_y + 20, bold=True)

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