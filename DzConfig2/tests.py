import unittest
from unittest.mock import patch, MagicMock
import subprocess
import io
import sys

# Импортируем функции из вашего скрипта
from graphviz import parse_args, analyze_dependencies, generate_mermaid_code, visualize_graph


class TestDependencyVisualizer(unittest.TestCase):

    # Тест для функции parse_args
    def test_parse_args(self):
        test_args = ["script_name", "-v", "mmdc", "-p", "curl", "-d", "3", "-r", "https://example.com"]
        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            self.assertEqual(args.visualizer, "mmdc")
            self.assertEqual(args.package, "curl")
            self.assertEqual(args.depth, 3)
            self.assertEqual(args.repo, "https://example.com")

    # Тест для функции analyze_dependencies
    @patch('subprocess.run')
    def test_analyze_dependencies(self, mock_run):
        # Мокаем subprocess.run, чтобы избежать реальных вызовов команд
        mock_run.return_value = MagicMock(returncode=0)

        # Проверка на выполнение правильной команды
        analyze_dependencies("curl", 3, "https://example.com")
        mock_run.assert_called_with("apt-cache depends curl", shell=True)

    # Тест для функции generate_mermaid_code
    def test_generate_mermaid_code(self):
        package = "curl"
        depth = 3
        repo_url = "https://example.com"

        # Проверка, что функция генерирует правильный код Mermaid
        expected_code = """
        graph TD
          curl --> dep1
          dep1 --> dep2
          dep2 --> dep3
        """
        mermaid_code = generate_mermaid_code(package, depth, repo_url)
        self.assertEqual(mermaid_code.strip(), expected_code.strip())

    # Тест для функции visualize_graph
    @patch('subprocess.run')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_visualize_graph(self, mock_open, mock_run):
        visualizer = "mmdc"
        mermaid_code = "graph TD\n  A --> B"

        # Мокаем open и subprocess.run
        mock_run.return_value = MagicMock(returncode=0)

        # Визуализируем граф
        visualize_graph(visualizer, mermaid_code)

        # Проверка, что файл был записан
        mock_open.assert_called_with('graph.mmd', 'w')
        mock_open.return_value.write.assert_called_with(mermaid_code)

        # Проверка, что команда для визуализации была выполнена
        mock_run.assert_called_with(f"{visualizer} -i graph.mmd -o graph.png", shell=True)


if __name__ == '__main__':
    unittest.main()
