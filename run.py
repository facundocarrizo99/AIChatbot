import logging
from app.controller.controller import UsuarioController

#para testear conexion con mongo
from app.database import get_test_collection

from app import create_app

app = create_app()

if __name__ == "__main__":
    logging.info("Flask app started")
    controller = UsuarioController()
    app.run(host="0.0.0.0", port=8000)
