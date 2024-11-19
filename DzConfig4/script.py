import os
import sys
import struct
import json

class Assembler:
    def __init__(self):
        # Маппинг инструкций в бинарные коды
        self.instructions = {
            'LOAD': 1,
            'STORE': 2,
            'ADD': 3,
            'SUB': 4,
            'JUMP': 5,
            'HALT': 6,
            'LOAD_CONSTANT': 27,  # Команда для загрузки константы
            'LOAD_MEMORY': 13
        }

    def load_constant(self, B):
        # Команда LOAD_CONSTANT
        op_code = self.instructions['LOAD_CONSTANT']
        # Преобразуем операнд в бинарное представление
        return struct.pack('B', op_code) + struct.pack('I', B)

    def load_memory(self):
        # Команда LOAD_MEMORY
        op_code = self.instructions['LOAD_MEMORY']
        # Формируем команду без операнда (поскольку операнд берется из стека)
        return struct.pack('B', op_code) + b'\x00\x00\x00'

        # Преобразуем в байты
        return struct.pack('I', instruction)

    # def assemble(self, source_code):
    #     machine_code = []
    #     log_entries = []
    #
    #     for line in source_code.splitlines():
    #         line = line.strip()
    #         if not line:  # Пропускаем пустые строки
    #             continue
    #
    #         parts = line.split('=')
    #         instruction = parts[0].strip()
    #
    #         if instruction not in self.instructions:
    #             raise ValueError(f"Unknown instruction {instruction}")
    #
    #         op_code = self.instructions[instruction]
    #
    #         if len(parts) > 1:  # Если есть операнд
    #             operand = int(parts[1].strip())
    #             packed_instruction = struct.pack('B', op_code) + struct.pack('I', operand)
    #             machine_code.append(packed_instruction)
    #             log_entries.append(f"{instruction}={operand}")
    #         else:  # Если операнда нет
    #             packed_instruction = struct.pack('B', op_code) + b'\x00\x00\x00'
    #             machine_code.append(packed_instruction)
    #             log_entries.append(f"{instruction}=No Operand")
    #
    #     return machine_code, log_entries
    def assemble(self, source_code):
        machine_code = []
        log_entries = []

        for line in source_code.splitlines():
            line = line.strip()
            if not line:  # Пропускаем пустые строки
                continue

            parts = line.split(' ')
            instruction = parts[0].strip()

            if instruction not in self.instructions:
                raise ValueError(f"Unknown instruction {instruction}")

            op_code = self.instructions[instruction]

            if len(parts) > 1:  # Если есть операнд
                operand = int(parts[1].strip())
                packed_instruction = struct.pack('B', op_code) + struct.pack('I', operand)
                machine_code.append(packed_instruction)
                log_entries.append(f"{instruction}={operand}")
            else:  # Если операнда нет
                packed_instruction = struct.pack('B', op_code) + b'\x00\x00\x00'
                machine_code.append(packed_instruction)
                log_entries.append(f"{instruction}=No Operand")

        return machine_code, log_entries

    def save_binary(self, machine_code, output_file):
        # Удаляем старый файл, если он существует
        if os.path.exists(output_file):
            os.remove(output_file)

        with open(output_file, 'wb') as f:
            for instruction in machine_code:
                f.write(instruction)

    def save_log(self, log_entries, log_file):
        with open(log_file, 'w') as f:
            for entry in log_entries:
                f.write(entry + '\n')

