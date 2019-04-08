from functools import reduce
from copy import deepcopy
from typing import *

from tools350.assembler.instruction.InstructionType import InstructionType, BASE_JSON_PATH, BASE_JSON_LOCAL
from tools350.assembler.instruction.Instruction import Instruction
from itertools import count
import json
import re
from os.path import join
from numpy import binary_repr


class Parser:

    def __init__(self, extra_registers: Iterable[dict] = (), extra_instr: Iterable[dict] = (),
                 extra_types: Iterable[dict] = ()):
        self._extra_registers = extra_registers
        self._extra_instr = extra_instr
        try:
            self._instruction_bank: dict = Parser._load_jsons(join(BASE_JSON_PATH, 'base_instr.json'),
                                                              self._extra_instr)
            # Overload the jump replace logic to also handle named registers
            self._jump_targets: dict = Parser._load_jsons(join(BASE_JSON_PATH, 'value-mappings.json'),
                                                          self._extra_registers)
            self._instruction_types: InstructionType = InstructionType(
                Parser._load_jsons(join(BASE_JSON_PATH, 'instruction-types.json'), extra_types))
        except FileNotFoundError:
            self._instruction_bank: dict = Parser._load_jsons(join(BASE_JSON_LOCAL, 'base_instr.json'),
                                                              self._extra_instr)
            # Overload the jump replace logic to also handle named registers
            self._jump_targets: dict = Parser._load_jsons(join(BASE_JSON_LOCAL, 'value-mappings.json'),
                                                          self._extra_registers)
            self._instruction_types: InstructionType = InstructionType(
                Parser._load_jsons(join(BASE_JSON_LOCAL, 'instruction-types.json'), extra_types))

    @classmethod
    def _load_jsons(cls, master_location: str, extra_files: Iterable[dict] = ()) -> dict:
        """Load json resource files into the program. The master JSON file takes priority over all others for replacement
            of elements, but after that the elements are prioritized their order in the tuple, ie element 1 will
            overwrite all common entries of element 2.
            :param master_location: Location of the base elements, like the provided ISA or instruction types. No
            elements from these can be overwritten, and they should be deployed by course staff only.
            :type master_location: str
            :param extra_files: Secondary locations to draw from. These will be uploaded by students as supplements to add
            instruction types, instructions, or named registers.
            :type extra_files: tuple(str)
            :returns: a merged dictionary from all the json files specified.
            :rtype: dict
            :raises AssertionError: master_location must be a valid file to read.
            :raises JSONDecodeError: master_location must be a valid JSON file.
            """
        with open(master_location, 'r') as file:
            ret: dict = json.load(file)
        for possible_jsn in extra_files:
            ret = Parser._merge_dicts(ret, possible_jsn)
        return ret

    @classmethod
    def _merge_dicts(cls, dict1: dict, dict2: dict) -> dict:
        """
        Do a deep merge across the two dictionary arguments. If the two share a key, and that key is not a merge-able
        type like list or dict, then the first dictionary (dict1) is taken.
        :param dict1: First dict to merge. Will override all non-merge-able values
        :param dict2: Second dict to merge
        :return: Merged dict. Values are deep copies of the values in the original dicts
        """
        ret = {}
        overlap = dict1.keys() & dict2.keys()
        for k in overlap:
            if type(dict1[k]) is dict:  # Recursively merge
                ret[k] = Parser._merge_dicts(dict1[k], dict2[k])
            elif type(dict1[k]) is list:  # Concat the list
                ret[k] = dict1[k] + dict2[k]
            else:  # Take the master arg
                ret[k] = dict1[k]
        for k in dict1.keys() - overlap:
            ret[k] = deepcopy(dict1[k])
        for k in dict2.keys() - overlap:
            ret[k] = deepcopy(dict2[k])
        return ret

    def parse_line(self, line: str, line_num: int) -> Instruction:
        """
        Convert a line into an Instruction with all arguments properly populated.
        :param line: Line to convert to an instruction
        :type line: str
        :param line_num: Current line number to use for branches
        :type line_num: int
        :return: Compiled instruction, if line contains an instruction, else None
        :rtype: Instruction or None
        :raises AssertionError:
        """
        line = line.split('#')[0].strip()  # Remove comments
        line = reduce(lambda a, kv: re.sub(*kv, a), Parser._REPLACEMENTS,
                      line)  # Make all replacements in _replacements
        args = line.split()
        instruction = self._build_base(args.pop(0))
        self._add_line_args(instruction, args, line_num)
        return instruction

    def _add_line_args(self, instruction: Instruction, line_args: List[str], line_num: int):
        """
        Take arguments specified in the line and add them to the base instruction.
        :param instruction: Instruction object created for this line
        :param line_args: Remaining parts of the line, will be read in order and applied to their matching fields
        :raises AssertionError: Not enough or too many values specified for this instruction
        """
        for field in instruction.get_syntax():
            assert line_args, "Not enough fields provided for this instruction"
            length = instruction.get_field_lengths()[field]
            value = line_args.pop(0)
            if not re.match(Parser._NUMERIC_PATTERN, value):
                value = self._replace_name(value, line_num, field, instruction.get_name())
            bin_value = Parser._to_binary(int(value), length, field == Parser._IMMED)
            instruction.add_component(field, bin_value)
        assert not line_args, "Not all fields specified in line were used"

    def _replace_name(self, name: str, line_num: int, field: str, inst_name: str) -> str:
        replacement = self._jump_targets[name]
        if self._instruction_types.is_branch(inst_name) and field == Parser._IMMED:
            replacement -= (line_num + 1)  # Since target = PC + N + 1   =>   N = target - N - 1
        return replacement

    def _build_base(self, mips_instr: str) -> Instruction:
        """
        Create a basic instruction for this line.
        :param mips_instr: Name of the instruction.
        :return: Instruction object with opcode and ALUop fields set as required.
        :raises KeyError: The instruction provided is invalid.
        """
        type_opcode = self._instruction_bank[mips_instr]
        type_ = type_opcode['type']
        ret = Instruction(type_, mips_instr, self._instruction_bank[mips_instr]['syntax'],
                          types=self._instruction_types)
        if type_ == "R":
            ret.add_component("aluop", type_opcode["aluop"])  # Opcode is always '00000' for R, no need to specify here
        else:
            ret.add_component("opcode", type_opcode['opcode'])
        return ret

    @classmethod
    def _to_binary(cls, value: int, bin_length: int, twos_complement: bool = False) -> str:
        """
        Util func to create a binary string of set length from a decimal value.
        :param value: decimal value to encode to decimal.
        :param bin_length: Number of digits to use to encode this value.
        :param twos_complement: Defaults to false, but can be set true to encode in two's complement
        :return: Binary string.
        """
        if twos_complement:
            assert -(2 ** (bin_length - 1)) <= value <= (2 ** (bin_length - 1)) - 1, \
                "{} is out of range for {}-bit two's complement".format(value, bin_length)
            return binary_repr(value, bin_length)
        else:
            assert value > -1, "Value must be at least 0 for representation in non-two's complement"
            assert value < 2 ** bin_length, "{} is out of range for {}-bit representation".format(value, bin_length)
            # Will always fit into length+1 as 2's comp, remove first digit to go back to unsigned
            return binary_repr(value, bin_length + 1)[1:]

    def preprocess_assembly(self, text_file: List[str]) -> List[str]:
        """
        Run over the assembly to find blank lines, comment lines, and jump target only lines, and remove them from the
        list of assembly. Log all the jump targets into a thread local dict for later use.
        :param text_file: List of all the lines in the text file.
        :return: Filtered list of only lines containing instructions.
        """
        whitespace_or_comment_only: Pattern = re.compile('^\s*$|\s*#')
        filtered_line_number: Counter = count(0)
        return [self._extract(line, next(filtered_line_number))  # If there's a jump target, parse it out;
                for line in text_file  # if not, just add the line
                if not re.match(whitespace_or_comment_only, line)  # is not empty or just a comment
                and not self._is_only_target(line, Parser._counter_to_int(filtered_line_number))]  # Has something other than a jump target

    def _is_only_target(self, line: str, line_number: int) -> bool:
        """
        Check if the line contains only a target. If so, it'll be removed from the assembly and logged in the jump dict
        :param line: Line to check
        :param line_number: Line number of the target. Used if the the target needs to be replaced
        :return: bool for if the line is just an instruction
        """
        without_comments = line.split('#')[0]
        if re.search(Parser._TARGET_PATTERN, without_comments):
            sections = [x.strip() for x in re.split(Parser._TARGET_PATTERN, without_comments) if x]
            if len(sections) > 2:
                raise SyntaxError("Too many sections to labeled line: expected two or fewer, found {}"
                                  .format(len(sections)))
            elif len(sections) < 2 or sections[1].startswith('#'):
                self._jump_targets[sections[0]] = line_number
                return True
        return False

    def _extract(self, line: str, line_number: int) -> str:
        """
        Extract a jump target from the line, if it exists, and log it.
        :param line: Line to potentially extract a jump from.
        :param line_number: Line number of the target.
        :return: String to insert into the list
        """
        without_comments = line.split('#')[0]
        if re.search(Parser._TARGET_PATTERN, without_comments):
            split = [x for x in re.split(Parser._TARGET_PATTERN, line) if x]
            self._jump_targets[split[0]] = line_number
            return split[1]
        else:
            return line

    @classmethod
    def _counter_to_int(cls, counter: Counter) -> int:
        """
        Util function to convert a counter to an int
        :param counter: Counter to convert to an int
        :return: int value of the counter
        """
        return int(str(counter)[6:-1])

    def clear(self):
        """
        Reset the parser to prepare it for the next file, dumping all jump references
        :return: None
        """
        self._jump_targets.clear()
        try:
            self._jump_targets: dict = Parser._load_jsons(join(BASE_JSON_PATH, 'value-mappings.json'),
                                                          self._extra_registers)
        except FileNotFoundError:
            self._jump_targets: dict = Parser._load_jsons(join(BASE_JSON_LOCAL, 'value-mappings.json'),
                                                          self._extra_registers)

    _NUMERIC_PATTERN = re.compile('^[\+\-]?\d+$')
    _TARGET_PATTERN = re.compile(':\s*')
    _PC_LENGTH = 12
    _REPLACEMENTS = [(re.compile(','), ''), (re.compile(';'), ''), (re.compile('\$r(\d+)'), r'\1'),
                     (re.compile('\$(\d+)'), r'\1'), (re.compile('\('), ' '), (re.compile('\)'), ' ')]
    _IMMED = "immed"
