from io import StringIO, BytesIO, IOBase
from typing import List, TextIO
from os import path
from tools350.assembler.instruction.Instruction import Instruction
from tools350.assembler.parsing.Parser import Parser
from zipfile import ZipFile


class Assembler:

    FIELDS = ['inst', 'inst-types', 'named-regs']

    @classmethod
    def assemble_all(cls, files: List[str], names: List[str], additional_declarations: dict, is_pipelined=True) -> BytesIO:
        parser_ = Parser(Assembler.unpack(additional_declarations, 'registers'),
                         Assembler.unpack(additional_declarations, 'instructions'))
        tmp = [cls.assemble(f, parser_, is_pipelined) for f in files]
        return Assembler._zip(names, tmp)

    @classmethod
    def unpack(cls, dict_: dict, key: str) -> List:
        try:
            return [dict_[key]]
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
            instr = Instruction("R", "err", []).replace_with_error(str(e))
        # print(mips, '\n', str(instr))
        # print(Assembler.MIF_LINE.format(number, str(instr), mips))
        return Assembler._MIF_LINE.format(number, str(instr), mips)

    @classmethod
    def _zip(cls, file_names: List[str], assembled_files: List[StringIO]) -> BytesIO:
        zipped = BytesIO()
        with ZipFile(zipped, 'w') as zip_:
            for filename, file in zip(file_names, assembled_files):
                filename = Assembler.fix_filename(filename)
                zip_.writestr(filename, file.getvalue())
                file.close()
            for file in zip_.filelist:
                file.create_system = 0
        return zipped

    @classmethod
    def fix_filename(cls, name: str) -> str:
        return '{}.mif'.format(path.basename(name).split('.')[0])

    _HEADER = """DEPTH = 4096;\nWIDTH = 32;\nADDRESS_RADIX = DEC;\nDATA_RADIX = BIN;\nCONTENT\nBEGIN\n"""
    _MIF_LINE = """{:04d} : {:32s}; -- {}\n"""
    _FOOTER = """[{:04d}..4095] : {:32s};\nEND;\n"""
    _NOP = Instruction("R", "nop", [])