class Interpreter:
    def __init__(self, memory_size, start_address, end_address):
        # Инициализация памяти и диапазона
        self.memory = [0] * memory_size
        self.register = 0  # Регистратор
        self.pc = 0  # Программный счётчик
        self.start_address = start_address
        self.end_address = end_address

    def load_binary(self, binary_file):
        with open(binary_file, 'rb') as f:
            code = f.read()

        self.code = []
        i = 0
        while i < len(code):
            if len(code) - i < 1:  # Проверяем, достаточно ли данных для хотя бы одного байта
                print(
                    f"Warning: not enough data at position {i}, expected at least 1 byte but found {len(code) - i} bytes.")
                break  # Выход из цикла, так как данных недостаточно для дальнейшей обработки

            op_code = code[i]  # Опкод — это один байт
            i += 1  # Переходим к следующему байту

            if op_code in [1, 2, 3, 4, 5, 13]:  # Команды с операндами (например, LOAD, STORE, ADD, LOAD_MEMORY)
                if len(code) - i < 4:  # Если не хватает 4 байтов для операнда
                    print(f"Warning: not enough data for operand at position {i}. Skipping this command.")
                    i += 3  # Пропускаем остаток этой команды
                    continue  # Переходим к следующей команде
                operand = struct.unpack('I', code[i:i + 4])[0]  # Чтение 4 байтов как целое число
                self.code.append((op_code, operand))
                i += 4  # Переход к следующей команде

            else:  # Команда без операнда
                self.code.append((op_code,))
                i += 1  # Команда без операнда, увеличиваем индекс на 1 (только для опкода)

        return self.code


    def execute(self):
        log = []
        while self.pc < len(self.code):
            instruction = self.code[self.pc]
            op_code = instruction[0]

            # В зависимости от опкода выполняем соответствующую команду
            try:
                if op_code == 1:  # LOAD
                    address = instruction[1]
                    self.register = self.memory[address]
                    log.append(f"LOAD {address} -> {self.register}")
                elif op_code == 2:  # STORE
                    address = instruction[1]
                    self.memory[address] = self.register
                    log.append(f"STORE {address} <- {self.register}")
                elif op_code == 3:  # ADD
                    address = instruction[1]
                    self.register += self.memory[address]
                    log.append(f"ADD {address} -> {self.register}")
                elif op_code == 4:  # SUB
                    address = instruction[1]
                    self.register -= self.memory[address]
                    log.append(f"SUB {address} -> {self.register}")
                elif op_code == 5:  # JUMP
                    address = instruction[1]
                    self.pc = address
                    log.append(f"JUMP {address}")
                    continue  # Переходим к следующей итерации
                elif op_code == 6:  # HALT
                    log.append(f"HALT")
                    break
                elif op_code == 7:
                    log.append(f"LOAD_CONSTANT")
                elif op_code == 13:  # LOAD_MEMORY
                    # Имитация работы со стеком для LOAD_MEMORY
                    address = self.register  # Предполагаем, что регистр указывает на адрес
                    self.register = self.memory[address]  # Читаем значение из памяти
                    log.append(f"LOAD_MEMORY {address} -> {self.register}")
                else:
                    log.append(f"Unknown op_code {op_code}")

            except Exception as e:
                log.append(f"Error executing op_code {op_code}: {e}")
                break  # Прерываем выполнение, если произошла ошибка
            self.pc += 1  # Переходим к следующей команде
        return log

    def save_result(self, result_file):
        # Записываем значения из диапазона памяти в json
        result = {f"address_{i}": self.memory[i] for i in range(self.start_address, self.end_address + 1)}
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=4)

def view_binary_file(binary_file):
    """
    Просмотр содержимого бинарного файла в шестнадцатеричном формате.
    """
    try:
        with open(binary_file, 'rb') as f:
            data = f.read()
            print("Содержимое бинарного файла (HEX):")
            print(' '.join(f"{byte:02X}" for byte in data))
    except FileNotFoundError:
        print(f"Файл {binary_file} не найден.")
    except Exception as e:
        print(f"Ошибка: {e}")


def assemble_and_run():
    if len(sys.argv) < 4:
        print("Usage: script.py <input_file> <output_bin_file> <log_file>")
        sys.exit(1)

    input_file = sys.argv[2]
    output_bin_file = sys.argv[3]
    log_file = sys.argv[4]

    # Очистка старого бинарного файла
    if os.path.exists(output_bin_file):
        os.remove(output_bin_file)

    with open(input_file, 'r') as f:
        source_code = f.read()

    assembler = Assembler()
    machine_code, log_entries = assembler.assemble(source_code)

    assembler.save_binary(machine_code, output_bin_file)
    print(f"Binary file saved to {output_bin_file}")

    assembler.save_log(log_entries, log_file)
    print(f"Log file saved to {log_file}")



def interpret_and_log():
    if len(sys.argv) < 6:
        print("Usage: interpreter.py <binary_file> <start_address> <end_address> <log_file> <result_file>")
        sys.exit(1)

    binary_file = sys.argv[2]
    start_address = int(sys.argv[3])
    end_address = int(sys.argv[4])
    log_file = sys.argv[5]
    result_file = sys.argv[6]

    memory_size = 1024  # Примерный размер памяти
    interpreter = Interpreter(memory_size, start_address, end_address)

    try:
        interpreter.load_binary(binary_file)
    except Exception as e:
        print(f"Error loading binary file: {e}")
        sys.exit(1)

    try:
        log = interpreter.execute()
    except Exception as e:
        print(f"Error executing commands: {e}")
        sys.exit(1)

    # Запись логов в файл
    try:
        with open(log_file, 'w') as f:
            json.dump(log, f, indent=4)
    except Exception as e:
        print(f"Error saving log file: {e}")
        sys.exit(1)

    # Запись результатов
    try:
        interpreter.save_result(result_file)
    except Exception as e:
        print(f"Error saving result file: {e}")
        sys.exit(1)

    print(f"Log saved to {log_file}")
    print(f"Results saved to {result_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <mode> ...")
        print("Modes: assemble, interpret, view_binary")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "assemble":
        assemble_and_run()
    elif mode == "interpret":
        interpret_and_log()
    elif mode == "view_binary":
        if len(sys.argv) < 3:
            print("Usage: python script.py view_binary <binary_file>")
            sys.exit(1)
        binary_file = sys.argv[2]
        view_binary_file(binary_file)
    else:
        print("Invalid mode. Use 'assemble', 'interpret', or 'view_binary'")
        sys.exit(1)

if __name__ == '__main__':
    main()
    view_binary_file('output.bin')
