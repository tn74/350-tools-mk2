from io import BytesIO, StringIO
from typing import List
from zipfile import ZipFile
from os import path
from math import ceil, log2

LARGE = 2 ** 64


def num_bits_needed(x: int) -> int:
    return int(ceil(log2(x)))


def num_hex_bits_needed(x: int) -> int:
    return int(ceil(log2(x) / 4))


def fix_filename(name: str, extension: str) -> str:
    return '{}.{}'.format(path.basename(name).split('.')[0], extension)


def zip_(file_names: List[str], files: List[StringIO], file_type: str="mif") -> BytesIO:
    """
    Take a collection of StringIOs and zip them together into a single file
    :param file_names: Names of the zip entries
    :param files: StringIOs to write
    :param file_type: Extention for the new zip entries
    :return: BytesIO containing the zip file
    """
    ret = BytesIO()
    with ZipFile(ret, 'w') as zipped:
        for filename, file in zip(file_names, files):
            filename = fix_filename(filename, file_type)
            zipped.writestr(filename, file.getvalue())
            file.close()
        for file in zipped.filelist:
            file.create_system = 0
    return ret
