from io import StringIO, IOBase
from typing import List

from assembler.instruction.Instruction import Instruction
from assembler.parsing.Parser import Parser
from zipfile import ZipFile


class Assembler:

    def __init__(self, ):
        pass

    @classmethod
    def assemble_all(cls, files: List[str], additional_declarations: dict) -> IOBase:
        parser_ = Parser(additional_declarations['registers'], additional_declarations['instructions'])
        return Assembler._zip(files, [cls.assemble(file, parser_) for file in files])

    @classmethod
    def assemble(cls, file: str, parser_: Parser) -> StringIO:
        with open(file, 'r') as f:
            parser_.clear()
            text = parser_.preprocess_assembly(f.readlines())
            ret = StringIO()
            ret.write(Assembler.HEADER)
            ret.writelines([Assembler.format_line(parser_.parse_line(line), line, i) for i, line in enumerate(text)])
            ret.write(Assembler.FOOTER.format(len(text), str(Assembler.NOP)))
            return ret

    @classmethod
    def format_line(cls, instr: Instruction, mips: str, number: int) -> str:
        return Assembler.MIF_LINE.format(number, str(instr), mips)

    @classmethod
    def _zip(cls, file_names: List[str], assembled_files: List[StringIO]) -> StringIO:
        zipped = StringIO()
        with ZipFile(zipped, 'w+') as zip_:
            for filename, file in zip_(file_names, assembled_files):
                zip_.writestr(filename, file.getvalue())
                file.close()
        return zipped

    HEADER = """DEPTH = 4096;\nWIDTH = 32;\nADDRESS_RADIX = DEC;\nDATA_RADIX = BIN;\nCONTENT\nBEGIN\n"""
    MIF_LINE = """{0.4d} : {0.32s}; -- {}\n"""
    FOOTER = """[{0.4d}..4095] : {0.32s};\nEND;\n"""
    NOP = Instruction("R")
