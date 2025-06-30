from bson import ObjectId
from datetime import datetime
from app.models.cliente import Cliente
from app.models.monotributista import Monotributista
from app.services.monotributista_service import MonotributistaService

class MonotributistaController:
    def __init__(self):
        self.service = MonotributistaService(False)

    def crear_monotributista(self,tele_original, nombreCompleto, telefono, email, condicionIva, cuit, domicilio,
                 razonSocial, categoria_monotributo, actividad, punto_venta, ingresos_brutos, fecha_inicio_actividad):
        monotributista = Monotributista(nombreCompleto, telefono, email, condicionIva, cuit, domicilio,
                 razonSocial, categoria_monotributo, actividad, punto_venta, ingresos_brutos, fecha_inicio_actividad)
        return self.service.agregar_monotributista(monotributista)

    def eliminar_monotributista(self, telefono):
        return self.service.eliminar_monotributista(telefono)

    def modificar_monotributista(self, telefono, nuevos_datos):
        return self.service.modificar_monotributista(telefono, nuevos_datos)

    def obtener_por_telefono(self, telefono):
        return self.service.buscar_por_telefono(telefono)

    def agregar_cliente(self, telefono_monotributista, nombre_completo, telefono, email, condicion_iva, cuit, domicilio):
        cliente = Cliente(nombre_completo, telefono, email, condicion_iva, cuit, domicilio)
        return self.service.agregar_cliente_a_monotributista(telefono_monotributista, cliente)

    def modificar_cliente(self, telefono, cliente_identificador, nuevos_datos):
        return self.service.modificar_cliente_de_monotributista(telefono, cliente_identificador, nuevos_datos)

    def obtener_por_cuit(self,cuit):
        return self.service.buscar_por_cuit(cuit)

    def verificar_cliente(self, telefono, nombre):
        monotributista = Monotributista.from_dict(self.obtener_por_telefono(telefono))
        cliente = monotributista.buscar_clientes_por_valor(nombre)
        if not cliente:
            return None
        return cliente

    def to_raw_dict(self, string):
        return eval(string, {"ObjectId": ObjectId, "datetime": datetime})