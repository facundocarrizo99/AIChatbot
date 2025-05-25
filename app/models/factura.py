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
    def __init__(self, numero, fecha, cuit_emisor, cuit_cliente, productos):
        self.numero = numero
        self.fecha = fecha or datetime.utcnow().isoformat()
        self.cuit_emisor = cuit_emisor
        self.cuit_cliente = cuit_cliente
        self.productos = [p.to_dict() if isinstance(p, Producto) else p for p in productos]
        self.total = sum([p["total"] for p in self.productos])
        self.cae = None
        self.fecha_vencimiento_cae = None


    def to_dict(self):
        return {
            "numero": self.numero,
            "fecha": self.fecha,
            "cuit_emisor": self.cuit_emisor,
            "cuit_cliente": self.cuit_cliente,
            "productos": self.productos,
            "total": self.total
        }