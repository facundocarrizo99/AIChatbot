from app.models.usuario import Usuario

class Monotributista(Usuario):
    def __init__(self, nombreCompleto, telefono, email, condicionIva, cuit, domicilio,
                 razonSocial, categoria_monotributo, actividad, punto_venta, ingresos_brutos=None, fecha_inicio_actividad=None):
        super().__init__(nombreCompleto, telefono, email, condicionIva, cuit, domicilio)
        self.razonSocial = razonSocial
        self.ingresos_brutos = ingresos_brutos
        self.fecha_inicio_actividad = fecha_inicio_actividad
        self.categoria_monotributo = categoria_monotributo
        self.actividad = actividad
        self.punto_venta = punto_venta
        self.clientes = []  # Lista de clientes

    def buscar_cliente_por_cuit(self, cuit):
        for cliente in self.clientes:
            if cliente.cuit == cuit:
                return cliente
        return None