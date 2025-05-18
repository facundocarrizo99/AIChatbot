from app.services.cliente_service import ClienteService

class ClienteController:
    def __init__(self):
        self.service = ClienteService()

    def crear_cliente(self, datos):
        return self.service.agregar_cliente(datos)

    def eliminar_cliente(self, telefono):
        return self.service.eliminar_cliente(telefono)

    def modificar_cliente(self, telefono, nuevos_datos):
        return self.service.modificar_cliente(telefono, nuevos_datos)

    def obtener_por_telefono(self, telefono):
        return self.service.buscar_por_telefono(telefono)