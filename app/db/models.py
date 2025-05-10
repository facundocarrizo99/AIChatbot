class Usuario:
    def __init__(self, nombreCompleto, telefono, email, condicionIva, cuit, domicilio):
        self.nombreCompleto = nombreCompleto
        self.telefono = telefono
        self.email = email
        self.condicionIva = condicionIva
        self.cuit = cuit
        self.domicilio = domicilio

class Monotributista(Usuario):
    def __init__(self, nombreCompleto, telefono, email, condicionIva, cuit, domicilio,
                 razonSocial, categoria_monotributo, actividad, punto_venta):
        super().__init__(nombreCompleto, telefono, email, condicionIva, cuit, domicilio)
        self.razonSocial = razonSocial
        self.categoria_monotributo = categoria_monotributo
        self.actividad = actividad
        self.punto_venta = punto_venta
        self.clientes = []  # Lista de clientes

class Cliente(Usuario):
    def __init__(self, nombreCompleto, telefono, email, condicionIva, cuit, domicilio):
        super().__init__(nombreCompleto, telefono, email, condicionIva, cuit, domicilio)
