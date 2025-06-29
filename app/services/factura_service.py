from app.config.database import db, db_test
from app.models.factura import Factura
from typing import Optional

class FacturaService:
    def __init__(self, is_test=False):
        if is_test:
            self.facturas_collection = db_test["Factura"]
        else:
            self.facturas_collection = db["Factura"]

    def crear_factura(self, factura):
        # TODO: ROMPE el TEST
        factura_existente = self.facturas_collection.find_one({"numero": factura.numero})

        if factura_existente:
            ultima_factura = self.facturas_collection.find().sort("numero", -1).limit(1)
            ultimo_numero = int(ultima_factura[0]["numero"]) if ultima_factura else 0
            factura.numero = (ultimo_numero + 1)

        result = self.facturas_collection.insert_one(factura.to_dict())
        return str(result.inserted_id)

    def obtener_factura_por_numero(self, numero) -> Optional[Factura]:
        data = self.facturas_collection.find_one({"numero": numero})
        if data:
            data.pop("_id", None)  # Opcional: elimina el _id si no lo vas a usar
            return Factura.from_dict(data)
        return None

    def eliminar_factura(self, numero):
        result = self.facturas_collection.delete_one({"numero": numero})
        return result.deleted_count > 0

    def modificar_factura(self, numero, nuevos_datos):
        result = self.facturas_collection.update_one(
            {"numero": numero},
            {"$set": nuevos_datos}
        )
        return result.modified_count > 0

    def obtener_todas(self):
        return list(self.facturas_collection.find())