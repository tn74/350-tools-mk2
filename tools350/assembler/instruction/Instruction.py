from typing import List, Dict

from tools350.assembler.instruction.InstructionType import InstructionType


class Instruction:

    _R_OPCODE = '00000'

    def __init__(self, inst_type: str, name: str, syntax: List[str], *, types: InstructionType=None, fmt: dict=None):
        self._instruction_type: str = inst_type
        self._binary_components = {}
        self._load_type_variables(types, fmt)
        self._syntax = syntax
        self.name = name

    def get_name(self):
        return self.name

    def _load_type_variables(self, types: InstructionType, fmt: dict):
        if types is None and fmt is None:
            print("General kenobi!")
        instr_structure: dict = types.get_by_type(self.get_type()) if types else fmt
        self._fields = instr_structure.keys()
        self._lengths: dict = instr_structure
        self._init_default()


    def _init_default(self):
        """Assign all fields to 0, essentially makes a nop.
            """
        for field in self._fields:
            self._binary_components[field] = '0' * self._lengths[field]

    def replace_with_error(self, msg: str) -> "Instruction":
        ret = Instruction("E", 'err', ['err'], fmt=InstructionType.ERROR)
        ret.add_component("err", msg)
        return ret

    def get_type(self) -> str:
        """Return the type of instruction.
            :rtype: str
            :returns: Instr type
            """
        return self._instruction_type

    def get_field_lengths(self) -> Dict[str, int]:
        """
            :rtype: Dict[str, int]
            :returns: Length of each field, paired by index to the instance variable _fields
            """
        return self._lengths

    def get_opcode(self) -> str:
        """
            :rtype: str
            :returns: opcode
            """
        return self._binary_components['opcode']

    def add_component(self, field: str, value: str):
        """Add a value to the instruction. If the variable doesn't exist as a field in the instruction, throw an exception
            as this was an invalid assignment.
            :param field: name of the field to update
            :type field: str
            :param value: new value to assign to the field
            :type value: str
            :raises AssertionError: param field is not found in this instruction type
            """
        assert field in self._fields, "Field {} not in instruction type {}".format(field, self._instruction_type)
        self._binary_components[field] = value

    def get_syntax(self) -> List[str]:
        """
            :returns: Syntax used for this instruction when writing mips, neglecting the instruction name. For example, add
            would return ["rd", "rs", "rt"]
            :rtype: List[str]
            """
        return self._syntax

    def __str__(self) -> str:
        return ''.join([self._binary_components[section] for section in self._fields])

