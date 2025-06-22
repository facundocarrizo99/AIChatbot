import logging
import os
import shelve
import time
import json
from typing import Optional, Dict
from enum import Enum

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

class BotType(Enum):
    GENERAL = "General"
    FACTURAR = "Facturar"
    REGISTRAR = "Registrar"

class OpenAIService:
    def __init__(self):
        self.assistant_ids = {
            BotType.GENERAL: OPENAI_ASSISTANT_ID_GENERAL,
            BotType.FACTURAR: OPENAI_ASSISTANT_ID_FACTURAS,
            BotType.REGISTRAR: OPENAI_ASSISTANT_ID_REGISTRAR,
        }
        
        self.controllers = {
            'factura': FacturaController(),
            'monotributista': MonotributistaController()
        }

    def create_thread(self, name: str, wa_id: str) -> str:
        """Create a new thread and return its ID"""
        logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create()
        return thread.id

    def add_message_to_thread(self, thread_id: str, message: str) -> None:
        """Add a message to an existing thread"""
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )

    def run_assistant(self, thread_id: str, name: str, bot_type: BotType, wa_id: str) -> str:
        """Run the assistant and handle any required actions"""
        assistant_id = self.assistant_ids[bot_type]
        assistant = client.beta.assistants.retrieve(assistant_id)
        
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant.id,
            instructions=f"You are having a conversation with {name}"
        )

        while True:
            time.sleep(1.5)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            
            if run.status == "completed":
                break
            elif run.status == "requires_action":
                self._handle_required_actions(thread_id, run, wa_id)

        messages = client.beta.threads.messages.list(thread_id=thread_id)
        return messages.data[0].content[0].text.value

    def _handle_required_actions(self, thread_id: str, run, wa_id: str) -> None:
        """Handle any required actions from the assistant"""
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            result = self._execute_function(function_name, arguments, wa_id)
            
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": result
            })

        client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )

    def _execute_function(self, function_name: str, arguments: Dict, wa_id: str) -> str:
        """Execute a function based on its name and return the result"""
        # Special handling for bot calls
        print(f"Executing {function_name}")
        #TODO: no se mapea bien el bot con su type correspondiente
        if function_name.startswith("call_") and function_name.endswith("_bot"):
            bot_type = self._get_bot_type_from_function(function_name)
            print("BOT TYPE VALUE:", bot_type)
            print("BOT TYPE TYPE:", type(bot_type))
            # More explicit check for bot_type
            if bot_type is not None and isinstance(bot_type, BotType):
                print("BOT TYPE MATCHED:", bot_type.value)
                return self.handle_specific_bot(arguments.get("message", ""), wa_id, arguments.get("name", ""), bot_type)
            else:
                print("BOT TYPE NOT MATCHED - Debug info:")
                print("Function name:", function_name)
                print("Available mappings:", self._get_bot_type_from_function.__defaults__)
        
        # Handle controller functions
        controller_functions = {
            'crear_factura': self.controllers['factura'].crear_factura,
            'obtener_factura': self.controllers['factura'].obtener_factura,
            'verificar_cliente': self.controllers['monotributista'].verificar_cliente,
            'crear_cliente': self.controllers['monotributista'].agregar_cliente,
            'modificar_cliente': self.controllers['monotributista'].modificar_cliente,
            'obtener_por_cuit': self.controllers['monotributista'].obtener_por_cuit
        }

        func = controller_functions.get(function_name)
        print("SE INTENTA EJECUTAR LA FUNCION: ", func)
        if not func:
            return f"Function {function_name} not found"

        try:
            result = func(wa_id, *arguments.values())
            return str(result)
        except Exception as e:
            logging.error(f"Error executing {function_name}: {str(e)}")
            return str({"error": True, "message": str(e)})

    def _get_bot_type_from_function(self, function_name: str) -> Optional[BotType]:
        """Convert function name to bot type"""
        mapping = {
            "call_facturar_bot": BotType.FACTURAR,
            "call_monotributista_bot": BotType.REGISTRAR,
            "call_general_bot": BotType.GENERAL
        }
        print("Attempting to map function:", function_name)
        print("Available mappings:", mapping)
        result = mapping.get(function_name)
        print("Mapping result:", result)
        return result

    def handle_specific_bot(self, message: str, wa_id: str, name: str, bot_type: BotType) -> str:
        """Handle requests for specific bots"""
        thread_id = self.create_thread(name, wa_id)
        print("CREATED NEW THREAD FOR BOT: ", str(BotType))
        self.add_message_to_thread(thread_id, message)
        return self.run_assistant(thread_id, name, bot_type, wa_id)

    def process_message(self, message: str, wa_id: str, name: str) -> str:
        """Main entry point for processing messages"""
        # Always start with general bot
        thread_id = self.create_thread(name, wa_id)
        self.add_message_to_thread(thread_id, message)
        return self.run_assistant(thread_id, name, BotType.GENERAL, wa_id)

