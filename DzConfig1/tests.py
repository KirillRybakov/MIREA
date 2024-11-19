import unittest
import os
import tarfile
from io import StringIO, BytesIO
from emulator import ShellEmulator  # Импортируем ShellEmulator

class TestShellEmulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Создаем временный tar-архив с файловой системой для тестов
        cls.test_tar_path = "test_virtual_fs.tar"
        with tarfile.open(cls.test_tar_path, "w") as tar:
            # Создаем файлы и директории в tar-архиве
            for name in ["file1.txt", "file2.txt", "/dir1/", "dir2/"]:
                info = tarfile.TarInfo(f"./{name}")  # Добавляем ./ перед именами
                if name.endswith("/"):
                    info.type = tarfile.DIRTYPE
                else:
                    file_content = f"Contents of {name}".encode("utf-8")  # Преобразуем строку в байты
                    info.size = len(file_content)
                    tar.addfile(info, BytesIO(file_content))

    def setUp(self):
        # Инициализируем эмулятор с тестовым tar-архивом
        self.shell = ShellEmulator(TestShellEmulator.test_tar_path, "test_shell")

    def test_ls(self):
        # Тестируем вывод содержимого корневой директории
        output = self._capture_stdout(self.shell.ls)
        self.assertIn("file1.txt", output)
        self.assertIn("file2.txt", output)


    def test_ls_in_directory(self):
        # Переход в директорию dir1 и проверка, что ls показывает содержимое директории
        self.shell.cd("dir1")
        output = self._capture_stdout(self.shell.ls)
        self.assertEqual(output.strip(), "file1.txt  file2.txt")

    def test_cd(self):
        # Проверка смены директории
        self.shell.cd("dir1")
        self.shell.cd("/")
        self.assertEqual(self.shell.current_path, "/")

    def test_cd_nonexistent_directory(self):
        # Проверка попытки смены директории на несуществующую
        output = self._capture_stdout(lambda: self.shell.cd("nonexistent"))
        self.assertIn("no such file or directory", output)

    def test_cd_back_to_root(self):
        # Проверка возвращения в корень
        self.shell.cd("dir1")
        self.shell.cd("..")
        self.assertEqual(self.shell.current_path, "/")

    def test_pwd(self):
        # Проверка отображения текущей директории
        output = self._capture_stdout(self.shell.pwd)
        self.assertEqual(output.strip(), "/")

    def test_mkdir(self):
        # Создание новой директории и проверка ее существования
        self.shell.mkdir("dir3")
        self.assertIn("./dir3", self.shell.file_system)
    #
    def test_mkdir_existing_directory(self):
        # Попытка создания существующей директории
        output = self._capture_stdout(lambda: self.shell.mkdir("dir1"))

    def test_mv_file(self):
        # Перемещение файла
        self.shell.mv("file1.txt", "dir2/file1.txt")
        self.assertIn("./dir2/file1.txt", self.shell.file_system)
        self.assertNotIn("./file1.txt", self.shell.file_system)

    def test_mv_nonexistent_file(self):
        # Перемещение несуществующего файла
        output = self._capture_stdout(lambda: self.shell.mv("nonexistent.txt", "dir1/nonexistent.txt"))
        self.assertIn("No such file or directory", output)

    def test_mv_to_existing_file(self):
        # Попытка перемещения в существующий файл
        output = self._capture_stdout(lambda: self.shell.mv("file1.txt", "file2.txt"))
        self.assertIn("File exists", output)

    def test_cat(self):
        # Чтение содержимого файла
        output = self._capture_stdout(lambda: self.shell.cat("file1.txt"))
        self.assertEqual(output.strip(), "[DEBUG] Trying to access file at path: '/file1.txt'\nContents of file1.txt")

    def test_cat_directory(self):
        # Попытка чтения директории
        output = self._capture_stdout(lambda: self.shell.cat("dir1"))
        self.assertIn("[DEBUG] Trying to access file at path: '/dir1'\ncat: dir1: No such file or directory\n", output)

    def test_cat_nonexistent_file(self):
        # Попытка чтения несуществующего файла
        output = self._capture_stdout(lambda: self.shell.cat("nonexistent.txt"))
        self.assertIn("No such file or directory", output)

    def test_head(self):
        # Чтение первых 10 строк файла (или меньше)
        output = self._capture_stdout(lambda: self.shell.head("file1.txt"))
        self.assertIn("Contents of file1.txt", output)

    def test_head_nonexistent_file(self):
        # Попытка чтения несуществующего файла
        output = self._capture_stdout(lambda: self.shell.head("nonexistent.txt"))
        self.assertIn("No such file or directory", output)

    # Вспомогательный метод для захвата вывода функций
    def _capture_stdout(self, func):
        import sys
        from io import StringIO
        # Сохраняем текущее состояние stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        try:
            func()
            return captured_output.getvalue()
        finally:
            sys.stdout = old_stdout

    @classmethod
    def tearDownClass(cls):
        # Удаляем временный tar-архив после тестов
        if os.path.exists(cls.test_tar_path):
            os.remove(cls.test_tar_path)


if __name__ == "__main__":
    unittest.main()
