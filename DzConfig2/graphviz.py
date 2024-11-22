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


def get_package_dependencies(package_name):
    """
    Получить зависимости для указанного пакета с помощью команды apt-cache.
    """
    try:
        result = subprocess.run(
            ["apt-cache", "depends", package_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды: {e.stderr}")
        return ""


def parse_dependencies(raw_dependencies):
    """
    Разобрать вывод команды apt-cache в формат зависимостей.
    """
    dependencies = []
    for line in raw_dependencies.splitlines():
        line = line.strip()
        if line.startswith("Depends:"):
            dep = line.split("Depends:")[1].strip()
            # Убираем символы < >, чтобы не было синтаксических ошибок в Mermaid
            dep = dep.replace('<', '').replace('>', '')
            dependencies.append(dep)
    return dependencies


def build_dependency_graph(package_name, max_depth):
    """
    Построить граф зависимостей пакета в формате Mermaid с учётом глубины.
    """
    visited = set()  # Для отслеживания посещённых пакетов
    edges = []  # Для хранения рёбер графа

    def dfs(package, current_depth):
        if current_depth > max_depth:
            return
        if package in visited:
            return
        visited.add(package)

        raw_dependencies = get_package_dependencies(package)
        dependencies = parse_dependencies(raw_dependencies)

        for dep in dependencies:
            edges.append((package, dep))
            dfs(dep, current_depth + 1)

    # Построение графа начиная с указанного пакета
    dfs(package_name, 1)

    # Генерация Mermaid-графа
    mermaid = ["graph TD"]
    for parent, child in edges:
        mermaid.append(f"  {parent} --> {child}")
    return "\n".join(mermaid)


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

    package_name = args.package
    print(f"Получение зависимостей для пакета: {package_name}")

    try:
        # Генерация графа зависимостей с учётом глубины
        mermaid_code = build_dependency_graph(package_name, args.depth)

        # Печать кода Mermaid в терминал
        print("Сгенерированный код Mermaid:")
        print(mermaid_code)

        # Сохранение графа в файл
        output_file = "graph.mmd"
        with open(output_file, "w") as file:
            file.write(mermaid_code)
        print(f"Граф зависимостей сохранён в файле '{output_file}'.")
        print("Откройте его в Mermaid Live Editor: https://mermaid-js.github.io/mermaid-live-editor/")

        # Визуализируем граф
        visualize_graph(args.visualizer, mermaid_code)

    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
