from datetime import datetime
#from formatter import NullWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

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
    def __init__(self, productos):
        self.numero = None
        self.productos = [p.to_dict() if isinstance(p, Producto) else p for p in productos]
        self.total = sum([p["total"] for p in self.productos])
        self.fecha = datetime.utcnow().isoformat()
        self.tipo_factura = None
        self.cuit_emisor = None
        self.nombre_emisor = None
        self.razon_social_emisor = None
        self.domicilio_emisor = None
        self.telefono_emisor = None
        self.condicion_iva_emisor = None
        self.punto_de_venta = None
        self.ingresos_brutos = None
        self.fecha_inicio_actividad_emisor = None
        self.periodo_facturado_desde = None
        self.periodo_facturado_hasta = None
        self.fecha_vencimiento_pago = None
        self.cuit_cliente = None
        self.nombre_cliente = None
        self.razon_social_cliente = None
        self.domicilio_cliente = None
        self.telefono_cliente = None
        self.condicion_iva_cliente = None
        self.condicion_venta = None #Contado - Transferencia - Tarejar
        self.cae = None
        self.fecha_vencimiento_cae = None

    def to_dict(self):
        return {
            "numero": self.numero,
            "fecha": self.fecha,
            "tipo_factura": self.tipo_factura,
            "cuit_emisor": self.cuit_emisor,
            "nombre_emisor": self.nombre_emisor,
            "razon_social_emisor": self.razon_social_emisor,
            "domicilio_emisor": self.domicilio_emisor,
            "telefono_emisor": self.telefono_emisor,
            "condicion_iva_emisor": self.condicion_iva_emisor,
            "punto_de_venta": self.punto_de_venta,
            "ingresos_brutos": self.ingresos_brutos,
            "fecha_inicio_actividad_emisor": self.fecha_inicio_actividad_emisor,
            "periodo_facturado_desde": self.periodo_facturado_desde,
            "periodo_facturado_hasta": self.periodo_facturado_hasta,
            "fecha_vencimiento_pago": self.fecha_vencimiento_pago,
            "cuit_cliente": self.cuit_cliente,
            "nombre_cliente": self.nombre_cliente,
            "razon_social_cliente": self.razon_social_cliente,
            "domicilio_cliente": self.domicilio_cliente,
            "telefono_cliente": self.telefono_cliente,
            "condicion_iva_cliente": self.condicion_iva_cliente,
            "condicion_venta": self.condicion_venta,
            "productos": self.productos,
            "total": self.total,
            "cae": self.cae,
            "fecha_vencimiento_cae": self.fecha_vencimiento_cae
        }

    def completar_factura(self, datos, monotributista, cliente):
        factura = Factura(**datos)
        factura.cuit_emisor = monotributista.cuit
        factura.nombre_emisor = monotributista.nombreCompleto
        factura.condicion_iva_emisor = monotributista.condicionIva
        factura.domicilio_emisor = monotributista.domicilio
        factura.fecha_inicio_actividad_emisor = monotributista.fecha_inicio_actividad #TODO: Tiene que solicitarse en cuando se registra
        factura.ingresos_brutos = monotributista.ingresos_brutos
        factura.razon_social_emisor = monotributista.razonSocial
        factura.telefono_emisor = monotributista.telefono
        factura.cuit_cliente = cliente.cuit
        factura.nombre_cliente = cliente.nombreCompleto
        factura.razon_social_cliente = cliente.razonSocial
        factura.domicilio_cliente = cliente.domicilio
        factura.telefono_cliente = cliente.telefono
        factura.condicion_iva_cliente = cliente.condicionIva
        factura.punto_de_venta = monotributista.punto_venta
        factura.condicion_venta = 'Contado'
        factura.tipo_factura = 'C'

    def crear_pdf(self):
        c = canvas.Canvas("factura_generada.pdf", pagesize=A4)
        width, height = A4

        def agregar_texto(texto, x, y, size=10, bold=False):
            c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
            c.drawString(x * mm, (height - y * mm), texto)

        def dibujar_linea(x1, y1, x2, y2):
            c.line(x1 * mm, (height - y1 * mm), x2 * mm, (height - y2 * mm))

        # ================= ENCABEZADO GENERAL =================
        agregar_texto("ORIGINAL", 100, 10, size=12, bold=True)
        agregar_texto(self.nombre_emisor or "", 10, 20, bold=True)
        agregar_texto(f"Razón Social: {self.razon_social_emisor or ''}", 10, 25)
        agregar_texto(f"Domicilio Comercial: {self.domicilio_emisor or ''}", 10, 30)
        agregar_texto(f"Condición frente al IVA: {self.condicion_iva_emisor or ''}", 10, 35)

        agregar_texto(self.tipo_factura or "C", 100, 20, size=18, bold=True)
        agregar_texto("COD. 011", 110, 25)
        agregar_texto("FACTURA", 120, 20, size=14, bold=True)
        agregar_texto(f"Punto de Venta: {str(self.punto_de_venta).zfill(5)}", 120, 25)
        agregar_texto(f"Comp. Nro: {str(self.numero).zfill(8)}", 120, 30)
        agregar_texto(f"Fecha de Emisión: {self.fecha[:10]}", 120, 35)
        agregar_texto(f"CUIT: {self.cuit_emisor}", 120, 40)
        agregar_texto(f"Ingresos Brutos: {self.ingresos_brutos or ''}", 120, 45)
        agregar_texto(f"Fecha de Inicio de Actividades: {self.fecha_inicio_actividad_emisor or ''}", 120, 50)

        # ================= DATOS DEL PERÍODO =================
        agregar_texto(f"Periodo Facturado Desde: {self.periodo_facturado_desde or ''}  "
                      f"Hasta: {self.periodo_facturado_hasta or ''}  "
                      f"Fecha de Vto. para el pago: {self.fecha_vencimiento_pago or ''}", 10, 60, size=9)

        # ================= DATOS DEL RECEPTOR =================
        agregar_texto(f"Apellido y Nombre / Razón Social: {self.nombre_cliente or ''}", 10, 75)
        agregar_texto(f"Condición frente al IVA: {self.condicion_iva_cliente or ''}", 10, 80)
        agregar_texto(f"Condición de venta: {self.condicion_venta or ''}", 10, 85)
        agregar_texto(f"Domicilio: {self.domicilio_cliente or ''}", 10, 90)

        # ================= TABLA DE PRODUCTOS =================
        table_y = 100
        columnas = ["Producto / Servicio", "Cantidad", "U. Medida", "Precio Unit.", "Subtotal"]
        col_x = [10, 90, 110, 130, 190]
        for i, col in enumerate(columnas):
            agregar_texto(col, col_x[i], table_y, size=8, bold=True)

        row_y = table_y + 5
        for prod in self.productos:
            agregar_texto(prod["nombre"], 10, row_y)
            agregar_texto(f"{prod['cantidad']:.2f}", 90, row_y)
            agregar_texto("unidades", 110, row_y)
            agregar_texto(f"${prod['precio_unitario']:.2f}", 130, row_y)
            agregar_texto(f"${prod['total']:.2f}", 190, row_y)
            row_y += 5

            # Salto de página si es necesario
            if row_y > 260:
                c.showPage()
                row_y = 10

        # ================= TOTALES =================
        agregar_texto(f"Subtotal: $ {self.total:.2f}", 150, row_y + 10)
        agregar_texto("Importe Otros Tributos: $ 0,00", 150, row_y + 15)
        agregar_texto(f"Importe Total: $ {self.total:.2f}", 150, row_y + 20, bold=True)

        return c.save()