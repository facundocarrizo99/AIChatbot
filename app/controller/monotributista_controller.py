from app.services.monotributista_service import MonotributistaService

class MonotributistaController:
    def __init__(self):
        self.service = MonotributistaService(False)

    def crear_monotributista(self, datos):
        return self.service.agregar_monotributista(datos)

    def eliminar_monotributista(self, telefono):
        return self.service.eliminar_monotributista(telefono)

    def modificar_monotributista(self, telefono, nuevos_datos):
        return self.service.modificar_monotributista(telefono, nuevos_datos)

    def obtener_por_telefono(self, telefono):
        return self.service.buscar_por_telefono(telefono)

    def agregar_cliente(self, telefono_monotributista, cliente_data):
        return self.service.agregar_cliente_a_monotributista(telefono_monotributista, cliente_data)

    def modificar_cliente(self, telefono, cliente_identificador, nuevos_datos):
        return self.service.modificar_cliente_de_monotributista(telefono, cliente_identificador, nuevos_datos)

    def obtener_por_cuit(self,cuit):
        return self.service.buscar_por_cuit(cuit)