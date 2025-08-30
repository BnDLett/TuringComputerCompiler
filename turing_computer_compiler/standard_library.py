from enum import Enum
from turing_computer_compiler.compiler import Compiler, CompileResult

compiler = Compiler()

# Note that INSTRUCTION_LENGTH is equal to the length of the value.
INSTRUCTION_LENGTH = 32
BINARY_LENGTH = 64


class SpecialCharacters(Enum):
    COMMENT = "--"
    COLON = ":"


def register_to_flag(register: int, initial_binary: str = "0b00000000000000000000000000000000") -> str:
    # fuck you python this should be a standard feature not a fucking work around
    # Replace the character at a given position in a string
    position = (len(initial_binary) - register)
    result = initial_binary[:position] + "1" + initial_binary[(position + 1):]
    return result


def pad_instruction(instruction: str) -> str:
    return instruction.ljust(BINARY_LENGTH + 2, "0")


@compiler.rule
def comment(instruction: list[str]) -> CompileResult:
    if SpecialCharacters.COMMENT.value in instruction[0]:
        return CompileResult.IGNORE_LINE

    return CompileResult.UNRECOGNIZED_INSTRUCTION


@compiler.rule
def insert(instruction: list[str], label_position: int | None = None) -> CompileResult | str:
    if instruction[0] != "PANA": return CompileResult.UNRECOGNIZED_INSTRUCTION
    elif len(instruction) != 3: return CompileResult.COMPILE_ERROR

    value = instruction[1]
    register = instruction[2]

    # Leaves the label processing up to the post processor
    if label_position is not None:
        value = label_position
    elif not value.isdecimal():
        return " ".join(instruction)

    register_flag = register_to_flag(int(register))
    value_binary = bin(int(value)).removeprefix("0b").rjust(INSTRUCTION_LENGTH, "0")

    # Register is not a general-purpose register. It is intended for register flags.
    if register == "6":
        value_binary = register_to_flag(int(value), "000000").rjust(INSTRUCTION_LENGTH, "0")

    return register_flag + value_binary


@compiler.rule
def arithmetic(instruction: list[str]) -> CompileResult | str:
    INSTRUCTION = "0b00000000000000000100000000"

    # ADD a b reg
    if instruction[0] != "ANTE_NANPA": return CompileResult.UNRECOGNIZED_INSTRUCTION
    elif len(instruction) != 2: return CompileResult.COMPILE_ERROR

    register = instruction[1]
    final_instruction = pad_instruction(INSTRUCTION + register_to_flag(int(register), "000000"))

    return final_instruction


@compiler.rule
def labels(instruction: list[str]) -> CompileResult | str:
    if instruction[0][-1] != SpecialCharacters.COLON.value:
        return CompileResult.UNRECOGNIZED_INSTRUCTION

    return f"LABEL {instruction[0].removesuffix(":")}"


@compiler.rule
def conditional_jump(instruction: list[str]) -> CompileResult | str:
    INSTRUCTION = "0b00000000000000000100000000000000".ljust(INSTRUCTION_LENGTH + 2, "0")

    if instruction[0] != "TAWA_KEN":
        return CompileResult.UNRECOGNIZED_INSTRUCTION

    return INSTRUCTION


@compiler.rule
def end(instruction: list[str]) -> CompileResult | str:
    INSTRUCTION = pad_instruction("0b00000000000000000000000001000000")

    if instruction[0] != "PAKE":
        return CompileResult.UNRECOGNIZED_INSTRUCTION

    return INSTRUCTION


@compiler.rule
def jump(instruction: list[str]) -> CompileResult | str:
    INSTRUCTION = pad_instruction("0b00000000000000000000000010000000")

    if instruction[0] != "TAWA_ANTE":
        return CompileResult.UNRECOGNIZED_INSTRUCTION

    return INSTRUCTION


