import logging

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
        try:
            # Get the last invoice if it exists
            ultima_factura = list(self.facturas_collection.find().sort("numero", -1).limit(1))

            # Set the new invoice number
            if ultima_factura and "numero" in ultima_factura[0]:
                factura.numero = int(ultima_factura[0]["numero"]) + 1
            else:
                factura.numero = 1  # Start from 1 if no invoices exist

            # Set punto_venta if not already set
            if not hasattr(factura, 'punto_venta') or not factura.punto_venta:
                factura.punto_venta = 1  # Default value, adjust as needed

            # Insert the new invoice
            result = self.facturas_collection.insert_one(factura.to_dict())
            return str(result.inserted_id)

        except Exception as e:
            logging.error(f"Error creating invoice: {e}")
            raise

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