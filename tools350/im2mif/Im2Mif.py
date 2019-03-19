from ..util.util import *
from .Compressor import Compressor
from PIL import Image
from .mif import Mif
from .rgb import RGB
from .MifEntry import MifEntry


class Im2Mif:

    @classmethod
    def convert(cls, files: List[str], names: List[str], compression_ratio: float, max_colors: int,
                bulk_color_compression: bool) -> BytesIO:
        images: List[Image.Image] = [Image.open(f) for f in files]
        compressed = [Compressor.compress_pixels(im, compression_ratio) for im in images]
        max_colors = LARGE if max_colors < 1 else max_colors

        if bulk_color_compression:
            color_mif, color_compressed = Compressor.compress_colors_collective(compressed, max_colors)
        else:
            color_mif, color_compressed = Compressor.compress_colors_individual(compressed, max_colors)

        mifs = [color_mif] + [Im2Mif.mifify(im, color_mif) for im in color_compressed]
        names = ["colors.foo"] + names
        ret = zip_(names, [StringIO(str(x)) for x in mifs])
        [x.close() for x in images + compressed + color_compressed]
        return ret

    @classmethod
    def mifify(cls, im: Image.Image, color_mif: Mif) -> Mif:
        ret = Mif()
        width = int(num_bits_needed(color_mif.get_num_entries()) / 4)  # Over 4 since using hex radix
        for pixel in im:
            r, g, b = pixel
            color_dex = color_mif.index_of(RGB(r=r, b=b, g=g))
            if color_dex > 0:
                ret.add(MifEntry(value=color_dex, width=width))
            else:
                raise ValueError("Cannot find pixel color in color MIF: {}".format(str(pixel)))
        return ret