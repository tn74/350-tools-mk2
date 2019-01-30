import json

BASE_JSON_PATH = './assembler/jsn_resources/{}'


def _load_json():
    with open(BASE_JSON_PATH.format('instruction-types.json'), 'r') as file:
        return json.load(file)


class InstructionType:

    @classmethod
    def get_by_type(cls, type_: str) -> dict:
        return InstructionType._instruction_types["types"][type_]

    @classmethod
    def is_branch(cls, instr: str) -> bool:
        return instr in InstructionType._instruction_types["branches"]

    _instruction_types = _load_json()

