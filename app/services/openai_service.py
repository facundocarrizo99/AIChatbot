import logging
import os
import shelve
import time
import json
from unicodedata import category

from dotenv import load_dotenv
from openai import OpenAI

from app.controller.factura_controller import FacturaController
from app.controller.monotributista_controller import MonotributistaController
from app.utils.string_utils import check_string_for_specific_words

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID_ORIGINAL = os.getenv("OPENAI_ASSISTANT_ID_ORIGINAL")
OPENAI_ASSISTANT_ID_FACTURAS = os.getenv("OPENAI_ASSISTANT_ID_FACTURAS")
OPENAI_ASSISTANT_ID_REGISTRAR = os.getenv("OPENAI_ASSISTANT_ID_REGISTRAR")
OPENAI_ASSISTANT_ID_GENERAL = os.getenv("OPENAI_ASSISTANT_ID_GENERAL")
client = OpenAI(api_key=OPENAI_API_KEY)

def create_assistant(file):
    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name="WhatsApp AirBnb Assistant",
        instructions="You're a helpful WhatsApp assistant that can assist guests that are staying in our Paris AirBnb. Use your knowledge base to best respond to customer queries. If you don't know the answer, say simply that you cannot help with question and advice to contact the host directly. Be friendly and funny.",
        tools=[{"type": "retrieval"}],
        model="gpt-4-1106-preview",
        file_ids=[file.id],
    )
    return assistant


# Use context manager to ensure the shelf file is closed properly
def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)


def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id

def run_assistant(thread_id, name, assistant_category, telefono):
    assistant_id = get_assistant_id_from_category(assistant_category)
    assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID_FACTURAS)

    # Recuperar el thread actualizado
    thread = client.beta.threads.retrieve(thread_id)

    print(assistant.id + " " + str(assistant.tools))

    # Crear el run
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=f"You are having a conversation with {name}",
    )

    while True:
        time.sleep(1.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id )
        # tool_calls = run.required_action
        # print(str(tool_calls))
        if run.status == "completed":
            break

        elif run.status == "requires_action":
            #print("Requires action" + str(run.required_action))
            tool_calls = run.required_action.submit_tool_outputs.tool_calls

            tool_outputs = []

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                print("Function name: " + function_name)
                print("Arguments: " + str(arguments))

                result = ejecutar_funcion_por_nombre(function_name, arguments, telefono)

                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": result
                })

            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

    # Obtener el último mensaje del assistant
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    logging.info(f"Generated message: {new_message}")
    return new_message

def generate_ai_response(message_body, wa_id, name):
    # Check if there is already a thread_id for the wa_id
    #thread_id = check_if_thread_exists(wa_id)
    # If a thread doesn't exist, create one and store it
    # if thread_id is None:
    #     logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
    #     thread = client.beta.threads.create()
    #     #store_thread(wa_id, thread.id)
    #     thread_id = thread.id
    # # Otherwise, retrieve the existing thread
    # else:
    #     logging.info(f"Retrieving existing thread for {name} with wa_id {wa_id}")
    #     thread = client.beta.threads.retrieve(thread_id)

    logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
    thread = client.beta.threads.create()
    thread_id = thread.id

    # Add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )

    # Run the assistant and get the new message
    #categoria = check_string_for_specific_words(message_body, wa_id)
    new_message = run_assistant(thread.id, name, "Facturar", wa_id)
    categoria = check_string_for_specific_words(message_body, wa_id)
    new_message = run_assistant(thread.id, name, categoria)

    return new_message

def get_assistant_id_from_category(assistant_category):
    if assistant_category == "Registrar":
        return OPENAI_ASSISTANT_ID_REGISTRAR
    elif assistant_category == "Facturar":
        return OPENAI_ASSISTANT_ID_FACTURAS
    elif assistant_category == "General":
        return OPENAI_ASSISTANT_ID_GENERAL
    else:
        return OPENAI_ASSISTANT_ID_ORIGINAL

def ejecutar_funcion_por_nombre(nombre_funcion, args, telefono):
    funciones = {
        "crear_factura": FacturaController().crear_factura,
        "obtener_factura": FacturaController().obtener_factura,
        "verificar_cliente": MonotributistaController().verificar_cliente,
        "crear_cliente": MonotributistaController().agregar_cliente,
        "modificar_cliente": MonotributistaController().modificar_cliente,
        "obtener_por_cuit": MonotributistaController().obtener_por_cuit
    }

    funcion = funciones.get(nombre_funcion)
    if funcion:
        object = funcion(telefono, *args.values())
    else:
        object = f"Función {nombre_funcion} no encontrada"

    if object is Exception:
        response = {
            "error": True,
            "message": object.args[0]
        }
    else:
        response = {
            "error": False,
            "object": object
        }

    return str(response) if isinstance(response, dict) else response

def get_assistant_id_from_category(assistant_category):
    if assistant_category == "Registrar":
        return OPENAI_ASSISTANT_ID_REGISTRAR
    elif assistant_category == "Facturar":
        return OPENAI_ASSISTANT_ID_FACTURAS
    elif assistant_category == "General":
        return OPENAI_ASSISTANT_ID_GENERAL
    else:
        return OPENAI_ASSISTANT_ID_ORIGINAL