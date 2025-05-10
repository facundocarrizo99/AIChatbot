from flask import Flask, jsonify
from app.controller.controller import UsuarioController
from app.db.models import Monotributista, ConsumidorFinal

app = Flask(__name__)
controller = UsuarioController()

if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=8000)