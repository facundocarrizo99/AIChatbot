from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from app.models.cliente import Cliente
from app.models.monotributista import Monotributista

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
        c = canvas.Canvas("factura_generada.pdf", pagesize=A4)
        width, height = A4

        def agregar_texto(texto, x, y, size=10, bold=False):
            c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
            c.drawString(x * mm, (height - y * mm), texto)

        def dibujar_linea(x1, y1, x2, y2):
            c.line(x1 * mm, (height - y1 * mm), x2 * mm, (height - y2 * mm))

        emisor = self.emisor
        receptor = self.cliente
        productos = self.productos

        # ================= ENCABEZADO =================
        agregar_texto("ORIGINAL", 10, 10, size=10, bold=True)

        agregar_texto("C", 100, 20, size=18, bold=True)
        agregar_texto("COD. 011", 100, 25)
        agregar_texto("FACTURA", 100, 30, size=14, bold=True)

        agregar_texto(f"Punto de Venta: 00001", 100, 35)
        agregar_texto(f"Comp. Nro: {int(self.numero):08d}", 100, 40)
        agregar_texto(f"Fecha de Emisión: {self.fecha[:10]}", 100, 45)
        agregar_texto(f"CUIT: {emisor.cuit}", 100, 50)
        agregar_texto(f"Ingresos Brutos: {emisor.cuit}", 100, 55)
        agregar_texto(f"Fecha de Inicio de Actividades: {getattr(emisor, 'inicioActividades', '01/01/2000')}", 100, 60)

        # ================= DATOS DEL EMISOR =================
        agregar_texto(emisor.nombreCompleto, 10, 20, bold=True)
        agregar_texto(emisor.domicilio, 10, 25)
        agregar_texto(f"Condición frente al IVA: {emisor.condicionIva}", 10, 30)

        dibujar_linea(10, 65, 200, 65)

        # ================= PERÍODO =================
        agregar_texto(
            f"Periodo Facturado Desde: {self.periodo_facturado_desde[:10]}  Hasta: {self.periodo_facturado_hasta[:10]}  Fecha de Vto. para el pago: {self.fecha_vencimiento_pago[:10]}",
            10, 70, size=9)

        dibujar_linea(10, 75, 200, 75)

        # ================= CLIENTE =================
        agregar_texto(f"Apellido y Nombre / Razón Social: {receptor.nombreCompleto}", 10, 80)
        agregar_texto(f"Condición frente al IVA: {receptor.condicionIva}", 10, 85)
        agregar_texto(f"Domicilio: {receptor.domicilio}", 10, 90)
        agregar_texto(f"Condición de venta: {self.condicion_venta}", 10, 95)

        dibujar_linea(10, 100, 200, 100)

        # ================= TABLA DE PRODUCTOS =================
        table_y = 105
        columnas = ["Código", "Producto / Servicio", "Cantidad", "U. Medida", "Precio Unit.", "% Bonif.",
                    "Imp. Bonif.", "Subtotal"]
        col_x = [10, 40, 90, 110, 130, 150, 170, 190]

        for i, col in enumerate(columnas):
            agregar_texto(col, col_x[i], table_y, size=8, bold=True)

        row_y = table_y + 5
        for prod in productos:
            agregar_texto(prod.get("codigo", ""), 10, row_y)
            agregar_texto(prod.get("nombre", ""), 40, row_y)
            agregar_texto(f"{prod.get('cantidad', 0):.2f}", 90, row_y)
            agregar_texto(prod.get("unidad", "unidades"), 110, row_y)
            agregar_texto(f"{prod.get('precio_unitario', 0):.2f}", 130, row_y)
            agregar_texto("0.0", 150, row_y)
            agregar_texto("0.0", 170, row_y)
            agregar_texto(f"{prod.get('total', 0):.2f}", 190, row_y)
            row_y += 5

        dibujar_linea(10, row_y + 3, 200, row_y + 3)

        # ================= TOTALES =================
        agregar_texto(f"Subtotal: $ {self.total:.2f}", 150, row_y + 10)
        agregar_texto("Importe Otros Tributos: $ 0,00", 150, row_y + 15)
        agregar_texto(f"Importe Total: $ {self.total:.2f}", 150, row_y + 20, bold=True)


        return c.save()