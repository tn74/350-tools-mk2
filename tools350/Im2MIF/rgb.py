from MifEntry import MifEntry


class RGB(MifEntry):

    def __init__(self, *, r=0, g=0, b=0):
        """
        :param r: Red value
        :param g: Green value
        :param b: blue value
        """
        for val in [r, g, b]:
            assert 0 <= val < 256, "Must specify value in range (0,256] for R, G, and B"
        value = (b << 16) + (g << 8) + r  # Prod value for FGPA layout
        # value = (r << 16) + (g << 8) + b  # Local testing value with RGB
        super().__init__(value=value, width=24)
