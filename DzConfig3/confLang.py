import argparse
import json
import sys


def translate(json_data, constants=None, indent_level=0):
    if constants is None:
        constants = {}

    result = []

    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if key.startswith("def "):
                const_name = key[4:].strip()
                constants[const_name] = int(value)
                result.append(f"def {const_name} := {value}")
            elif isinstance(value, dict):
                result.append(f"{key} {handle_dictionaries(value, constants, indent_level)}")
            elif key == "комментарий":
                comment = handle_multiline_comments(value)
                if comment:
                    result.append(comment)
            else:
                result.append(f"{key} = {handle_value(value, constants, indent_level)}")
    else:
        raise ValueError("JSON должен быть объектом верхнего уровня (dict)")

    return "\n".join(result)


# Функция для обработки многострочных комментариев
def handle_multiline_comments(value):
    if isinstance(value, str) and value.startswith("#|") and value.endswith("|#"):
        # Если строка - это многострочный комментарий, выводим как комментарий
        return f"#|\n{value[2:-2].strip()}\n|#"
    return None


# Функция для обработки значений (число, строка или словарь)
def handle_value(value, constants, indent_level=0):
    # Проверяем многострочный комментарий
    comment = handle_multiline_comments(value)
    if comment:
        return comment  # Если это комментарий, возвращаем его

    if isinstance(value, dict):
        # Если значение — это словарь, вызываем обработку словаря
        return handle_dictionaries(value, constants, indent_level)
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        # Обрабатываем выражение ^{имя_константы}
        if value.startswith("^{"):
            const_name = value[2:-1]  # Извлекаем имя константы
            if const_name in constants:
                return str(constants[const_name])  # Подставляем значение константы
            else:
                raise ValueError(f"Неизвестная константа: {const_name}")
        return f'"{value}"'
    return str(value)


# Функция для обработки словарей с отступами
def handle_dictionaries(data, constants, indent_level):
    """
    Обрабатывает словари, возвращая их представление в виде $[ ... ].

    :param data: Входной словарь
    :param constants: Словарь констант
    :param indent_level: Уровень отступа для вложенных структур
    :return: Строка, представляющая словарь в учебном языке
    """
    indent = "    " * indent_level
    nested_indent = "    " * (indent_level + 1)
    lines = ["$["]

    items = list(data.items())

    for i, (key, value) in enumerate(items):
        if isinstance(value, dict):
            # Рекурсивная обработка вложенного словаря
            lines.append(f"{nested_indent}{key} {handle_dictionaries(value, constants, indent_level + 1)}")
        else:
            # Обычное ключ-значение
            lines.append(f"{nested_indent}{key} : {handle_value(value, constants, indent_level + 1)}")

        # Если это не последний элемент, добавляем запятую
        if i < len(items) - 1:
            lines[-1] += ","

    lines.append(f"{indent}]")
    return "\n".join(lines)

# Функция для обработки объявления и вычисления констант
def handle_definitions(data, constants, indent_level=0):
    result = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "комментарий":
                # Обрабатываем комментарий отдельно
                comment = handle_multiline_comments(value)
                if comment:
                    result.append(f"{'    ' * indent_level}{comment}")
                continue  # Пропускаем ключ "комментарий", так как он уже будет обработан
            if isinstance(value, dict):
                # Если это вложенный словарь, добавляем отступы и рекурсивно вызываем обработку
                result.append(f"{key} {handle_dictionaries(value, constants, indent_level)}")
            elif isinstance(value, str) and value.startswith("def"):
                # Это объявление константы
                const_name, const_value = value[4:].split(" := ")
                constants[const_name.strip()] = const_value.strip()
                result.append(f"def {const_name.strip()} := {const_value.strip()}")
            else:
                result.append(f"{'    ' * indent_level}{key} = {handle_value(value, constants, indent_level)}")
    return "\n".join(result)


# Главная функция для парсинга JSON и генерации конфигурационного текста
def json_to_config(data):
    constants = {}
    config_text = handle_definitions(data, constants)
    return config_text


# Главная функция для работы с командной строкой
def main():
    parser = argparse.ArgumentParser(description='Конвертирование JSON в конфигурационный язык.')
    parser.add_argument('file', help='Путь к файлу JSON')

    args = parser.parse_args()

    try:
        # Чтение входного JSON файла
        with open(args.file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # Преобразуем JSON в конфигурационный язык
        config_text = json_to_config(json_data)

        # Выводим результат на стандартный вывод
        print(config_text)

    except FileNotFoundError:
        print(f"Ошибка: Файл {args.file} не найден.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Ошибка: Некорректный JSON в файле {args.file}. Ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
