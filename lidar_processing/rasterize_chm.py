## Libraries
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
filename_las_in = "../../data/lidar/dsm_fil_for.txt"
filename_dtm_in = "../../data/lidar/dtm_1m_for.tif"
#filename_out = "../../data/lidar/chm_40cm_dilation.tif"
filename_out = "../../data/lidar/chm_40cm_gaussian.tif"
chm_points_out = "../../data/lidar/chm_grid_points.txt"

raster_coor = []  # [x0, y0, width, height]
raster_size = []  # [num_cols, num_rows]

RES = 0.4 # 40cm
def set_raster_dim():
    global raster_coor
    line = file_las_in.readline()
    values_str = line.rstrip().split(' ')
    raster_coor = [float(i) for i in values_str]
    raster_size.append(int(math.ceil(raster_coor[2]/RES)))
    raster_size.append(int(math.ceil(raster_coor[3]/RES)))

def load_values():
    array = []
    for line in file_las_in:
        values_str = line.rstrip().split(' ')
        values = [float(i) for i in values_str]
        # Need to read the raster with geographic coordinates instead
        dtm = dtm_band[int(values[X]-(file_dtm_in.bounds.left)), int(values[Y]-(file_dtm_in.bounds.bottom))]
        if dtm >= 0:
            values[H] -= dtm   #Mean value of DTM
        else:
            values[H] = 0
        pixel_coor_x = math.floor((values[X]-raster_coor[X]) / raster_coor[2] * raster_size[X])
        pixel_coor_y = raster_size[Y] - 1- math.floor((values[Y]-raster_coor[Y]) / raster_coor[3] * raster_size[Y])
        values.append(pixel_coor_x)
        values.append(pixel_coor_y)
        print("values")
        print(values)
        array.append(values)
    return array

def set_pixel_value(array):
    chm_array = np.full((raster_size[Y], raster_size[X]), 0.0)
    for point in array:
        if point[H] > chm_array[int(point[PY]),int(point[PX])]:
            chm_array[int(point[PY]),int(point[PX])] = point[H]
    footprint = generate_binary_structure(2, 1)
    #filtered_chm = grey_dilation(chm_array, footprint=footprint)
    filtered_chm = gaussian_filter(chm_array, sigma=0.95)
    return filtered_chm

def save_raster(chm_array):
    transform = from_origin(raster_coor[X], raster_coor[Y]+100, RES, RES)
    chm_raster = rasterio.open(filename_out, 'w', driver='GTiff',
                            height = chm_array.shape[0], width = chm_array.shape[1],
                            count=1, dtype=str(chm_array.dtype),
                            crs='EPSG:32638',
                            transform=transform)
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
