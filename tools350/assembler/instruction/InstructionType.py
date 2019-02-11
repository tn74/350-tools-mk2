import json
from os import path

BASE_JSON_PATH = '/home/mdd36/tools350/tools350/assembler/base_jsn'
BASE_JSON_LOCAL = '/Users/matthew/Documents/SchoolWork/TA/ECE350/2019s/350_tools_mk2/tools350/assembler/base_jsn'


def _load_json():
    try:
        with open(path.join(BASE_JSON_PATH, 'instruction-types.json'), 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        with open(path.join(BASE_JSON_LOCAL, 'instruction-types.json'), 'r') as file:
            return json.load(file)


class InstructionType:

    @classmethod
    def get_by_type(cls, type_: str) -> dict:
        return InstructionType._instruction_types["types"][type_]

    @classmethod
    def is_branch(cls, instr: str) -> bool:
        return instr in InstructionType._instruction_types["branches"]

    _instruction_types = _load_json()

