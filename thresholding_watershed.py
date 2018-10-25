import warnings
import numpy as np

from scipy import ndimage as ndi

from skimage.segmentation import watershed
from skimage.segmentation import find_boundaries
from skimage.morphology import binary_dilation
from skimage.exposure import equalize_adapthist
from skimage.filters import gaussian
from skimage.color import rgb2gray
from skimage.filters import threshold_mean
from skimage.feature import peak_local_max


def delineate_boundaries(segments, n_dilation=3):
    boundaries = find_boundaries(segments)
    for i in range(n_dilation):
        boundaries = binary_dilation(boundaries)
    return boundaries

def itcd(input_img, smoothing=30, rgb=True, n_dilation=3):
    """
    Returns boundaries of tree crowns in the imageself.
    Implementation of canopies thresholding and watershed segmentation.

    input_img: input image (np.array)
    """
    if rgb:
        img_gray = rgb2gray(input_img)
    else:
        img_gray = input_img

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        img_equlized = equalize_adapthist(img_gray)
    img_gaussian = gaussian(img_equlized, smoothing)

    canopy_mask = img_gaussian > threshold_mean(img_gaussian)

    masked_gaussian = np.copy(img_gaussian)
    masked_gaussian[canopy_mask==False] = 0

    local_maxima = peak_local_max(masked_gaussian, min_distance=1, exclude_border=0, indices=False)
    markers, n_labels = ndi.label(local_maxima)

    segments = watershed(-img_gaussian, markers, mask=canopy_mask)
    segments[np.where((segments==0) & (canopy_mask==True))] = n_labels+1

    boundaries = delineate_boundaries(segments,n_dilation=n_dilation)
    return boundaries
