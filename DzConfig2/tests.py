import unittest
from unittest.mock import patch, MagicMock
import subprocess
from io import StringIO
import sys


# Импортируем функции из вашего кода
from graphviz import parse_args, get_package_dependencies, parse_dependencies, build_dependency_graph, visualize_graph


class TestDependencyAnalyzer(unittest.TestCase):

    @patch('subprocess.run')
    def test_get_package_dependencies_success(self, mock_run):
        # Подготовим мок для subprocess.run
        mock_run.return_value = MagicMock(stdout="Depends: libcurl4\nDepends: ca-certificates", stderr='', returncode=0)

        result = get_package_dependencies("curl")
        self.assertIn("Depends: libcurl4", result)
        self.assertIn("Depends: ca-certificates", result)

    @patch('subprocess.run')
    def test_get_package_dependencies_failure(self, mock_run):
        # Мокируем ошибку subprocess.run
        mock_run.side_effect = subprocess.CalledProcessError(1, 'apt-cache', 'Error occurred')

        result = get_package_dependencies("curl")
        self.assertEqual(result, "")

    def test_parse_dependencies(self):
        raw_dependencies = "Depends: libcurl4\nDepends: ca-certificates"
        result = parse_dependencies(raw_dependencies)
        self.assertEqual(result, ['libcurl4', 'ca-certificates'])

    @patch('subprocess.run')
    def test_build_dependency_graph(self, mock_run):
        # Мокируем возвращаемое значение get_package_dependencies
        mock_run.return_value = MagicMock(stdout="Depends: libcurl4\nDepends: ca-certificates", stderr='', returncode=0)

        # Запускаем тест на build_dependency_graph
        mermaid_code = build_dependency_graph("curl", 1)
        self.assertIn("graph TD", mermaid_code)
        self.assertIn("curl --> libcurl4", mermaid_code)
        # self.assertIn("libcurl4 --> ca-certificates", mermaid_code)

    @patch('subprocess.run')
    @patch('builtins.open', new_callable=MagicMock)
    def test_visualize_graph(self, mock_open, mock_subprocess):
        # Мокируем процесс визуализации
        mock_subprocess.return_value = MagicMock(stdout='', stderr='', returncode=0)
        mermaid_code = "graph TD\n    curl --> libcurl4"

        # Мокаем open, чтобы проверить сохранение графа в файл
        mock_open.return_value = MagicMock()

        # Визуализация
        visualize_graph("mmdc", mermaid_code)

        # Проверка, что команда subprocess была вызвана
        mock_subprocess.assert_called_with("mmdc -i graph.mmd -o graph.png", shell=True)

        # Проверка, что граф был сохранён в файл
        mock_open.assert_called_with('graph.mmd', 'w')

    def test_parse_args(self):
        # Проверка корректности парсинга аргументов
        test_args = ['graphviz.py', '-v', 'mmdc', '-p', 'curl', '-d', '2', '-r', 'https://archive.ubuntu.com/ubuntu']
        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            self.assertEqual(args.visualizer, 'mmdc')
            self.assertEqual(args.package, 'curl')
            self.assertEqual(args.depth, 2)
            self.assertEqual(args.repo, 'https://archive.ubuntu.com/ubuntu')

    @patch('subprocess.run')
    def test_build_dependency_graph_with_max_depth(self, mock_run):
        # Мокируем возвращаемое значение get_package_dependencies
        mock_run.return_value = MagicMock(stdout="Depends: libcurl4\nDepends: ca-certificates", stderr='', returncode=0)

        # Запуск теста
        mermaid_code = build_dependency_graph("curl", 1)
        self.assertIn("graph TD", mermaid_code)
        self.assertIn("curl --> libcurl4", mermaid_code)
        self.assertNotIn("libcurl4 --> ca-certificates", mermaid_code)

    @patch('subprocess.run')
    def test_build_dependency_graph_without_dependencies(self, mock_run):
        # Мокируем, что пакет не имеет зависимостей
        mock_run.return_value = MagicMock(stdout="", stderr='', returncode=0)

        mermaid_code = build_dependency_graph("curl", 1)
        self.assertIn("graph TD", mermaid_code)
        self.assertNotIn("curl -->", mermaid_code)

    def test_parse_dependencies_empty(self):
        raw_dependencies = ""
        result = parse_dependencies(raw_dependencies)
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
