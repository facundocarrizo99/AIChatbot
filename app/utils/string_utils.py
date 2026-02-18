import json
import re

from app.models.monotributista import Monotributista
from app.models.cliente import Cliente

_monotributista_controller = None


def _get_monotributista_controller():
    global _monotributista_controller
    if _monotributista_controller is None:
        from app.controller.monotributista_controller import MonotributistaController
        _monotributista_controller = MonotributistaController()
    return _monotributista_controller


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


def convertJSONToCliente(data):
    # Convertir el JSON a un objeto Cliente
    cliente = Cliente(
        nombreCompleto=data.get("name"),
        telefono=data.get("Phone"),
        email=data.get("Email"),
        condicionIva=data.get("condition_iva"),
        cuit=data.get("cuit"),
        domicilio=data.get("Address")
    )
    return cliente


def convertJSONToMonotributista(data):
    # Convertir el JSON a un objeto Monotributista
    monotributista = Monotributista(
        nombreCompleto=data.get("full_name"),
        telefono=data.get("phone"),
        email=data.get("email"),
        condicionIva=data.get("condition_iva"),
        cuit=data.get("cuit"),
        domicilio=data.get("tax_address"),
        razonSocial=data.get("company_name"),
        categoria_monotributo=data.get("monotributo_category"),
        actividad=data.get("activity"),
        punto_venta=data.get("point_of_sale")
    )

    return monotributista


def check_string_for_specific_words(message, wa_id):
    """
    Recorre un texto y determina a qué categoría pertenece según las listas de palabras clave.
    """
    monotributista = _get_monotributista_controller().obtener_por_telefono(wa_id)
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
