import numpy as np
import imageio
from scipy import ndimage
import os


def rotate_and_blur(image_path):
    full_path = os.path.join(os.path.dirname(__file__), image_path)
    img_array = imageio.imread(full_path)

    '''
    This can be replaced with `np.flipud(img_array)` or a related
    rotation method; when running `hdat run` the results
    and metrics should match within the defined examplesuite.check method.
    '''
    flipped_array = np.flip(img_array, 0)

    '''
    Changing the filter parameter `sigma` will alter the resulting image,
    failing the ExampleSuite.check method. Running `hdat show` will display
    the output, and then `hdat verify` can confirm the resulting
    image as the golden result for future runs.
    '''
    new_img_array = ndimage.gaussian_filter(flipped_array, sigma=(3, 3, 1))
    return new_img_array
