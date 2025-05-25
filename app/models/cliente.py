from app.models.usuario import Usuario

class Cliente(Usuario):
    def __init__(self, nombreCompleto, telefono, email, condicionIva, cuit, domicilio, _id=None):
        super().__init__(nombreCompleto, telefono, email, condicionIva, cuit, domicilio)

    def to_dict(self): return {
        "nombreCompleto": self.nombreCompleto,
        "telefono": self.telefono,
        "email": self.email,
        "condicionIva": self.condicionIva,
        "cuit": self.cuit,
        "domicilio": self.domicilio,
    }
