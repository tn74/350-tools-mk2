from io import StringIO, BytesIO
from typing import List
from os import path
from assembler.instruction.Instruction import Instruction
from assembler.parsing.Parser import Parser
from zipfile import ZipFile


class Assembler:

    @classmethod
    def assemble_all(cls, files: List[str], additional_declarations: dict) -> BytesIO:
        parser_ = Parser(additional_declarations['registers'], additional_declarations['instructions'])
        tmp = [cls.assemble(file, parser_) for file in files]
        return Assembler._zip(files, tmp)

    @classmethod
    def assemble(cls, file: str, parser_: Parser) -> StringIO:
        with open(file, 'r') as f:
            parser_.clear()
            text = parser_.preprocess_assembly(f.readlines())
            ret = StringIO()
            ret.write(Assembler.HEADER)
            ret.writelines([Assembler._parse_and_format_line(parser_, line, i+1) for i, line in enumerate(text)])
            ret.write(Assembler.FOOTER.format(len(text), str(Assembler.NOP)))
            return ret

    @classmethod
    def _parse_and_format_line(cls, parser_: Parser, mips: str, number: int) -> str:
        try:
            instr = parser_.parse_line(mips, number)
        except (AssertionError, SyntaxError) as e:
            instr = Instruction("R", "err", []).replace_with_error(str(e))
        # print(mips, '\n', str(instr))
        # print(Assembler.MIF_LINE.format(number, str(instr), mips))
        return Assembler.MIF_LINE.format(number, str(instr), mips)

    @classmethod
    def _zip(cls, file_names: List[str], assembled_files: List[StringIO]) -> BytesIO:
        zipped = BytesIO()
        with ZipFile(zipped, 'w') as zip_:
            for filename, file in zip(file_names, assembled_files):
                filename = Assembler.fix_filename(filename)
                zip_.writestr(filename, file.getvalue())
                file.close()
        return zipped

    @classmethod
    def fix_filename(cls, name: str) -> str:
        return '{}.mif'.format(path.basename(name).split('.')[0])

    HEADER = """DEPTH = 4096;\nWIDTH = 32;\nADDRESS_RADIX = DEC;\nDATA_RADIX = BIN;\nCONTENT\nBEGIN\n"""
    MIF_LINE = """{:04d} : {:32s}; -- {}\n"""
    FOOTER = """[{:04d}..4095] : {:32s};\nEND;\n"""
    NOP = Instruction("R", "nop", [])
