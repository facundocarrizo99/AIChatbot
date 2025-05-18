from app.models.usuario import Usuario

class Cliente(Usuario):
    def __init__(self, nombreCompleto, telefono, email, condicionIva, cuit, domicilio):
        super().__init__(nombreCompleto, telefono, email, condicionIva, cuit, domicilio)

