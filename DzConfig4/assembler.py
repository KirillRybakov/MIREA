import sys
import json


class Assembler:
    def __init__(self):
        self.instructions = {
            "LOAD_CONSTANT": 27,
            "LOAD_MEMORY": 13,
            "STORE_TO_MEMORY": 14,
            ">": 21
        }

    def assemble(self, source_code):
        machine_code = []
        log = []

        for line_no, line in enumerate(source_code.splitlines(), 1):
            line = line.strip()
            if not line or line.startswith(";"):  # Пропуск пустых строк и комментариев
                continue

            parts = line.split()
            command = parts[0]

            if command not in self.instructions:
                raise ValueError(f"Unknown instruction '{command}' on line {line_no}")

            opcode = self.instructions[command]
            if command == "LOAD_CONSTANT":
                _, reg, value = parts
                reg = int(reg)
                value = int(value)
                encoded = (opcode << 24) | (reg << 19) | value
                machine_code.append(encoded)
                log.append({"line": line_no, "instruction": line, "binary": f"{encoded:08X}"})

            elif command == "STORE_TO_MEMORY":
                if len(parts) != 3:
                    raise ValueError(f"Invalid number of arguments for command: {line}")
                _, reg, address = parts
                reg = int(reg)
                address = int(address)

                # Проверка допустимых значений
                if not (0 <= reg < 32):
                    raise ValueError(f"Invalid register number: {reg}")
                if not (0 <= address < (1 << 22)):
                    raise ValueError(f"Invalid address: {address}")

                # Кодирование команды
                encoded = (opcode << 24) | (reg << 19) | address
                machine_code.append(encoded)
                log.append({"line": line_no, "instruction": line, "binary": f"{encoded:08X}"})

            elif command == "LOAD_MEMORY":
                _, reg = parts
                reg = int(reg)
                encoded = (opcode << 24) | (reg << 19)
                machine_code.append(encoded)
                log.append({"line": line_no, "instruction": line, "binary": f"{encoded:08X}"})

            elif command == ">":
                encoded = (opcode << 24)
                machine_code.append(encoded)
                log.append({"line": line_no, "instruction": line, "binary": f"{encoded:08X}"})

            else:
                raise ValueError(f"Unhandled instruction '{command}' on line {line_no}")

        return machine_code, log


class Interpretator:
    def __init__(self):
        self.stack = []  # Стек
        self.memory = [0] * 256  # Память (256 ячеек)
        self.log = []  # Лог выполнения команд

    def execute(self, machine_code):
        for index, instruction in enumerate(machine_code):
            opcode = (instruction >> 24) & 0xFF
            if opcode == 27:  # LOAD_CONSTANT
                reg = (instruction >> 19) & 0x1F
                value = instruction & 0x7FFFF
                self.stack.append(value)
                self.log.append(f"[{index}] LOAD_CONSTANT: Pushed {value} onto stack.")

            elif opcode == 13:  # LOAD_MEMORY
                if not self.stack:
                    raise RuntimeError("LOAD_MEMORY failed: Stack is empty.")
                address = self.stack.pop()
                if address < 0 or address >= len(self.memory):
                    raise RuntimeError(f"LOAD_MEMORY failed: Invalid address {address}.")
                value = self.memory[address]
                self.stack.append(value)
                self.log.append(f"[{index}] LOAD_MEMORY: Loaded value {value} from memory[{address}].")

            elif opcode == 14:  # STORE_TO_MEMORY
                if len(self.stack) < 2:
                    raise RuntimeError("STORE_TO_MEMORY failed: Not enough values on stack.")
                value = self.stack.pop()
                address = self.stack.pop()
                if address < 0 or address >= len(self.memory):
                    raise RuntimeError(f"STORE_TO_MEMORY failed: Invalid address {address}.")
                self.memory[address] = value
                self.log.append(f"[{index}] STORE_TO_MEMORY: Stored value {value} to memory[{address}].")

            elif opcode == 21:  # >
                if len(self.stack) < 2:
                    raise RuntimeError("> failed: Not enough values on stack.")
                b = self.stack.pop()
                a = self.stack.pop()
                result = (a > b)
                self.stack.append(result)
                self.log.append(f"[{index}] >: Compared {a} > {b}, pushed {result}.")

            else:
                raise RuntimeError(f"Unknown opcode {opcode} at index {index}.")

    def get_memory_dump(self):
        """Возвращает содержимое памяти в виде словаря."""
        return {f"address_{i}": value for i, value in enumerate(self.memory)}
        # return {f"address_{i}": value for i, value in enumerate(self.memory) if value != 0}


def main():
    if len(sys.argv) != 5:
        print("Usage: python script.py <input_file> <output_bin> <log_file> <result_json>")
        sys.exit(1)

    input_file, binary_file, log_file, result_file = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

    with open(input_file, "r") as f:
        source_code = f.read()

    assembler = Assembler()
    machine_code, log = assembler.assemble(source_code)

    # Запись бинарного файла
    with open(binary_file, "wb") as f:
        for instruction in machine_code:
            f.write(instruction.to_bytes(4, byteorder='big'))
    print(f"Binary file saved to {binary_file}")

    # Запись файла лога
    with open(log_file, "w") as f:
        json.dump(log, f, indent=4)
    print(f"Log file saved to {log_file}")

    # Выполнение машинного кода
    vm = Interpretator()
    try:
        vm.execute(machine_code)
        # Сохранение памяти в result.json
        memory_dump = vm.get_memory_dump()
        with open(result_file, "w") as f:
            json.dump(memory_dump, f, indent=4)
        print(f"Memory dump saved to {result_file}")

    except RuntimeError as e:
        print(f"Runtime error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
