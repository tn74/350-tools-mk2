from math import ceil


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
        return int(ceil(width / 4))

    def set_width(self, width: int):
        self.width = self.hex_bits_needed(width)

    def hexify(self) -> str:
        s = hex(self.value)[2:]
        pad_len = self.width - len(s)
        return ('0' * pad_len) + s

    def __eq__(self, other):
        return isinstance(other, MifEntry) and self.value == other.value and self.width == other.width

    def __str__(self):
        return self.hexify()
