import logging
from pymongo import MongoClient
from app.models.monotributista import Monotributista
from app.models.cliente import Cliente
from app.config.database import db, db_test

class MonotributistaService:
    def __init__(self):
        self.collection = db["Usuario"]

    def agregar_monotributista(self, datos):
        monotributista = Monotributista(**datos)
        return str(self.collection.insert_one(monotributista.__dict__).inserted_id)

    def eliminar_monotributista(self, telefono):
        return self.collection.delete_one({"telefono": telefono}).deleted_count > 0

    def modificar_monotributista(self, telefono, nuevos_datos):
        result = self.collection.update_one({"telefono": telefono}, {"$set": nuevos_datos})
        return result.modified_count > 0

    def buscar_por_telefono(self, telefono):
        return self.collection.find_one({"telefono": telefono, "categoria_monotributo": {"$exists": True}})

    def agregar_cliente_a_monotributista(self, telefono, cliente_data):
        monotributista = self.buscar_por_telefono(telefono)
        if not monotributista:
            return False

        cliente = Cliente(**cliente_data)
        self.collection.update_one(
            {"telefono": telefono},
            {"$addToSet": {"clientes": cliente.__dict__}}
        )
        return True

    def modificar_cliente_de_monotributista(self, telefono, cliente_identificador, nuevos_datos):
        monotributista = self.buscar_por_telefono(telefono)
        if not monotributista:
            return False

        clientes = monotributista.get("clientes", [])
        modificado = False

        for cliente in clientes:
            if any(cliente.get(k) == v for k, v in cliente_identificador.items()):
                cliente.update(nuevos_datos)
                modificado = True
                break

        if not modificado:
            return False

        self.collection.update_one({"telefono": telefono}, {"$set": {"clientes": clientes}})
        return True