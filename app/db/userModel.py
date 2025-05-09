from enum import Enum


class TipoUsuario(Enum):
    MONOTRIBUTISTA = "Monotributista"
    CONSUMIDOR_FINAL = "ConsumidorFinal"


class Usuario:
    def init(self, userId, password, nombreCompleto, tipo, telefono, email, condicionIva):
        self.userId = userId
        self.password = password
        self.nombreCompleto = nombreCompleto
        self.tipo = tipo  # Será un string ("Monotributista" o "ConsumidorFinal")
        self.telefono = telefono
        self.email = email
        self.condicionIva = condicionIva


class Monotributista(Usuario):
    def init(self, userId, password, nombreCompleto, telefono, email, condicionIva,
                 cuit, razonSocial, categoria_monotributo, actividad, domicilioFiscal, punto_venta):
        super().init(userId, password, nombreCompleto, TipoUsuario.MONOTRIBUTISTA.value, telefono, email, condicionIva)
        self.dni = "null"  # No aplica
        self.cuit = cuit
        self.razonSocial = razonSocial
        self.categoria_monotributo = categoria_monotributo
        self.actividad = actividad
        self.domicilio = "null"  # No aplica
        self.domicilioFiscal = domicilioFiscal
        self.punto_venta = punto_venta


class ConsumidorFinal(Usuario):
    def init(self, userId, password, nombreCompleto, telefono, email, condicionIva,
                 dni, domicilio):
        super().init(userId, password, nombreCompleto, TipoUsuario.CONSUMIDOR_FINAL.value, telefono, email, condicionIva)
        self.dni = dni
        self.cuit = "null"  # No aplica
        self.razonSocial = "null"  # No aplica
        self.categoria_monotributo = "null"  # No aplica
        self.actividad = "null"  # No aplica
        self.domicilio = domicilio
        self.domicilioFiscal = "null"  # No aplica
        self.punto_venta = "null"  # No aplica