
import unittest

from openai import OpenAI
from app.services.openai_service import generate_ai_response, OPENAI_API_KEY


class TestOpenAIService(unittest.TestCase):
    def test_return_function(self):
        text = "crear factura a Juan Perez"
        response = generate_ai_response(text, "5491123456789", "Macarena")
        print(response)
        self.assertIsInstance(response, str)

    def test_generate_message(self):
        message = generate_ai_response("hola", "5491123456789", "Macarena Algo")
        self.assertIsInstance(message, str)
