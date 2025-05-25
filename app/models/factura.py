from datetime import datetime
from formatter import NullWriter


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