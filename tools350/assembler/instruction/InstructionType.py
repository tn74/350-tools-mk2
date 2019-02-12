BASE_JSON_PATH = '/home/mdd36/tools350/tools350/assembler/base_jsn'
BASE_JSON_LOCAL = '/Users/matthew/Documents/SchoolWork/TA/ECE350/2019s/350_tools_mk2/tools350/assembler/base_jsn'


class InstructionType:

    def __init__(self, types: dict):
        self._instruction_types: dict = types

    def get_by_type(self, type_: str) -> dict:
        return self._instruction_types["types"][type_]

    def is_branch(self, instr: str) -> bool:
        return instr in self._instruction_types["branches"]

    NOP = {"opcode": 5, "rd": 5, "rs": 5, "rt": 5, "shamt": 5, "aluop": 5, "zeroes": 2}
    ERROR = {"err": 32}

