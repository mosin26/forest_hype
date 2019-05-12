import laspy
import sys
import numpy as np
from scipy.spatial import cKDTree

'''
    This code generates DEM (DTM or DSM) for specific ROI

    How to run:
    python3 las2dem.py input_file.las output_file class_int (2 or 5)
'''

## Regions of interest
forest_area = [53085364, 681550046, 53085364+100*100, 681550046-100*100]

def in_ROI(x, y, area):
    ROI_x0 = area[0]
    ROI_y0 = area[3]
    ROI_x1 = area[2]
    ROI_y1 = area[1]
    if x > ROI_x0 and x < ROI_x1 and y > ROI_y0 and y < ROI_y1:
        return True
    return False

in_file = laspy.file.File(sys.argv[1], mode = "r")
out_file = open(sys.argv[2]+".txt", 'w')
point_records = in_file.points.copy()

classification = int(sys.argv[3])
print("Class = "+str(classification))
trees_only = np.where(in_file.raw_classification == classification)

# pull out full point records of filtered points, and create an XYZ array for KDTree
trees_points = in_file.points[trees_only]     

max_x = 0
min_x = 981550046
max_y = 0
min_y = 981550046
for trees_point in trees_points:
    print("%.2f %.2f" % (trees_point['point']['X'], trees_point['point']['Y'])) 
    out_file.write("%.2f %.2f %.2f\n" % (trees_point['point']['X']/100, trees_point['point']['Y']/100, trees_point['point']['Z']/100))
    if trees_point['point']['X'] < min_x:
        min_x = trees_point['point']['X']
    if trees_point['point']['X'] > max_x:
        max_x = trees_point['point']['X']
    if trees_point['point']['Y'] < min_y:
        min_y = trees_point['point']['Y']
    if trees_point['point']['Y'] > max_y:
        max_y = trees_point['point']['Y']
print(min_x)
print(max_x)
print(min_y)
print(max_y)

out_file.close()

