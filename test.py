from io import BytesIO

from assembler.Assembler import Assembler
from zipfile import ZipFile


def test():

    assembler = Assembler()
    output: BytesIO = assembler.assemble_all(['/Users/matthew/Desktop/test.asm'],
                           {"registers": [], "instructions": []})

    print()
    x = ZipFile(output)
    with x.open('test.mif', 'r') as f:
        print('\n'.join([str(l) for l in f]))


if __name__ == "__main__":
    test()
