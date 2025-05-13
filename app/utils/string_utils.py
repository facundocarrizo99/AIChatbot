import json
import re
from app.controller.controller import UsuarioController
from app.db.models import Monotributista, Cliente

usuarioControlerSingleton = UsuarioController()

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

def stringToAction(json, ownerPhone):
    # find on json attribute type the object to be processed
    type = json.get("type")
    print('El tipo de objeto recibido es: ',type)
    #TODO agregar handelleo de errores para cuando la response no es correcta en la bd
    if type == "client":
        # process client
        UsuarioController.agregar_cliente_a_monotributista(usuarioControlerSingleton, ownerPhone, convertJSONToCliente(json))
        newResponse = 'Hemos agregado tu cliente a la lista de clientes de tu monotributista, ahora puedes agregar más clientes! O solicitar una nueva factura!'
        pass
    elif type == "monotributista":
        # process invoice
        UsuarioController.agregar_usuario(usuarioControlerSingleton, convertJSONToMonotributista(json))
        newResponse = 'Te hemos agregado como monotributista, ahora puedes agregar clientes a tu lista!'
        pass
    elif type == "factura":
        # process payment
        newResponse = 'Todavia no podemos emitir facturas, pero pronto lo haremos!'
        pass
    else:
        # process other
        newResponse = 'Hubo un error, no hemos podido procesar tu mensaje, por favor intenta nuevamente!'
        pass

    return newResponse

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
