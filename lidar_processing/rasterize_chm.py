## Libraries

import time
import numpy as np
import math
import rasterio
from rasterio.transform import from_origin
from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage.morphology import grey_dilation, grey_opening
from scipy.ndimage import generate_binary_structure
## CONSTANTS
X = 0
Y = 1
H = 2
PX = 3
PY = 4
P = 3
filename_las_in = "../../data/lidar/THD29/dtm_29_minmax.txt"
filename_dtm_in = "../../data/lidar/dtm_thd29_linear.tif"
#filename_out = "../../data/lidar/chm_2.tif"
filename_out = "../../data/lidar/chm_THD29_linear_33.tif"
chm_points_out = "../../data/lidar/chm_THD29_linear_33.txt"

raster_coor = []  # [x0, y0, width, height]
raster_size = []  # [num_cols, num_rows]

RES = 0.33 # 40cm
def set_raster_dim():
    global raster_coor
    line = file_las_in.readline()
    values_str = line.rstrip().split(' ')
    raster_coor = [float(i) for i in values_str]
    raster_size.append(int(math.ceil(raster_coor[2]/RES)))
    raster_size.append(int(math.ceil(raster_coor[3]/RES)))
    print(raster_coor)
    print(raster_size)
    time.sleep(5)

def load_values():
    array = []
    for line in file_las_in:
        values_str = line.rstrip().split(' ')
        values = [float(i) for i in values_str]
        # Need to read the raster with geographic coordinates instead
        row, col = file_dtm_in.index(values[X], values[Y]) 
        '''if row > 100:
            row = 100
        if col > 100:
            col = 100'''
        dtm = dtm_band[row, col]
        if dtm >= 0:
            values[H] -= dtm   #Mean value of DTM
        else:
            values[H] = 0
        pixel_coor_x = math.floor((values[X]-raster_coor[X]) / raster_coor[2] * raster_size[X])
        pixel_coor_y = raster_size[Y] - math.floor((values[Y]-raster_coor[Y]) / raster_coor[3] * raster_size[Y])
        values.append(pixel_coor_x)
        values.append(pixel_coor_y)
        array.append(values)
    return array

def set_pixel_value(array):
    chm_array = np.full((raster_size[Y], raster_size[X]), 0.0)
    for point in array:
        if point[PX] < raster_size[X] and point[PY] < raster_size[Y]:
            if point[H] > chm_array[int(point[PY]),int(point[PX])]:
                chm_array[int(point[PY]),int(point[PX])] = point[H]
    footprint = generate_binary_structure(2, 1)
    filtered_chm = grey_dilation(chm_array, footprint=footprint)
    #filtered_chm = gaussian_filter(chm_array, sigma=1)
    #filtered_chm = chm_array
    return np.maximum(filtered_chm, chm_array)

def save_raster(chm_array):
    print(raster_coor[X])
    print(raster_coor[Y])
    transform = from_origin(raster_coor[X], raster_coor[Y]+raster_coor[3]+5, RES, RES)
    chm_raster = rasterio.open(filename_out, 'w', driver='GTiff',
                            height = chm_array.shape[0], width = chm_array.shape[1],
                            count=1, dtype=str(chm_array.dtype),
                            #crs='100026',
                            transform=transform)
                            #crs='EPSG:32638',
    chm_raster.write(chm_array, 1)
    chm_raster.close()

########################### Main #################################
file_las_in = open(filename_las_in, "r")
file_dtm_in = rasterio.open(filename_dtm_in)
dtm_band = file_dtm_in.read(1)
file_out = open(chm_points_out, "w")
set_raster_dim()
input_array = load_values()
chm_array = set_pixel_value(input_array)
save_raster(chm_array)
file_las_in.close()
file_out.close()
