
from skimage import draw
from skimage import io
import numpy as np
import json
import os
import sys


def poly2mask(blobs, path_to_masks_folder, h, w):
    mask = np.zeros((h, w))
    for l in blobs:
        fill_row_coords, fill_col_coords = draw.polygon(l[1], l[0], l[2])
        mask[fill_row_coords, fill_col_coords] = 1
    io.imsave(path_to_masks_folder + "/" + str(0) + ".png", mask)


def convert_dataturks_to_masks(path_to_dataturks_annotation_json, path_to_masks_folder):
    f = open(path_to_dataturks_annotation_json)
    train_data = f.readlines()
    train = []
    for line in train_data:
        data = json.loads(line)
        train.append(data)

    blobs = []
    points = train[0][1]['Label']['Tree'][0]['geometry']
    h = 256
    w = 256
    x_coord = []
    y_coord = []
    l = []
    for p in points:
        x_coord.append(p['x'])
        y_coord.append(p['y'])
    shape = (h, w)
    l.append(x_coord)
    l.append(y_coord)
    l.append(shape)
    blobs.append(l)
    poly2mask(blobs, path_to_masks_folder, h, w)


convert_dataturks_to_masks('/Users/vasilii.mosin/Desktop/cjmgjfit4qavs0729jbxs19zn-cjmgjfitvcixd0780wp7lkd1i-export-2018-09-24T17-54-49.675Z.json',
                            '/Users/vasilii.mosin/Desktop/')
