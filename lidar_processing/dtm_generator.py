#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
import rasterio
from rasterio.transform import from_origin


def save_raster(x_coor, y_coor, chm_array):
    chm_array = np.flip(chm_array, axis=0)
    transform = from_origin(x_coor, y_coor, 1, 1)
    chm_raster = rasterio.open("../../data/lidar/dtm_thd29_linear.tif", 'w', driver='GTiff',
                            height = chm_array.shape[0], width = chm_array.shape[1],
                            count=1, dtype=str(chm_array.dtype),
                            crs='EPSG:32638',
                            transform=transform)
    chm_raster.write(chm_array, 1)
    chm_raster.close()

file_las_in = open("/home/roberto/Documents/LIDAR_DATA/THD29/thd_000029_ground.txt", "r")

x_array = []
y_array = []
z_array = []
x_coor = 0
y_coor = 0
for line in file_las_in:
    values_str = line.rstrip().split(' ')
    values = [float(i) for i in values_str]
    x_array.append(values[0])
    y_array.append(values[1])
    z_array.append(values[2])

# data coordinates and values
x = np.array(x_array)
x_coor = np.floor(np.min(x))
y = np.array(y_array)
y_coor = np.floor(np.max(y))
z = np.array(z_array) 

# target grid to interpolate to
xi = np.arange(np.min(x),np.max(x),1)
yi = np.arange(np.min(y),np.max(y),1)
xi,yi = np.meshgrid(xi,yi)

# interpolate
zi = griddata((x,y),z,(xi,yi),method='linear')
print("-----------------------------------------------------------")
save_raster(x_coor, y_coor,zi)
print(x_coor)
print(np.floor(np.max(x))-np.floor(np.min(x)))
print(y_coor)
print(np.floor(np.max(y))-np.floor(np.min(y)))
