import logging
from abc import ABC, abstractmethod


class Usuario(ABC):
    def __init__(self, nombreCompleto, telefono, email, condicionIva, cuit, domicilio, _id=None):
        self.objectId = _id
        self.nombreCompleto = nombreCompleto
        self.telefono = telefono
        self.email = email
        self.condicionIva = condicionIva
        self.cuit = cuit
        self.domicilio = domicilio
        self.razonSocial = None

    @abstractmethod
    def to_dict(self):
        pass