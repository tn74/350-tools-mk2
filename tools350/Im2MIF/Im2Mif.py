#!/usr/bin/env python3

from util.util import *
from Compressor import Compressor
from PIL import Image
from mif import Mif
from rgb import RGB
from MifEntry import MifEntry
import argparse as ap
from os.path import basename, dirname


class Im2Mif:

    @classmethod
    def pre_convert(): # formats images in case it has more than rgb values
        '''
        title = "test.png"
        count = count + 1
        png = Image.open(title)
        png.load()

        background = Image.new("RGB", png.size, (255,255,255))
        background.paste(png, mask=png.split()[3])

        background.save(title + ".jpg", "JPEG", quality=500)
        '''
        return

    @classmethod
    def convert(cls, files: List[str], cluster_size: int, max_colors: int) -> BytesIO:
        images: List[Image.Image] = [Image.open(f) for f in files]
        compressed = [Compressor.compress_pixels(im, cluster_size) for im in images] if cluster_size > 1 else images
        color_mif, color_compressed = Compressor.compress_colors_collective(compressed, max_colors)

        mifs = [color_mif] + [Im2Mif.mifify(im, color_mif) for im in color_compressed]
        names = ["colors.foo"] + [str(basename(f)) for f in files]

        ret = zip_(names, [StringIO(str(x)) for x in mifs])
        [x.close() for x in images + compressed + color_compressed if x]
        return ret

    @classmethod
    def mifify(cls, im: Image.Image, color_mif: Mif) -> Mif:
        width = num_bits_needed(color_mif.get_num_entries())
        ret = Mif(width=width)
        for pixel in im.getdata():
            r, g, b = pixel
            color_dex = color_mif.index_of(RGB(r=r, b=b, g=g))
            if color_dex < 0:
                color_dex = color_mif.index_of(color_mif.get_closest(RGB(r=r, b=b, g=g)))
            ret.add(MifEntry(value=color_dex, width=width))
        return ret


'''
if __name__ == '__main__':
    args = ap.ArgumentParser()
    args.add_argument('files', nargs='+', help='Path to image files -- for best results, use absolute path')
    args.add_argument('-c', '--colors', dest='colors', default=32, help='Max allowed colors in the color MIF.'
                                                                        ' Must be between 1 and 1024, inclusive')
    args.add_argument('-p', '--pixel-compression', dest='cluster_size', default=1, help='Pixel window size. Must be '
                                                                                        'less than the size of the '
                                                                                        'image')
    in_ = args.parse_args()
    if int(in_.colors) <= 0 or int(in_.colors) > 1024:
        args.print_help()
    else:
        by = Im2Mif.convert(files=in_.files, max_colors=int(in_.colors), cluster_size=int(in_.cluster_size))
        with open('{}/im-mifs.zip'.format(dirname(in_.files[0])), 'w+b') as file:
            file.write(by.getvalue())
'''
