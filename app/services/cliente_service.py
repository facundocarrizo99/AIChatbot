import logging
from pymongo import MongoClient
from app.models.cliente import Cliente
from app.config.database import db,db_test

class ClienteService:
    def __init__(self, is_test=False):
        if is_test:
            self.collection = db_test["Usuario"]
        else:
            self.collection = db["Usuario"]
        
    def agregar_cliente(self, datos):
        cliente = Cliente(**datos)
        return str(self.collection.insert_one(cliente.__dict__).inserted_id)

    def eliminar_cliente(self, telefono):
        return self.collection.delete_one({"telefono": telefono, "categoria_monotributo": {"$exists": False}}).deleted_count > 0

    def modificar_cliente(self, telefono, nuevos_datos):
        result = self.collection.update_one(
            {"telefono": telefono, "categoria_monotributo": {"$exists": False}},
            {"$set": nuevos_datos}
        )
        return result.modified_count > 0

    def buscar_por_telefono(self, telefono):
        return self.collection.find_one({"telefono": telefono, "categoria_monotributo": {"$exists": False}})

    def buscar_por_cuit(self,cuit):
        return self.collection.find_one({
            "clientes": {
                "$elemMatch": {"cuit":cuit}
            }
        })