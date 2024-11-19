import unittest
from confLang import handle_value, handle_dictionaries, translate  # Импорт функций из основной программы

class TestConfLang(unittest.TestCase):

    def test_simple_key_value(self):
        # Простой JSON с несколькими ключами-значениями
        json_data = {
            "ключ1": "значение1",
            "ключ2": 42
        }
        expected_output = 'ключ1 = "значение1"\nключ2 = 42'
        constants = {}
        result = translate(json_data, constants)
        self.assertEqual(result, expected_output)

    def test_nested_dictionaries(self):
        # Словари с вложенной структурой
        json_data = {
            "словарь": {
                "ключ1": "значение1",
                "вложенный_словарь": {
                    "ключ2": 42
                }
            }
        }
        expected_output = (
            'словарь $[\n'
            '    ключ1 : "значение1",\n'
            '    вложенный_словарь $[\n'
            '        ключ2 : 42\n'
            '    ]\n'
            ']'
        )
        constants = {}
        result = translate(json_data, constants)
        self.assertEqual(result, expected_output)

    def test_constants_and_expressions(self):
        # Константы и выражения
        json_data = {
            "def число": "100",
            "выражение": "^{число}"
        }
        expected_output = 'def число := 100\nвыражение = 100'
        constants = {}
        result = translate(json_data, constants)
        self.assertEqual(result, expected_output)

    def test_multiline_comment(self):
        # Многострочный комментарий
        json_data = {
            "комментарий": "#| Этот комментарий\nпродолжается на несколько строк\n|#"
        }
        expected_output = '#|\nЭтот комментарий\nпродолжается на несколько строк\n|#'
        constants = {}
        result = translate(json_data, constants)
        self.assertEqual(result, expected_output)

    def test_complex_structure(self):
        # Сложная структура с вложенностью, комментариями и константами
        json_data = {
            "ключ1": "значение1",
            "ключ2": 42,
            "словарь": {
                "ключ3": "значение3",
                "вложенный_словарь": {
                    "ключ4": 56
                }
            },
            "def число": "100",
            "выражение": "^{число}",
            "комментарий": "#| Это тестовый комментарий\nс новой строкой\n|#"
        }
        expected_output = (
            'ключ1 = "значение1"\n'
            'ключ2 = 42\n'
            'словарь $[\n'
            '    ключ3 : "значение3",\n'
            '    вложенный_словарь $[\n'
            '        ключ4 : 56\n'
            '    ]\n'
            ']\n'
            'def число := 100\n'
            'выражение = 100\n'
            '#|\n'
            'Это тестовый комментарий\n'
            'с новой строкой\n'
            '|#'
        )
        constants = {}
        result = translate(json_data, constants)
        self.assertEqual(result, expected_output)

if __name__ == "__main__":
    unittest.main()
