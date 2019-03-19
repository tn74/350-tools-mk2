from math import log2, ceil


class MifEntry:

    def __init__(self, value=0, width=1):
        """
        :param value: Value of the entry
        :param width: Width of the entry, specified in bits
        """
        self.value = value
        self.width = self.hex_bits_needed(width)

    @staticmethod
    def hex_bits_needed(width: int) -> int:
        return int(width / 4)

    def set_width(self, width: int):
        self.width = self.hex_bits_needed(width)

    def hexify(self) -> str:
        return "{0:#0{1}x}".format(self.value, self.width)[2:].upper()  # [2:] to remove 0x from start of string

    def __eq__(self, other):
        return isinstance(other, MifEntry) and self.value == other.value and self.width == other.width

    def __str__(self):
        return self.hexify()
