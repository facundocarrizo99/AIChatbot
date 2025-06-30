import logging
import os
import shelve
import time
import json
from typing import Dict

from dotenv import load_dotenv
from openai import OpenAI

from app.controller.thread_controller import thread_manager, MAX_MESSAGES_PER_THREAD
from app.controller.factura_controller import FacturaController
from app.controller.monotributista_controller import MonotributistaController

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID_ORIGINAL = os.getenv("OPENAI_ASSISTANT_ID_ORIGINAL")
OPENAI_ASSISTANT_ID_FACTURAS = os.getenv("OPENAI_ASSISTANT_ID_FACTURAS")
OPENAI_ASSISTANT_ID_REGISTRAR = os.getenv("OPENAI_ASSISTANT_ID_REGISTRAR")
OPENAI_ASSISTANT_ID_GENERAL = os.getenv("OPENAI_ASSISTANT_ID_GENERAL")
client = OpenAI(api_key=OPENAI_API_KEY)

# Commenting out BotType since we're using a single assistant
# class BotType(Enum):
#     GENERAL = "General"
#     FACTURAR = "Facturar"
#     REGISTRAR = "Registrar"

class OpenAIService:
    def __init__(self):
        # self.assistant_ids = {
        #     BotType.GENERAL: OPENAI_ASSISTANT_ID_GENERAL,
        #     BotType.FACTURAR: OPENAI_ASSISTANT_ID_FACTURAS,
        #     BotType.REGISTRAR: OPENAI_ASSISTANT_ID_REGISTRAR,
        # }
        self.assistant_id = OPENAI_ASSISTANT_ID_ORIGINAL

        # Keeping controllers in case they're needed for other functionality
        self.controllers = {
            'factura': FacturaController(),
            'monotributista': MonotributistaController()
        }
        # Clean up old threads on startup
        thread_manager.cleanup_old_threads()

    def create_thread(self, name: str, wa_id: str) -> str:
        """Get or create a thread for the given WA ID"""
        thread_id, is_new = thread_manager.get_or_create_thread(wa_id, name)
        if is_new:
            logging.info(f"Created new thread for {name} with wa_id {wa_id}")
        else:
            logging.info(f"Reusing existing thread for {name} with wa_id {wa_id}")
        return thread_id

    def add_message_to_thread(self, thread_id: str, message: str) -> None:
        """Add a message to an existing thread"""
        try:
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )
            logging.info(f"Added message to thread {thread_id}")
        except Exception as e:
            logging.error(f"Error adding message to thread: {str(e)}")
            raise

    def run_assistant(self, thread_id: str, name: str, wa_id: str) -> str:
        """Run the assistant and handle any required actions"""
        assistant_id = self.assistant_id  # Using the single assistant ID

        try:
            # Get the current message count
            current_count = next(
                (t['message_count'] for t in thread_manager.threads_db.values()
                 if t['thread_id'] == thread_id), 0)

            # If we're approaching the message limit, start a new thread
            if current_count >= MAX_MESSAGES_PER_THREAD:
                logging.info(f"Message limit reached for thread {thread_id}, creating new thread")
                thread_id = self.create_thread(name, wa_id)

            assistant = client.beta.assistants.retrieve(assistant_id)
            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant.id,
                instructions=f"You are having a conversation with {name} (WA: {wa_id})"
            )

            while True:
                time.sleep(1.5)
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )

                if run.status == "completed":
                    break

                if run.status == "requires_action":
                    self._handle_required_actions(thread_id, run, wa_id)

            # Get the response
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            if not messages.data:
                return "I'm sorry, I couldn't process your request."

            response = messages.data[0].content[0].text.value

            # Update the thread's last activity time
            for wa_id, data in thread_manager.threads_db.items():
                if data['thread_id'] == thread_id:
                    data['last_activity'] = time.time()
                    thread_manager._save_threads()
                    break

            return response

        except Exception as e:
            logging.error(f"Error in run_assistant: {str(e)}")
            return f"I encountered an error: {str(e)}"

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
            if bot_type is not None and isinstance(bot_type, BotType):
                print("BOT TYPE MATCHED:", bot_type.value)
                return self.handle_specific_bot(arguments.get("message", ""), wa_id, arguments.get("name", ""), bot_type)
            # else:
            #     print("BOT TYPE NOT MATCHED - Debug info:")
            #     print("Function name:", function_name)
            #     print("Available mappings:", self._get_bot_type_from_function.__defaults__)
        
        # Handle controller functions
        controller_functions = {
            'crear_factura': self.controllers['factura'].crear_factura,
            'obtener_factura': self.controllers['factura'].obtener_factura,
            'verificar_cliente': self.controllers['monotributista'].verificar_cliente,
            'crear_cliente': self.controllers['monotributista'].agregar_cliente,
            'modificar_cliente': self.controllers['monotributista'].modificar_cliente,
            'obtener_por_cuit': self.controllers['monotributista'].obtener_por_cuit,
            'crear_monotributista': self.controllers['monotributista'].crear_monotributista
        }

        func = controller_functions.get(function_name)
        print("SE INTENTA EJECUTAR LA FUNCION: ", func)
        print("Argunmentos: ", arguments)
        if not func:
            return f"Function {function_name} not found"

        try:
            result = func(wa_id, *arguments.values())
            return str(result)
        except Exception as e:
            logging.error(f"Error executing {function_name}: {str(e)}")
            return str({"error": True, "message": str(e)})

    def process_message(self, message: str, wa_id: str, name: str) -> str:
        """Main entry point for processing messages"""
        thread_id = self.create_thread(name, wa_id)
        self.add_message_to_thread(thread_id, message)
        return self.run_assistant(thread_id, name, wa_id)

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

