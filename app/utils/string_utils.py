import json
import re

from app.controller.factura_controller import FacturaController
from app.controller.monotributista_controller import MonotributistaController
from app.models.monotributista import Monotributista
from app.models.cliente import Cliente

monotributistaController = MonotributistaController()
facturaController = FacturaController()


def getOnlyJsonFrom(text):
    best_block = ''
    max_length = 0

    # Buscamos todas las posibles aperturas de bloques de JSON
    stack = []
    start = None
    for i, char in enumerate(text):
        if char == '{':
            if not stack:
                start = i
            stack.append('{')
        elif char == '}':
            if stack:
                stack.pop()
                if not stack and start is not None:
                    block = text[start:i + 1]
                    try:
                        json_obj = json.loads(block)
                        if len(block) > max_length:
                            best_block = json_obj
                            max_length = len(block)
                    except json.JSONDecodeError:
                        continue

    return best_block  # Esto es un dict (JSON válido)


def hasJsonInside(text):
    # Buscar todos los bloques que parecen JSON entre llaves
    blocks = re.findall(r'\{.*?\}', text, re.DOTALL)

    for block in blocks:
        try:
            # Intentamos cargar el JSON para asegurarnos de que sea válido
            json.loads(block)
            return True
        except json.JSONDecodeError:
            continue

    return False


def convertJSONToCliente(json):
    # Convertir el JSON a un objeto Cliente
    cliente = Cliente(
        nombreCompleto=json.get("name"),
        telefono=json.get("Phone"),
        email=json.get("Email"),
        condicionIva=json.get("condition_iva"),
        cuit=json.get("cuit"),
        domicilio=json.get("Address")
    )
    return cliente


def convertJSONToMonotributista(json):
    # Convertir el JSON a un objeto Monotributista
    monotributista = Monotributista(
        nombreCompleto=json.get("full_name"),
        telefono=json.get("phone"),
        email=json.get("email"),
        condicionIva=json.get("condition_iva"),
        cuit=json.get("cuit"),
        domicilio=json.get("tax_address"),
        razonSocial=json.get("company_name"),
        categoria_monotributo=json.get("monotributo_category"),
        actividad=json.get("activity"),
        punto_venta=json.get("point_of_sale")
    )

    return monotributista


def check_string_for_specific_words(message, wa_id):
    """
    Recorre un texto y determina a qué categoría pertenece según las listas de palabras clave.
    """
    monotributista = monotributistaController.obtener_por_telefono(wa_id)
    if monotributista is not None:
        return 'General'

    words_list = cargar_listas_palabras()
    message = message.lower()

    for category, palabras_clave in words_list.items():
        for palabra in palabras_clave:
            if palabra.lower() in message:
                return category  # Podés cambiar esto por otra lógica

    return 'Original'


def cargar_listas_palabras(ruta="./app/config/palabras_clave.json"):
    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)
