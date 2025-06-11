import random
from datetime import datetime, timedelta, timezone

class ARCAService:
    def __init__(self):
        pass

    def get_cae(self, una_factura):
        # Implementa la lógica para obtener el CAE de la factura de ARCA
        una_factura_con_CAE = self.agregar_cae(una_factura)
        return una_factura_con_CAE

    def agregar_cae(self, una_factura):
        # Es la solucion actual para agregar el CAE
        una_factura.cae = str(random.randint(10**13, 10**14 - 1))
        una_factura.fecha_vencimiento_cae = self.generar_fecha_vencimiento_iso8601()
        return una_factura

    def generar_fecha_vencimiento_iso8601(self):
        fecha_vencimiento = datetime.now(timezone.utc) + timedelta(days=10)
        return fecha_vencimiento.strftime("%Y-%m-%dT%H:%M:%SZ")