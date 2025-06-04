import logging
import os
import shelve
import time
from unicodedata import category

from dotenv import load_dotenv
from openai import OpenAI

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


def run_assistant(thread_id, name, assistant_category):
    assistant_id = get_assistant_id_from_category(assistant_category)
    assistant = client.beta.assistants.retrieve(assistant_id)

    # Recuperar el thread actualizado
    thread = client.beta.threads.retrieve(thread_id)

    # Crear el run
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=f"You are having a conversation with {name}",
    )

    # Esperar a que termine
    while run.status != "completed":
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Obtener los mensajes
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    for message in messages.data:
        if message.role == "assistant":
            return message.content[0].text.value

    return "No assistant response found."

def generate_ai_response(message_body, wa_id, name):
    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)
    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id
    # Otherwise, retrieve the existing thread
    else:
        logging.info(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id)

    # Add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )

    # Run the assistant and get the new message
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