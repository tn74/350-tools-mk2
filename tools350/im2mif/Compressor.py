from PIL import Image
from typing import List, Tuple
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
        x = images[0].getcolors(images[0].size[0] * images[0].size[1])
        colors = []
        reduce(lambda res, head: res.append(list(map(lambda x: x[1], head.getcolors(head.size[0]*head.size[1])))), images, colors)
        colors = colors[0]
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
            colors = list(map(lambda x: x[1], image.getcolors(LARGE)))
            model = Compressor.get_model(colors, limit)
            for color in model.labels_:
                if color_mif.index_of(color) < 0:
                    r, g, b = color
                    color_mif.add(RGB(r=r, g=g, b=b))
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
        data = model.labels_[model.predict(im.getdata())]
        # for pixel in im.getdata():
        #     p = np.array(pixel)
        #     model.
        #     x = list(map(lambda y: int(y), model.labels_[model.predict(p)]))
        #     data.append(x)
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
        limit = len(colors) if limit > len(colors) else limit  # If the limit is too high, lower it to the right number
        return MiniBatchKMeans(n_clusters=limit, batch_size=int(limit/32), init_size=3*limit).fit(np.array(colors))

    @classmethod
    def compress_pixels(cls, im: Image.Image, compression_ratio: float) -> Image.Image:
        new_dims = tuple(map(lambda x: int(compression_ratio*x), im.size))
        return im.resize(new_dims, Image.LANCZOS)
