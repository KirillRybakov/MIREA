import os
import tarfile
import json

try:
    import readline  # Для Unix-подобных ОС
except ImportError:
    import pyreadline as readline  # Для Windows


class ShellEmulator:
    def __init__(self, tar_file_path, shell_invite):
        self.shell_invite = shell_invite
        self.tar_file_path = tar_file_path
        self.current_path = "/"  # Начальный путь как в UNIX
        self.file_system = {}

        # Загружаем файловую систему из tar
        self.load_file_system()

    def load_file_system(self):
        # Распаковка tar-файла в словарь self.file_system
        with tarfile.open(self.tar_file_path) as tar:
            for member in tar.getmembers():
                self.file_system[member.name] = member


    def ls(self):
        # Получаем полный путь текущей директории
        path = self._get_full_path(self.current_path).replace("\\", "./")

        # Находим все элементы, находящиеся внутри текущей директории
        contents = [name for name in self.file_system if name.startswith(path) and name != path]
        display_names = set()

        for content in contents:
            # Получаем относительное имя и первую часть пути
            rel_path = content[len(path):].strip("/")
            display_name = rel_path.split("/", 1)[0]
            display_names.add(display_name)

        print("  ".join(sorted(display_names)))

    def cd(self, path=None):
        # Если path не указан или указан как "..", возвращаемся в корень
        if path is None or path == "..":
            self.current_path = "/"
            return

        # Меняем текущую директорию на указанную в path
        new_path = self._get_new_path(path)
        full_path = self._get_full_path(new_path).replace("\\", "./")

        # Проверка, существует ли целевая директория
        if full_path in self.file_system and self.file_system[full_path].isdir():
            self.current_path = new_path
        else:
            print(f"cd: no such file or directory: {path}")

    def pwd(self):
        # Выводим текущий путь
        print(self.current_path)

    def mv(self, src, dst):
        # Получаем абсолютные пути для исходного и целевого файлов
        src_path = '.' + self._get_full_path(os.path.join(self.current_path, src)).replace("\\", "/")
        dst_path = '.' + self._get_full_path(os.path.join(self.current_path, dst)).replace("\\", "/")

        # Проверка существования исходного файла или директории
        if src_path not in self.file_system:
            print(self.file_system)
            print(f"mv: cannot stat '{src_path}': No such file or directory")
            return

        # Если целевой путь существует и является файлом, ошибка
        if dst_path in self.file_system and self.file_system[dst_path].isfile():
            print(f"mv: cannot move '{src}' to '{dst}': File exists")
            return

        # Проверка, если целевой путь является существующей директорией
        if dst_path in self.file_system and self.file_system[dst_path].isdir():
            # Перемещаем в существующую директорию
            dst_path = os.path.join(dst_path, os.path.basename(src_path)).replace("\\", "./")

        # Выполняем переименование/перемещение
        items_to_move = {key: value for key, value in self.file_system.items() if key.startswith(src_path)}
        for old_path, item in items_to_move.items():
            # Обновляем путь каждого элемента
            new_path = old_path.replace(src_path, dst_path, 1)
            self.file_system[new_path] = self.file_system.pop(old_path)

        print(f"Moved '{src}' to '{dst}'")

    def cat(self, filename):
        # Генерируем полный путь к файлу, учитывая текущую директорию
        full_path = self._get_full_path(os.path.join(self.current_path, filename)).replace("\\", "/")
        print(f"[DEBUG] Trying to access file at path: '{full_path}'")

        # Проверяем, существует ли файл в файловой системе
        if '.' + full_path in self.file_system:
            file_info = self.file_system['.'+full_path]

            # Проверяем, является ли указанный путь файлом, а не директорией
            if file_info.isfile():
                # Пытаемся прочитать содержимое файла из архива
                with tarfile.open(self.tar_file_path) as tar:
                    try:
                        file_content = tar.extractfile(file_info)
                        if file_content:
                            print(file_content.read().decode('utf-8'))
                        else:
                            print(f"cat: {filename}: Cannot read file content")
                    except KeyError:
                        print(f"cat: {filename}: No such file or directory in archive")
            else:
                print(f"cat: {filename}: Is a directory")
        else:
            print(f"cat: {filename}: No such file or directory")


    def mkdir(self, dirname):
        # Преобразуем путь новой директории в абсолютный
        dir_path = self._get_full_path(os.path.join(self.current_path, dirname)).replace("\\", "./")

        # Проверяем, существует ли уже директория или файл с таким именем
        if dir_path in self.file_system:
            print(f"mkdir: cannot create directory '{dirname}': Directory exists")
            return

        # Создаем новый объект TarInfo для директории и добавляем в файловую систему
        new_dir = tarfile.TarInfo(name=dir_path)
        new_dir.type = tarfile.DIRTYPE
        self.file_system[dir_path] = new_dir

    def head(self, filename, num_lines=10):
        # Генерируем полный путь к файлу, учитывая текущую директорию
        full_path = '.' + self._get_full_path(os.path.join(self.current_path, filename)).replace("\\", "/")
        print(f"[DEBUG] Trying to access file at path: '{full_path}'")

        # Проверяем, существует ли файл в файловой системе
        if full_path in self.file_system:
            file_info = self.file_system[full_path]

            # Проверяем, является ли указанный путь файлом, а не директорией
            if file_info.isfile():
                # Пытаемся прочитать содержимое файла из архива
                with tarfile.open(self.tar_file_path) as tar:
                    try:
                        file_content = tar.extractfile(file_info)
                        if file_content:
                            # Чтение и декодирование содержимого файла
                            lines = file_content.read().decode('utf-8').splitlines()
                            # Вывод первых num_lines строк
                            for line in lines[:num_lines]:
                                print(line)
                        else:
                            print(f"head: {filename}: Cannot read file content")
                    except KeyError:
                        print(f"head: {filename}: No such file or directory in archive")
            else:
                print(f"head: {filename}: Is a directory")
        else:
            print(f"head: {filename}: No such file or directory")

    def _get_full_path(self, path):
        # Преобразуем относительный путь в абсолютный
        return os.path.normpath(path)

    def _get_new_path(self, path):
        # Вычисляем новый путь в зависимости от относительного пути
        if path == "..":
            return os.path.dirname(self.current_path)
        elif path.startswith("/"):
            return path
        else:
            return os.path.join(self.current_path, path)

    def run(self):
        # Основной цикл эмуляции командной строки
        while True:
            try:
                command = input(f"{self.shell_invite}:{self.current_path}$ ")
                if command.startswith("ls"):
                    self.ls()
                elif command.startswith("cd"):
                    # Разделяем команду с учетом возможного отсутствия аргументов
                    parts = command.split(maxsplit=1)
                    path = parts[1] if len(parts) > 1 else None
                    self.cd(path)
                elif command == "pwd":
                    self.pwd()
                elif command.startswith("mv "):
                    # Разделяем команду на исходный и целевой путь
                    _, src, dst = command.split(maxsplit=2)
                    self.mv(src, dst)
                elif command.startswith("cat "):
                    _, filename = command.split(maxsplit=1)
                    self.cat(filename)
                elif command.startswith("mkdir "):
                    _, dirname = command.split(maxsplit=1)
                    self.mkdir(dirname)
                elif command.startswith("head "):
                    # Обработка команды head с указанием числа строк
                    parts = command.split()
                    filename = parts[1]
                    num_lines = int(parts[2]) if len(parts) > 2 else 10
                    self.head(filename, num_lines)
                elif command == "exit":
                    print("Выход из shell")
                    break
                elif command == "test":
                    self.test_commands()
                else:
                    print(f"{command}: command not found")
            except KeyboardInterrupt:
                print("\nВыход из shell")
                break




# Запуск эмулятора
if __name__ == "__main__":
    with open("config.json", 'r') as file:
        config = json.load(file)

    ShellEmulator(config['path'], config['name']).run()
