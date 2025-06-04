from app.models.usuario import Usuario
from app.models.cliente import Cliente

class Monotributista(Usuario):
    def __init__(self, nombreCompleto, telefono, email, condicionIva, cuit, domicilio,
                 razonSocial, categoria_monotributo, actividad, punto_venta, ingresos_brutos, fecha_inicio_actividad, _id=None, clientes=None):
        super().__init__(nombreCompleto, telefono, email, condicionIva, cuit, domicilio, _id)
        self.razonSocial = razonSocial
        self.ingresos_brutos = ingresos_brutos
        self.fecha_inicio_actividad = fecha_inicio_actividad
        self.categoria_monotributo = categoria_monotributo
        self.actividad = actividad
        self.punto_venta = punto_venta
        self.clientes = [] if clientes is None else clientes  # Lista de clientes

    def buscar_clientes_por_valor(self, valor_buscado):
        encontrados = []
        for cliente in self.clientes:
            if any(str(valor).lower() == str(valor_buscado).lower() for valor in cliente.values()):
                encontrados.append(cliente)
        return encontrados[0]

    def to_dict(self):
        return {
            "nombreCompleto": self.nombreCompleto,
            "telefono": self.telefono,
            "email": self.email,
            "condicionIva": self.condicionIva,
            "cuit": self.cuit,
            "domicilio": self.domicilio,
            "razonSocial": self.razonSocial,
            "categoria_monotributo": self.categoria_monotributo,
            "actividad": self.actividad,
            "punto_venta": self.punto_venta,
            "ingresos_brutos": self.ingresos_brutos,
            "fecha_inicio_actividad": self.fecha_inicio_actividad
        }


    def to_dict_for_factura(self):
        return {
            "nombreCompleto": self.nombreCompleto,
            "telefono": self.telefono,
            "email": self.email,
            "condicionIva": self.condicionIva,
            "cuit": self.cuit,
            "domicilio": self.domicilio,
            "razonSocial": self.razonSocial,
            "categoria_monotributo": self.categoria_monotributo,
            "actividad": self.actividad,
            "punto_venta": self.punto_venta,
            "ingresos_brutos": self.ingresos_brutos,
            "fecha_inicio_actividad": self.fecha_inicio_actividad
        }

    @staticmethod
    def from_dict(data):
        clientes_data = data.get("clientes", [])

        # Si querés convertir cada cliente a objeto Cliente:
        clientes = [Cliente.from_dict(c) if isinstance(c, dict) else c for c in clientes_data]

        return Monotributista(
            nombreCompleto=data.get("nombreCompleto"),
            telefono=data.get("telefono"),
            email=data.get("email"),
            condicionIva=data.get("condicionIva"),
            cuit=data.get("cuit"),
            domicilio=data.get("domicilio"),
            razonSocial=data.get("razonSocial"),
            categoria_monotributo=data.get("categoria_monotributo"),
            actividad=data.get("actividad"),
            punto_venta=data.get("punto_venta"),
            ingresos_brutos=data.get("ingresos_brutos"),
            fecha_inicio_actividad=data.get("fecha_inicio_actividad"),
            clientes=clientes
        )