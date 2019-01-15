from functools import reduce
from io import IOBase
from typing import *
from assembler.instruction.Instruction import Instruction
from itertools import count
import json
import re
from os.path import exists, isfile


class Parser:

    def __init__(self, extra_registers: Iterable[IOBase]=(), extra_instr: Iterable[IOBase]=()):
        self._extra_registers = extra_registers
        self._extra_instr = extra_instr
        self._instruction_bank: dict = Parser._load_jsons('./jsn_resources/jsn_resources.jsn', self._extra_instr)
        # Overload the jump replace logic to also handle named registers
        self._jump_targets: dict = Parser._load_jsons('./jsn_resources/value-mappings.json', self._extra_registers)

    @classmethod
    def _load_jsons(cls, master_location: str, extra_files: Iterable[IOBase]=()) -> dict:
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
        assert exists(master_location) and isfile(master_location), "Cannot find base instructions"
        ret = json.load(master_location)
        for possible_jsn in extra_files:
            try:
                extra_values = json.load(possible_jsn)
                ret = {**extra_values, **ret}  # ret goes second so that its values are preserved
            except json.JSONDecodeError as json_error:
                print(json_error)
        return ret

    def parse_line(self, line: str) -> Optional[Instruction]:
        """
        Convert a line into an Instruction with all arguments properly populated.
        :param line: Line to convert to an instruction
        :type line: str
        :return: Compiled instruction, if line contains an instruction, else None
        :rtype: Instruction or None
        :raises AssertionError:
        """
        line = line.split('#')[0].strip()  # Remove comments
        reduce(lambda a, kv: a.replace(*kv), line, Parser._replacements)  # Make all replacements in _replacements
        args = line.split()
        if len(args) < 1 or not args[0]: return None  # No instruction on this line
        instruction = self._build_base(args.pop(0))
        self._add_line_args(instruction, args)
        return instruction

    def _add_line_args(self, instruction: Instruction, line_args: List[str]):
        """
        Take arguments specified in the line and add them to the base instruction.
        :param instruction: Instruction object created for this line
        :param line_args: Remaining parts of the line, will be read in order and applied to their matching fields
        :raises AssertionError: Not enough or too many values specified for this instruction
        """
        for field, length in zip(instruction.get_syntax(), instruction.get_field_lengths()):
            assert line_args, "Not enough fields provided for this instruction"
            value = line_args.pop(0)
            if not value.isnumeric():
                value = self._jump_targets[value]
            bin_value = Parser._to_binary(int(value), length)
            instruction.add_component(field, bin_value)
        assert not line_args, "Not all fields specified in line were used"

    def _build_base(self, mips_instr: str) -> Instruction:
        """
        Create a basic instruction for this line.
        :param mips_instr: Name of the instruction.
        :return: Instruction object with opcode and ALUop fields set as required.
        :raises KeyError: The instruction provided is invalid.
        """
        type_opcode = self._instruction_bank[mips_instr]
        type_ = type_opcode['type']
        ret = Instruction(type_)
        if type_ == "R":
            ret.add_component("aluop", type_opcode["aluop"])  # Opcode is always '00000' for R, no need to specify here
        else:
            ret.add_component("opcode", type_opcode['opcode'])
        return ret

    @classmethod
    def _to_binary(cls, value: int, bin_length: int, twos_complement: bool=False) -> str:
        """
        Util func to create a binary string of set length from a decimal value.
        :param value: decimal value to encode to decimal.
        :param bin_length: Number of digits to use to encode this value.
        :return: Binary string.
        """
        if twos_complement:
            assert -(2**(bin_length-1)) < value < (2**(bin_length-1))-1, \
                "{} is out of range for {}-bit two's complement".format(value, bin_length)
            return bin(value & int('1'*bin_length))[2:]  # mask for length and remove the leading prefix of 0b
        else:
            assert value > -1, "Value must be at least 0 for representation in non-two's complement"
            assert value < 2**bin_length, "{} is out of range for {}-bit representation".format(value, bin_length)
            return '{0:0%db}'.format(bin_length).format(value)

    def preprocess_assembly(self, text_file: List[str]) -> List[str]:
        """
        Run over the assembly to find blank lines, comment lines, and jump target only lines, and remove them from the
        list of assembly. Log all the jump targets into a thread local dict for later use.
        :param text_file: List of all the lines in the text file.
        :return: Filtered list of only lines containing instructions.
        """
        comment_only: Pattern = re.compile('\s*#')
        filtered_line_number: Counter = count(1)
        return [Parser._extract(line, next(filtered_line_number))  # If there's a jump target, parse it out. If not, just add the line
                for line in text_file
                if line  # is not empty
                and not re.match(comment_only, line)  # Is not only comments
                and not self._is_only_target(line, Parser._counter_to_int(filtered_line_number))]  # Has something other than a jump target

    def _is_only_target(self, line: str, line_number: int) -> bool:
        """
        Check if the line contains only a target. If so, it'll be removed from the assembly and logged in the jump dict
        :param line: Line to check
        :param line_number: Line number of the target. Used if the the target needs to be replaced
        :return: bool for if the line is just an instruction
        """
        if re.search(Parser._TARGET_PATTERN, line):
            sections = [x for x in re.split(Parser._TARGET_PATTERN, line) if x]
            if len(sections) > 2:
                raise SyntaxError("Too many sections to labelled line: expected two or fewer, found {}"
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
        line = line.strip()
        if re.search(Parser._TARGET_PATTERN, line):
            split = [x for x in re.split(Parser._TARGET_PATTERN, line) if x]
            self._jump_targets[split[0]] = Parser._to_binary(line_number, Parser._PC_LENGTH)
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
        self._jump_targets: dict = Parser._load_jsons('./jsn_resources/value-mappings.json', self._extra_registers)

    _TARGET_PATTERN: Pattern = re.compile(':\s*')
    _PC_LENGTH = 12
    _replacements = (',', ''), (';', ''), ('$r', ''), ('(', ' '), (')', ' ')

