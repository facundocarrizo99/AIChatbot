from flask import Flask, jsonify
from app.controller.controller import UsuarioController

app = Flask(__name__)
controller = UsuarioController()

if __name__ == "__main__":
    """
    cliente_data = {
    "nombreCompleto": "Cliente Ejemplo",
    "telefono": "1100000001",
    "email": "cliente@correo.com",
    "condicionIva": "ConsumidorFinal",
    "cuit": "20304050608",
    "domicilio": "Calle Falsa 123"
    }
    controller.agregar_cliente_a_monotributista("1100000000",cliente_data)
    """
    app.run(host="0.0.0.0", port=8000)