import logging
import os
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

_client = None


def _get_openai_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


class OpenAIService:
    def __init__(self):
        self.assistant_id = OPENAI_ASSISTANT_ID_ORIGINAL
        self.controllers = {
            'factura': FacturaController(),
            'monotributista': MonotributistaController()
        }
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
            _get_openai_client().beta.threads.messages.create(
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

            assistant = _get_openai_client().beta.assistants.retrieve(assistant_id)
            run = _get_openai_client().beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant.id,
                instructions=f"You are having a conversation with {name} (WA: {wa_id})"
            )

            while True:
                time.sleep(1.5)
                run = _get_openai_client().beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )

                if run.status == "completed":
                    break

                if run.status == "requires_action":
                    self._handle_required_actions(thread_id, run, wa_id)

            # Get the response
            messages = _get_openai_client().beta.threads.messages.list(thread_id=thread_id)
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

        _get_openai_client().beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )

    def _execute_function(self, function_name: str, arguments: Dict, wa_id: str) -> str:
        """Execute a function based on its name and return the result"""
        logging.info(f"Executing function: {function_name}")

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
        logging.info(f"Resolved function: {func}, arguments: {arguments}")
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

_openai_service = None


def _get_openai_service():
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service


# Public interface functions
def generate_ai_response(message_body: str, wa_id: str, name: str) -> str:
    """Main entry point for generating AI responses"""
    return _get_openai_service().process_message(message_body, wa_id, name)

