import logging
from pymongo import MongoClient
from app.models.cliente import Cliente
from app.config.database import db,db_test

class ClienteService:
    def __init__(self):
        #self.collection = db["Usuario"]
        self.collection = db_test["Usuario"]
        
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