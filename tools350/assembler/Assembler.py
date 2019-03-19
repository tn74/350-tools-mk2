import json
from io import BytesIO, StringIO
from typing import List

from tools350.assembler.instruction.InstructionType import InstructionType
from tools350.assembler.instruction.Instruction import Instruction
from tools350.assembler.parsing.Parser import Parser
from ..util import util


class Assembler:

    FIELDS = ['inst', 'inst-types', 'named-regs']

    @classmethod
    def assemble_all(cls, files: List[str], names: List[str], additional_declarations: dict, is_pipelined=True) -> BytesIO:
        """
        Interface of Assembler with other types. Converts MIPS -> Zip[MIF]
        :param files: MIPS assembly files
        :param names: Names of the MIPS file before hashing so the files in the zip have the same name as their
         matching MIPS
        :param additional_declarations:
        :param is_pipelined:
        :return:
        """
        parser_ = Parser(Assembler.unpack(additional_declarations, 'named-regs'),
                         Assembler.unpack(additional_declarations, 'inst'),
                         Assembler.unpack(additional_declarations, 'inst-types'))
        tmp = [cls.assemble(f, parser_, is_pipelined) for f in files]
        return util.zip_(names, tmp)

    @classmethod
    def unpack(cls, dict_: dict, key: str) -> List[dict]:
        try:
            with open(dict_[key], 'r') as f:
                return [json.load(f)]
        except KeyError as e:
            return []

    @classmethod
    def assemble(cls, file: str, parser_: Parser, is_pipelined: bool) -> StringIO:
        with open(file, 'r') as f:
            parser_.clear()
            text = parser_.preprocess_assembly(f.readlines())
            ret = StringIO()
            ret.write(Assembler._HEADER)
            ret.writelines([Assembler._parse_and_format_line(parser_, line, i) for i, line in enumerate(text)])
            ret.write(Assembler._FOOTER.format(len(text), str(Assembler._NOP)))
            return ret

    @classmethod
    def _parse_and_format_line(cls, parser_: Parser, mips: str, number: int) -> str:
        try:
            instr = parser_.parse_line(mips, number)
        except (AssertionError, SyntaxError) as e:
            instr = Assembler._NOP.replace_with_error(str(e))
        return Assembler._MIF_LINE.format(number, str(instr), mips)

    _HEADER = """DEPTH = 4096;\nWIDTH = 32;\nADDRESS_RADIX = DEC;\nDATA_RADIX = BIN;\nCONTENT\nBEGIN\n"""
    _MIF_LINE = """{:04d} : {:32s}; -- {}\n"""
    _FOOTER = """[{:04d}..4095] : {:32s};\nEND;\n"""
    _NOP = Instruction("R", "nop", [], fmt=InstructionType.NOP)
