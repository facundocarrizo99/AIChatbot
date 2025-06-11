
import unittest

from openai import OpenAI
from app.services.openai_service import generate_ai_response, check_if_thread_exists, OPENAI_API_KEY


class MyTestCase(unittest.TestCase):
    def test_return_function(self):
        text = "crear factura a Juan Perez"
        response = generate_ai_response(text, "5491123456789", "Macarena")
        print(response)
        self.assertEqual(True, False)  # add assertion here

    def test_borrar_thread(self):
        client = OpenAI(api_key=OPENAI_API_KEY)
        wa_id = "541134031128"
        thread_id = check_if_thread_exists(wa_id)
        print(thread_id)
        response = client.beta.threads.delete(thread_id)
        self.assertEqual(True, response.get("deleted"))  # add assertion here
