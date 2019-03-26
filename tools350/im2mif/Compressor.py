from PIL import Image
from typing import List, Tuple, Collection, Set
from .mif import Mif
from sklearn.cluster import MiniBatchKMeans
import numpy as np
from functools import reduce
from .rgb import RGB
from ..util.util import LARGE




class Compressor:

    @classmethod
    def compress_colors_collective(cls, images: List[Image.Image], limit: int) -> Tuple[Mif, List[Image.Image]]:
        """
        Compress the colors in the images, keeping the desired count across all images
        :param limit: Maximum allowed colors
        :param images: Images to compress
        :return: The resultant color MIF file for the images and the new, color compressed images
        """
        colors = [pix for im in images for pix in im.getdata()]

        # reduce(lambda res, head: res.append(tuple(map(lambda x: x[1], head.getcolors(head.size[0]*head.size[1])))),
        #        images, colors)
        model = Compressor.get_model(colors, limit)
        colorMif = Mif(width=24)
        for color in model.cluster_centers_:
            r, g, b = color
            colorMif.add(RGB(r=int(r), g=int(g), b=int(b)))
        recolored_images = [Compressor.recolor_image(image, model) for image in images]
        return colorMif, recolored_images

    @classmethod
    def compress_colors_individual(cls, images: List[Image.Image], limit: int) -> Tuple[Mif, List[Image.Image]]:
        """
        Compress the colors in the images, keeping the desire count in each image
        :param limit: Maximum allowed colors
        :param images: Images to compress
        :return: The resultant color MIF file for the images and the new, color compressed images
        """
        color_mif = Mif(width=24)
        ret_images = []
        for image in images:
            colors = list(map(lambda x: x[1], image.getcolors(image.size[0] * image.size[1])))
            model = Compressor.get_model(colors, limit)
            for color in model.cluster_centers_:
                if color_mif.index_of(color) < 0:
                    r, g, b = color
                    color_mif.add(RGB(r=int(r), g=int(g), b=int(b)))
            ret_images.append(Compressor.recolor_image(image, model))
        return color_mif, ret_images

    @classmethod
    def recolor_image(cls, im: Image.Image, model: MiniBatchKMeans) -> Image.Image:
        """
        Copy to color compressed space of the old image into a new Image
        :param im: Original image
        :param model: Model to used to replace colors
        :return: New image representation of the image in the reduced color space
        """
        ret = Image.new(im.mode, im.size)
        data = model.predict(im.getdata())
        f = lambda x: int(x)
        g = lambda x: tuple(map(f, x))
        d = list(map(g, model.cluster_centers_[data]))
        ret.putdata(d)
        return ret

    @classmethod
    def get_model(cls, colors: List[Tuple[int, int, int]], limit: int) -> MiniBatchKMeans:
        """
        Get a model for reducing colors to a selected color, ie the closest selected color
        :param colors: All the colors in the image(s)
        :param limit: Maximum selected colors
        :return: A K-means predictor to will map all the colors to the desired limit
        """
        colors = np.squeeze(np.array(list(colors)))
        limit = len(colors) if limit > len(colors) else limit  # If the limit is too high for sklearn's k-means,
                                                               # lower it to the right number
        batch_size = int(limit / 32) if limit > (Compressor.__MIN_BATCH_SIZE) else limit
        return MiniBatchKMeans(n_clusters=limit, batch_size=batch_size, init_size=3 * limit).fit(colors)

    @classmethod
    def compress_pixels(cls, im: Image.Image, compression_ratio: float) -> Image.Image:
        new_dims = tuple(map(lambda x: int(compression_ratio*x), im.size))
        return im.resize(new_dims, Image.LANCZOS)

    __MIN_BATCH_SIZE = 200  # If there's less than colors, just do the whole thing at once