# Create a singleton instance
openai_service = OpenAIService()

# Public interface functions
def generate_ai_response(message_body: str, wa_id: str, name: str) -> str:
    """Main entry point for generating AI responses"""
    return openai_service.process_message(message_body, wa_id, name)

# Use context manager to ensure the shelf file is closed properly
def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)

def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id

# def run_assistant_without_response(thread_id, name, assistant_category, telefono):
#     assistant_id = get_assistant_id_from_category(assistant_category)
#     assistant = client.beta.assistants.retrieve(assistant_id)
#
#     # Recuperar el thread actualizado
#     thread = client.beta.threads.retrieve(thread_id)
#     print(assistant.id + " " + str(assistant.tools))
#     # Crear el run
#     run = client.beta.threads.runs.create(
#         thread_id=thread.id,
#         assistant_id=assistant.id,
#         instructions=f"You are having a conversation with {name}",
#     )
#
#     while True:
#         time.sleep(1.5)
#         run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id )
#         # tool_calls = run.required_action
#         # print(str(tool_calls))
#         if run.status == "completed":
#             break
#
#         elif run.status == "requires_action":
#             #print("Requires action" + str(run.required_action))
#             tool_calls = run.required_action.submit_tool_outputs.tool_calls
#
#             tool_outputs = []
#
#             for tool_call in tool_calls:
#                 function_name = tool_call.function.name
#                 arguments = json.loads(tool_call.function.arguments)
#
#                 print("Function name: " + function_name)
#                 print("Arguments: " + str(arguments))
#
#                 result = ejecutar_bot_correcto(function_name, arguments, telefono)
#
#                 tool_outputs.append({
#                     "tool_call_id": tool_call.id,
#                     "output": result
#                 })
#
#             client.beta.threads.runs.submit_tool_outputs(
#                 thread_id=thread.id,
#                 run_id=run.id,
#                 tool_outputs=tool_outputs
#             )
#
# def run_assistant(thread_id, name, assistant_category, telefono):
#     assistant_id = get_assistant_id_from_category(assistant_category)
#     assistant = client.beta.assistants.retrieve(assistant_id)
#
#     # Recuperar el thread actualizado
#     thread = client.beta.threads.retrieve(thread_id)
#     print(assistant.id + " " + str(assistant.tools))
#     # Crear el run
#     run = client.beta.threads.runs.create(
#         thread_id=thread.id,
#         assistant_id=assistant.id,
#         instructions=f"You are having a conversation with {name}",
#     )
#
#     while True:
#         time.sleep(1.5)
#         run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id )
#         # tool_calls = run.required_action
#         # print(str(tool_calls))
#         if run.status == "completed":
#             break
#
#         elif run.status == "requires_action":
#             #print("Requires action" + str(run.required_action))
#             tool_calls = run.required_action.submit_tool_outputs.tool_calls
#
#             tool_outputs = []
#
#             for tool_call in tool_calls:
#                 function_name = tool_call.function.name
#                 arguments = json.loads(tool_call.function.arguments)
#
#                 print("Function name: " + function_name)
#                 print("Arguments: " + str(arguments))
#
#                 result = ejecutar_funcion_por_nombre(function_name, arguments, telefono)
#
#                 tool_outputs.append({
#                     "tool_call_id": tool_call.id,
#                     "output": result
#                 })
#
#             client.beta.threads.runs.submit_tool_outputs(
#                 thread_id=thread.id,
#                 run_id=run.id,
#                 tool_outputs=tool_outputs
#             )
#
#     # Obtener el último mensaje del assistant
#     messages = client.beta.threads.messages.list(thread_id=thread.id)
#     new_message = messages.data[0].content[0].text.value
#     logging.info(f"Generated message: {new_message}")
#     return new_message
#
# def generate_ai_response_facturar(message_body, wa_id, name):
#     logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
#     thread = client.beta.threads.create()
#     thread_id = thread.id
#     message = client.beta.threads.messages.create(
#         thread_id=thread_id,
#         role="user",
#         content=message_body,
#     )
#     new_message = run_assistant(thread.id, name, "Facturar", wa_id)
#     return new_message
#
# def generate_ai_response_monotributista(message_body, wa_id, name):
#     logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
#     thread = client.beta.threads.create()
#     thread_id = thread.id
#     message = client.beta.threads.messages.create(
#         thread_id=thread_id,
#         role="user",
#         content=message_body,
#     )
#     new_message = run_assistant(thread.id, name, "Registrar", wa_id)
#
#     return new_message
#
# def generate_ai_response_informar(message_body, wa_id, name):
#     logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
#     thread = client.beta.threads.create()
#     thread_id = thread.id
#     message = client.beta.threads.messages.create(
#         thread_id=thread_id,
#         role="user",
#         content=message_body,
#     )
#     new_message = run_assistant(thread.id, name, "Informar", wa_id)
#
#     return new_message
#
# def get_assistant_id_from_category(assistant_category):
#     if assistant_category == "Registrar":
#         print("Assistant category is Registrar")
#         return OPENAI_ASSISTANT_ID_REGISTRAR
#     elif assistant_category == "Facturar":
#         print("Assistant category is Facturar")
#         return OPENAI_ASSISTANT_ID_FACTURAS
#     elif assistant_category == "General":
#         print("Assistant category is General")
#         return OPENAI_ASSISTANT_ID_GENERAL
#     else:
#         return OPENAI_ASSISTANT_ID_ORIGINAL
#
# def ejecutar_bot_correcto(nombre_funcion, args, telefono):
#     bot = {
#         "call_facturar_bot": generate_ai_response_facturar,
#         "call_informar_bot": generate_ai_response_informar,
#         "call_monotributista_bot": generate_ai_response_monotributista
#     }
#
#     funcion = bot.get(nombre_funcion)
#     if funcion:
#         object = funcion(telefono, *args.values())
#     else:
#         object = f"Función {nombre_funcion} no encontrada"
#
#     if object is Exception:
#         response = {
#             "error": True,
#             "message": object.args[0]
#         }
#     else:
#         response = {
#             "error": False,
#             "object": object
#         }
#
#     return str(response) if isinstance(response, dict) else response
#
# def ejecutar_funcion_por_nombre(nombre_funcion, args, telefono):
#     funciones = {
#         "call_facturar_bot": generate_ai_response_facturar,
#         "call_informar_bot": generate_ai_response_informar,
#         "call_monotributista_bot": generate_ai_response_monotributista,
#         "crear_factura": FacturaController().crear_factura,
#         "obtener_factura": FacturaController().obtener_factura,
#         "verificar_cliente": MonotributistaController().verificar_cliente,
#         "crear_cliente": MonotributistaController().agregar_cliente,
#         "modificar_cliente": MonotributistaController().modificar_cliente,
#         "obtener_por_cuit": MonotributistaController().obtener_por_cuit
#     }
#
#     funcion = funciones.get(nombre_funcion)
#     if funcion:
#         object = funcion(telefono, *args.values())
#     else:
#         object = f"Función {nombre_funcion} no encontrada"
#
#     if object is Exception:
#         response = {
#             "error": True,
#             "message": object.args[0]
#         }
#     else:
#         response = {
#             "error": False,
#             "object": object
#         }
#
#     return str(response) if isinstance(response, dict) else response
#
# def get_assistant_id_from_category(assistant_category):
#     if assistant_category == "Registrar":
#         return OPENAI_ASSISTANT_ID_REGISTRAR
#     elif assistant_category == "Facturar":
#         return OPENAI_ASSISTANT_ID_FACTURAS
#     elif assistant_category == "General":
#         return OPENAI_ASSISTANT_ID_GENERAL
#     else:
#         return OPENAI_ASSISTANT_ID_ORIGINAL