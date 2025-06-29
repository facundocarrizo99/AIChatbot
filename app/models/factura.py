from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from app.models.cliente import Cliente
from app.models.monotributista import Monotributista
from jinja2 import Environment, FileSystemLoader
#import pdfkit
import os

class Producto:
    def __init__(self, nombre, precio_unitario, cantidad):
        self.nombre = nombre
        self.precio_unitario = precio_unitario
        self.cantidad = cantidad
        self.total = round(precio_unitario * cantidad, 2)

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "precio_unitario": self.precio_unitario,
            "cantidad": self.cantidad,
            "total": self.total
        }

class Factura:
    def __init__(self, items=None, actionToBeDone=None, issue_date=None, billed_period_from=None, billed_period_to=None, until=None, expiration_date=None, client=None):
        self.numero = None
        self.productos = []
        self.total = 0
        self.fecha = datetime.utcnow().isoformat()
        self.tipo_factura = None
        self.emisor = None
        self.cliente = None
        self.periodo_facturado_desde = None
        self.periodo_facturado_hasta = None
        self.fecha_vencimiento_pago = None
        self.condicion_venta = None #Contado - Transferencia - Tarejar
        self.cae = None
        self.fecha_vencimiento_cae = None


    def to_dict(self):
        return {
            "numero": self.numero,
            "fecha": self.fecha,
            "tipo_factura": self.tipo_factura,
            "emisor": self.emisor.to_dict_for_factura(),
            "cliente": self.cliente.to_dict(),
            "periodo_facturado_desde": self.periodo_facturado_desde,
            "periodo_facturado_hasta": self.periodo_facturado_hasta,
            "fecha_vencimiento_pago": self.fecha_vencimiento_pago,
            "condicion_venta": self.condicion_venta,
            "productos": [p.to_dict() for p in self.productos],
            "total": self.total,
            "cae": self.cae,
            "fecha_vencimiento_cae": self.fecha_vencimiento_cae
        }
    @staticmethod
    def from_dict(data):
        factura = Factura(items=data["productos"])
        factura.numero = data.get("numero")
        factura.fecha = data.get("fecha")
        factura.tipo_factura = data.get("tipo_factura")
        factura.emisor = Monotributista.from_dict(data["emisor"])
        factura.cliente = Cliente.from_dict(data["cliente"])
        factura.periodo_facturado_desde = data.get("periodo_facturado_desde")
        factura.periodo_facturado_hasta = data.get("periodo_facturado_hasta")
        factura.fecha_vencimiento_pago = data.get("fecha_vencimiento_pago")
        factura.condicion_venta = data.get("condicion_venta")
        factura.cae = data.get("cae")
        factura.fecha_vencimiento_cae = data.get("fecha_vencimiento_cae")
        return factura

    def completar_factura(self, monotributista, cliente, productos):
        self.emisor = monotributista
        self.cliente = cliente
        self.condicion_venta = 'Contado'
        self.tipo_factura = 'C'
        for producto in productos:
            self.productos.append(Producto(**producto))
        self.total = sum([p.precio_unitario for p in self.productos])
        if self.fecha_vencimiento_pago is None:
            self.fecha_vencimiento_pago = self.fecha
            self.periodo_facturado_desde = self.fecha
            self.periodo_facturado_hasta = self.fecha
        return self

    def factura_to_pdf(self):
        # Configurar entorno de plantilla
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        env = Environment(loader=FileSystemLoader(base_dir))
        template = env.get_template("factura_template.html")

        # Renderizar HTML
        html = template.render(
            emisor=self.emisor.to_dict_for_factura(),
            cliente=self.cliente.to_dict(),
            numero=int(self.numero),
            fecha=self.fecha,
            punto_venta=self.emisor.punto_venta,
            tipo_factura=self.tipo_factura,
            condicion_venta=self.condicion_venta,
            periodo_facturado_desde=self.periodo_facturado_desde,
            periodo_facturado_hasta=self.periodo_facturado_hasta,
            fecha_vencimiento_pago=self.fecha_vencimiento_pago,
            productos=self.productos,
            total=self.total,
            cae=self.cae,
            fecha_vencimiento_cae=self.fecha_vencimiento_cae
        )

        # Ruta a wkhtmltopdf (ajustar si es necesario)
        # config = pdfkit.configuration(
        #     wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
        # )
        #
        # # Generar el PDF
        # return pdfkit.from_string(html, "factura_generada.pdf", configuration=config)