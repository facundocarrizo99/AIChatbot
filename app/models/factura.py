from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


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
    def __init__(self, items, actionToBeDone=None, issue_date=None, billed_period_from=None, billed_period_to=None, until=None, expiration_date=None, client=None):
        self.numero = None
        self.productos = [p.to_dict() if isinstance(p, Producto) else p for p in items]
        self.total = sum([p["total"] for p in self.productos])
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
            "productos": self.productos,
            "total": self.total,
            "cae": self.cae,
            "fecha_vencimiento_cae": self.fecha_vencimiento_cae
        }

    def completar_factura(self, monotributista, cliente):
        self.emisor = monotributista
        self.cliente = cliente
        self.condicion_venta = 'Contado'
        self.tipo_factura = 'C'
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

        # ================= ENCABEZADO GENERAL =================
        agregar_texto("ORIGINAL", 100, 10, size=12, bold=True)
        agregar_texto(emisor.nombreCompleto, 10, 20, bold=True)
        agregar_texto(f"Razón Social: {emisor.nombreCompleto}", 10, 25)
        agregar_texto(f"Domicilio Comercial: {emisor.domicilio}", 10, 30)
        agregar_texto(f"Condición frente al IVA: {emisor.condicionIva}", 10, 35)

        agregar_texto("C", 100, 20, size=18, bold=True)
        agregar_texto("COD. 011", 110, 25)
        agregar_texto("FACTURA", 120, 20, size=14, bold=True)
        agregar_texto(f"Punto de Venta: 00001", 120, 25)
        agregar_texto(f"Comp. Nro: {int(self.numero):08d}", 120, 30)
        agregar_texto(f"Fecha de Emisión: {self.fecha[:10]}", 120, 35)
        agregar_texto(f"CUIT: {emisor.cuit}", 120, 40)
        agregar_texto(f"Ingresos Brutos: {emisor.cuit}", 120, 45)
        agregar_texto(f"Fecha de Inicio de Actividades: {getattr(emisor, 'inicioActividades', '01/01/2000')}", 120,
                      50)

        # ================= DATOS DEL PERÍODO =================
        agregar_texto(
            "Periodo Facturado Desde: 27/02/2025  Hasta: 27/02/2025  Fecha de Vto. para el pago: 27/02/2025", 10,
            60, size=9)

        # ================= DATOS DEL RECEPTOR =================
        agregar_texto(f"Apellido y Nombre / Razón Social: {receptor.nombreCompleto}", 10, 75)
        agregar_texto(f"Condición frente al IVA: {receptor.condicionIva}", 10, 80)
        agregar_texto(f"Condición de venta: Contado", 10, 85)
        agregar_texto(f"Domicilio: {receptor.domicilio}", 10, 90)

        # ================= TABLA DE PRODUCTOS =================
        table_y = 100
        columnas = ["Código", "Producto / Servicio", "Cantidad", "U. Medida", "Precio Unit.", "% Bonif.",
                    "Imp. Bonif.", "Subtotal"]
        col_x = [10, 40, 90, 110, 130, 150, 170, 190]
        for i, col in enumerate(columnas):
            agregar_texto(col, col_x[i], table_y, size=8, bold=True)

        row_y = table_y + 5
        for prod in productos:
            agregar_texto(getattr(prod, "codigo", ""), 10, row_y)
            agregar_texto(prod.nombre, 40, row_y)
            agregar_texto(f"{prod.cantidad:.2f}", 90, row_y)
            agregar_texto(getattr(prod, "unidad", "unidades"), 110, row_y)
            agregar_texto(f"{prod.precio_unitario:.2f}", 130, row_y)
            agregar_texto("0.0", 150, row_y)
            agregar_texto("0.0", 170, row_y)
            agregar_texto(f"{prod.total:.2f}", 190, row_y)
            row_y += 5

        # ================= TOTALES =================
        agregar_texto(f"Subtotal: $ {self.total:.2f}", 150, row_y + 10)
        agregar_texto("Importe Otros Tributos: $ 0,00", 150, row_y + 15)
        agregar_texto(f"Importe Total: $ {self.total:.2f}", 150, row_y + 20, bold=True)

        return c.save()