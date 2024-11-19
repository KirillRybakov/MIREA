import argparse
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(description="Анализ зависимостей пакетов с визуализацией графов")

    # Путь к программе визуализации графов
    parser.add_argument('-v', '--visualizer', required=True,
                        help="Путь к программе для визуализации графов (например, mmdc)")

    # Имя пакета для анализа
    parser.add_argument('-p', '--package', required=True, help="Имя анализируемого пакета")

    # Максимальная глубина анализа зависимостей
    parser.add_argument('-d', '--depth', type=int, default=3,
                        help="Максимальная глубина анализа зависимостей (по умолчанию 3)")

    # URL репозитория для получения информации о зависимостях
    parser.add_argument('-r', '--repo', required=True, help="URL-адрес репозитория для анализа")

    return parser.parse_args()


def analyze_dependencies(package, depth, repo_url):
    print(f"Получение зависимостей для пакета: {package}")
    # Пример команды для получения зависимостей пакета

    command = f"apt-cache depends {package}"
    print(f"Выполнение команды: {command}")
    subprocess.run(command, shell=True)


def generate_mermaid_code(package, depth, repo_url):
    print(f"Генерация графа зависимостей для пакета {package} с глубиной {depth} и репозиторием {repo_url}")

    mermaid_code = f"""
    graph TD
          {package} --> dep1
          dep1 --> dep2
          dep2 --> dep3
    """
    return mermaid_code


def visualize_graph(visualizer, mermaid_code):
    # Сохраняем код графа в файл
    with open('graph.mmd', 'w') as file:
        file.write(mermaid_code)

    # Визуализируем граф с помощью внешней программы (например, mmdc)
    print(f"Визуализация графа с помощью {visualizer}")
    command = f"{visualizer} -i graph.mmd -o graph.png"
    subprocess.run(command, shell=True)


def main():
    args = parse_args()

    # Получаем зависимости и генерируем код Mermaid
    analyze_dependencies(args.package, args.depth, args.repo)
    mermaid_code = generate_mermaid_code(args.package, args.depth, args.repo)

    # Визуализируем граф
    visualize_graph(args.visualizer, mermaid_code)


if __name__ == "__main__":
    main()
