import unittest
from app.utils.string_utils import getOnlyJsonFrom


class TestStringToJson(unittest.TestCase):
    def test_extract_json_from_markdown_block(self):
        input = """Perfecto, aquí tienes el registro completo como monotributista con los datos adicionales:
                ```json
                {
                  "type": "monotributista",
                  "cuit": "2042214828",
                  "full_name": "Facundo Carrizo",
                  "social_reason": "Facudno SRL",
                  "monotributo_category": "A",
                  "activity": "Proveedor de servicios",
                  "tax_address": "urquiza 2271",
                  "phone": "1134031128",
                  "email": "facundocarrizo@gmail.com",
                  "condition_IVA": "01",
                  "point_of_sale": 1
                }
                ```
                ¿Querés que lo registre o hay alguna otra cosa que quieras agregar?"""
        expected_output = {
                  "type": "monotributista",
                  "cuit": "2042214828",
                  "full_name": "Facundo Carrizo",
                  "social_reason": "Facudno SRL",
                  "monotributo_category": "A",
                  "activity": "Proveedor de servicios",
                  "tax_address": "urquiza 2271",
                  "phone": "1134031128",
                  "email": "facundocarrizo@gmail.com",
                  "condition_IVA": "01",
                  "point_of_sale": 1
        }
        result = getOnlyJsonFrom(input)
        self.assertEqual(result, expected_output)  # add assertion here


if __name__ == '__main__':
    unittest.main()