@compiler.rule
def copy(instruction: list[str]) -> CompileResult | str:
    INSTRUCTION = "0b00000000000000000000100000"

    if instruction[0] != "SAMA":
        return CompileResult.UNRECOGNIZED_INSTRUCTION
    if len(instruction) != 2:
        return CompileResult.COMPILE_ERROR

    register = instruction[1]
    register_flag = register_to_flag(int(register), "000000")

    return pad_instruction(f"{INSTRUCTION}{register_flag}")


@compiler.rule
def write(instruction: list[str]) -> CompileResult | str:
    INSTRUCTION = "0b00000000000000000000000100000000"

    if instruction[0] != "PALI_NIMI":
        return CompileResult.UNRECOGNIZED_INSTRUCTION

    return pad_instruction(INSTRUCTION)


@compiler.rule
def load(instruction: list[str]) -> CompileResult | str:
    INSTRUCTION = "0b00000000000000000000010000"

    if instruction[0] != "LANPAN":
        return CompileResult.UNRECOGNIZED_INSTRUCTION
    if len(instruction) != 2:
        return CompileResult.COMPILE_ERROR

    register = instruction[1]
    register_flag = register_to_flag(int(register), "000000")

    return pad_instruction(f"{INSTRUCTION}{register_flag}")


@compiler.rule
def lshift(instruction: list[str]) -> CompileResult | str:
    INSTRUCTION = "0b00000000000000000010000000"

    if instruction[0] != "TAWA_SOTO":
        return CompileResult.UNRECOGNIZED_INSTRUCTION
    if len(instruction) != 2:
        return CompileResult.COMPILE_ERROR

    register = instruction[1]
    register_flag = register_to_flag(int(register), "000000")

    return pad_instruction(f"{INSTRUCTION}{register_flag}")


@compiler.rule
def rshift(instruction: list[str]) -> CompileResult | str:
    INSTRUCTION = "0b00000000000000000011000000"

    if instruction[0] != "TAWA_TEJE":
        return CompileResult.UNRECOGNIZED_INSTRUCTION
    if len(instruction) != 2:
        return CompileResult.COMPILE_ERROR

    register = instruction[1]
    register_flag = register_to_flag(int(register), "000000")

    return pad_instruction(f"{INSTRUCTION}{register_flag}")


def get_label_positions(instructions: list[str]) -> dict[str, int]:
    label_positions: dict[str, int] = {}

    for index, instruction in enumerate(instructions, 0):
        if not instruction.startswith("LABEL"): continue

        label_name = instruction.removeprefix("LABEL ")
        label_positions[label_name] = index

    return label_positions


# @compiler.post_compile_rule
# def squash_labels(instructions: list[str]) -> list[str]:
#     final_result: list[str] = []
#
#     for index, instruction in enumerate(instructions):
#         if not instruction.startswith("LABEL"):
#             final_result.append(instruction)
#             continue
#
#         pass
#
#     return instructions


@compiler.post_compile_rule
def convert_label_references(instructions: list[str]) -> list[str]:
    label_positions = get_label_positions(instructions)
    final_result: list[str] = []

    for instruction in instructions:
        if instruction.startswith("LABEL"):
            final_result.append("0x0")
            continue
        elif not instruction.startswith("PANA"):
            final_result.append(instruction)
            continue

        # INSERT foo 5
        parameters = instruction.split(" ")
        label = parameters[1]
        label_position = label_positions[label]

        processed_instruction = insert(parameters, label_position)
        final_result.append(processed_instruction)

    return final_result


@compiler.pre_compile_rule
def registers(code: list[str]) -> list[str]:
    final_result: list[str] = []

    for line in code:
        if "r" not in line.strip():
            final_result.append(line)
            continue

        processed_line = line.replace("r", "")
        final_result.append(processed_line)

    return final_result


if __name__ == "__main__":
    example_instructions = [
        "PANA 0 r4",
        "PANA 1 r2",
        "PANA 4 r6",

        "open:",
        "    SAMA r1",
        "    ANTE_NAMPA r4",
        "    PANA open r1",
        "    TAWA_ANTE"
    ]
    result = compiler.full_compile(example_instructions)
    print(result)
    print()
    print("\n".join(result))
