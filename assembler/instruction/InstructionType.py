import json


class InstructionType:

    _instruction_types = json.load('../')

    @classmethod
    def get_by_type(cls, type_: str) -> dict:
        return InstructionType._instruction_types[type_]
