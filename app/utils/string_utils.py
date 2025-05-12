import json
import re

def getOnlyJsonFrom(text):
    # Buscar todos los bloques que parecen JSON entre llaves
    blocks = re.findall(r'\{.*?\}', text, re.DOTALL)

    jsonOnly = ''
    graterSize = 0

    for block in blocks:
        try:
            # Intentamos cargar el JSON para asegurarnos de que sea válido
            json.loads(block)
            if len(block) > graterSize:
                graterSize = len(block)
                jsonOnly = block
        except json.JSONDecodeError:
            continue

    return jsonOnly

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

def stringToAction(json):
    # find on json attribute type the object to be processed
    type = json["type"]
    if type == "Cliente":
        # process client
        newResponse = 'algo'
        pass
    elif type == "Monotributista":
        # process invoice
        newResponse = 'algo'
        pass
    elif type == "Factura":
        # process payment
        newResponse = 'algo'
        pass
    else:
        # process other
        newResponse = 'algo'
        pass

    return newResponse