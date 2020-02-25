import numpy as np

from PIL import Image, ImageOps
from typing import List, Tuple
from mif import Mif
from sklearn.cluster import MiniBatchKMeans
from rgb import RGB


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
        model = Compressor.get_model(colors, limit)
        colorMif = Mif(width=24)
        for color in {tuple(x) for x in model.cluster_centers_}:
            r, g, b = color
            colorMif.add(RGB(r=int(r), g=int(g), b=int(b)))
        recolored_images = [Compressor.recolor_image(image, model) for image in images]
        return colorMif, recolored_images


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
        batch_size = int(limit / 32) if limit > Compressor.__MIN_BATCH_SIZE else limit
        return MiniBatchKMeans(n_clusters=limit, batch_size=batch_size, tol=0.2, max_iter=75).fit(colors)

    @classmethod
    def compress_pixels(cls, im: Image.Image, cluster_size: int) -> Image.Image:
        """
        Compress the image by clustering adjacent pixels to center color value.
        :param im: Image to compress
        :param cluster_size: Size of the square used to define adjacent pixels
        :return: Compressed version of the original image. This is a new image object
        """
        if any(cluster_size > i for i in im.size):
            print("Pixel cluster value of {} too large for im of dimension {}x{}".format(cluster_size, *im.size))
            exit(1)
        new_data = np.zeros(im.size, dtype=(np.uint8, 3))
        cols, rows = im.size
        for row in range(0, rows, cluster_size):
            for col in range(0, cols, cluster_size):
                pixel_value = Compressor.sample_image(im, col, row, cluster_size)
                c_bound = min(col + cluster_size, cols)
                r_bound = min(row + cluster_size, rows)
                for r in range(row, r_bound):
                    for c in range(col, c_bound):
                        new_data[c][r] = pixel_value
        return ImageOps.mirror(Image.fromarray(new_data, mode="RGB").rotate(-90, expand=True))

    @classmethod
    def sample_image(cls, im: Image.Image, col: int, row: int, cluster_size: int) -> Tuple[int, int, int]:
        """
        Get the center color value inside a square with side length cluster_size and top left corner at (row, col)
        :param im: Image to sample from
        :param col: Col to sample near
        :param row: Row to sample near
        :param cluster_size: Size of the square to define adjacent pixels
        :return: RGB value of the pixel at the center of the square
        """
        row_delta = cluster_size if row + cluster_size < im.size[1] else im.size[1] - row
        col_delta = cluster_size if col + cluster_size < im.size[0] else im.size[0] - col
        sample = (col + int(col_delta / 2), row + int(row_delta / 2))
        x = im.getpixel(sample)
        return x

    __MIN_BATCH_SIZE = 200  # If there's fewer than this many colors, just do the whole thing at once, no mini batches
