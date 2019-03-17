## Libraries
import numpy as np
import math
from raster_reader import set_raster, get_value

## CONSTANTS
X = 0
Y = 1
H = 2
PX = 3
PY = 4
P = 3
filename_in = "/home/roberto/Documents/LIDAR_DATA/Flight7/dsm_fil_for.txt"
filename_out = "/home/roberto/Documents/LIDAR_DATA/Flight7/dsm_raster.txt"

raster_coor = []  # [x0, y0, width, height]
raster_size = []  # [num_cols, num_rows]

RES = 0.4 # 40cm
def set_raster_dim():
    global raster_coor
    line = file_in.readline()
    values_str = line.rstrip().split(' ')
    raster_coor = [float(i) for i in values_str]
    raster_size.append(int(math.ceil(raster_coor[2]/RES)))
    raster_size.append(int(math.ceil(raster_coor[3]/RES)))

def load_values():
    array = []
    for line in file_in:
        values_str = line.rstrip().split(' ')
        values = [float(i) for i in values_str]
        dtm = get_value(values[X], values[Y])
        if dtm >= 0:
            values[H] -= dtm   #Mean value of DTM
        else:
            values[H] = 0
        pixel_coor_x = math.floor((values[X]-raster_coor[X]) / raster_coor[2] * raster_size[X])
        pixel_coor_y = math.floor((values[Y]-raster_coor[Y]) / raster_coor[3] * raster_size[Y])
        values.append(pixel_coor_x)
        values.append(pixel_coor_y)
        array.append(values)
    return array

def set_pixel_value(array):
    raster = np.full((raster_size[Y], raster_size[X]), -1.0)
    for point in array:
        if point[H] > raster[int(point[PY]),int(point[PX])]:
            raster[int(point[PY]),int(point[PX])] = point[H]
    return raster

def save_raster():
    for col_i, column in enumerate(raster, start=0):
        for row_i, height in enumerate(column, start=0):
            if height >= 0:
                print(str(raster_coor[X]+(row_i*RES)+RES/2)+" "+str(raster_coor[Y]+(col_i*RES)+RES/2)+" "+str(height))
                file_out.write(str(raster_coor[X]+(row_i*RES)+(7*RES/2))+" "+str(raster_coor[Y]+(col_i*RES)+(5*RES/2))+" "+str(height)+"\n")
            row_i += 1
########################### Main #################################

file_in = open(filename_in, "r")
file_out = open(filename_out, "w")
set_raster_dim()
input_array = load_values()
raster = set_pixel_value(input_array)
save_raster()
file_in.close()
file_out.close()

