from enum import Enum

class TipoUsuario(Enum):
    MONOTRIBUTISTA = "Monotributista"
    CONSUMIDOR_FINAL = "ConsumidorFinal"

class Usuario:
    def __init__(self, userId, password, nombreCompleto, tipo, telefono, email, condicionIva):
        self.userId = userId
        self.password = password
        self.nombreCompleto = nombreCompleto
        self.tipo = tipo.value
        self.telefono = telefono
        self.email = email
        self.condicionIva = condicionIva

class Monotributista(Usuario):
    def __init__(self, userId, password, nombreCompleto, telefono, email, condicionIva,
                 cuit, razonSocial, categoria_monotributo, actividad, domicilioFiscal, punto_venta):
        super().__init__(userId, password, nombreCompleto, TipoUsuario.MONOTRIBUTISTA, telefono, email, condicionIva)
        self.dni = None
        self.cuit = cuit
        self.razonSocial = razonSocial
        self.categoria_monotributo = categoria_monotributo
        self.actividad = actividad
        self.domicilio = None
        self.domicilioFiscal = domicilioFiscal
        self.punto_venta = punto_venta
        self.clientes = []  # Lista de clientes

class ConsumidorFinal(Usuario):
    def __init__(self, userId, password, nombreCompleto, telefono, email, condicionIva,
                 dni, domicilio):
        super().__init__(userId, password, nombreCompleto, TipoUsuario.CONSUMIDOR_FINAL, telefono, email, condicionIva)
        self.dni = dni
        self.cuit = None
        self.razonSocial = None
        self.categoria_monotributo = None
        self.actividad = None
        self.domicilio = domicilio
        self.domicilioFiscal = None
        self.punto_venta = None
