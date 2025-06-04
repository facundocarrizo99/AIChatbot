import unittest
from app.services.openai_service import generate_ai_response

class MyTestCase(unittest.TestCase):
    def test_generate_message(self):  # add assertion here
        message = generate_ai_response("hola", "5491123456789", "Macarena Algo")

if __name__ == '__main__':
    unittest.main()
