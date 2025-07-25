from collections.abc import Callable
from enum import Enum

# Jump to the top of the instruction stack.
JUMP_TO_TOP = "0b00000000000000000000000001000000".ljust(66, "0")


def binary_to_string(binary: int) -> str:
    return "0b" + bin(binary).removeprefix("0b").rjust(64, "0")


def binaries_to_string(binaries: list[int]) -> list[str]:
    final_result: list[str] = list()

    for binary in binaries:
        final_result.append(binary_to_string(binary))

    return final_result


class CompileResult(Enum):
    IGNORE_LINE = 1
    UNRECOGNIZED_INSTRUCTION = 2
    COMPILE_ERROR = 3


class Compiler:
    pre_compile_callbacks: list[Callable]
    callbacks: list[Callable]
    post_compile_callbacks: list[Callable]

    def __init__(self):
        self.pre_compile_callbacks = []
        self.callbacks = []
        self.post_compile_callbacks = []

    def pre_compile(self, code: list[str]) -> list[str]:
        for callback in self.pre_compile_callbacks:
            code = callback(code)

        return code

    def compile_line(self, line: str) -> str | None:
        """
        Compiles an individual line of code into its binary representation.
        :param line: The line to be compiled.
        :return: A string representing the binary instruction.
        """
        line_normalized = line.strip()
        line_split = line_normalized.split(" ")

        # There's nothing to process.
        if len(line_split) == 0:
            return None

        for callback in self.callbacks:
            result = callback(line_split)
            if result not in CompileResult: return result
            elif result == CompileResult.IGNORE_LINE: return None

        return None

    def compile_list(self, code: list[str]) -> list[str]:
        """
        Compiles a list of text instructions into binary strings.
        :param code: The code to be compiled.
        :return: Strings representing the binary instructions. These are not fixed to a length.
        """
        result: list[str] = []

        for line in code:
            compile_result = self.compile_line(line)

            if compile_result is None:
                continue

            if isinstance(compile_result, str):
                result.append(compile_result)
            # elif isinstance(compile_result, list):
            #     result += compile_result

        result.append(JUMP_TO_TOP)
        return result

    def compile_str(self, code: str) -> list[str]:
        """
        Compiles a string of text instructions into binary strings.
        :param code: The code to be compiled.
        :return: Strings representing the binary instructions. These are not fixed to a length.
        """
        code_list = code.split("\n")
        return self.compile_list(code_list)

    def post_compile(self, machine_code: list[str]) -> list[str]:
        """
        Processes the final machine code after compilation.
        :param machine_code:
        :return:
        """
        for callback in self.post_compile_callbacks:
            machine_code = callback(machine_code)

        return machine_code

    def compile(self, code: str | list) -> list[str]:
        """
        Compiles either a list of text instructions or a string of text instructions into binary instructions.
        :param code: The code to be compiled.
        :return: Strings representing the final representations of the binary instructions.
        """

        if isinstance(code, str):
            return self.compile_str(code)

        return self.compile_list(code)

    def full_compile(self, code: str | list) -> list[str]:
        pre_compile = self.pre_compile(code)
        compile_result = self.compile(pre_compile)
        return self.post_compile(compile_result)

    def rule(self, callback: Callable) -> Callable:
        """
        Adds a rule to the compiler, which will be at the top of the instruction stack. The callback should accept
        a list of strings as the only parameter. Once it is done processing the instruction, it should either return
        a CompileResult if it does not recognize the instruction *OR* the integer representation of the instruction or
        a list of integer representations.

        All instructions are checked to have a length of at least one. If you only need a length of one, then you don't
        need to worry about checking the length of the line itself.

        Note that the callback will be called for **every** line.
        :param callback: The callback to be called for every instruction.
        :return:
        """
        self.callbacks.append(callback)
        return callback

    def instruction(self, callback: Callable, instruction: str) -> Callable:
        def new_func(line: list[str]):
            if line[0] != instruction: return CompileResult.UNRECOGNIZED_INSTRUCTION
            return callback(instruction)

        return self.rule(new_func)

    def post_compile_rule(self, callback: Callable) -> Callable:
        """
        Adds a rule for post compilation. The callback will be given the list of machine instructions (`list[str]`) as
        a parameter, and it is expected to return a `list[str]`.
        :param callback: The callback to be called.
        :return:
        """
        self.post_compile_callbacks.append(callback)
        return callback

    def pre_compile_rule(self, callback: Callable) -> Callable:
        self.pre_compile_callbacks.append(callback)
        return callback
