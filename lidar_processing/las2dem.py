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
global_area = [53050878, 681576017, 53050878+1000*100, 681576017-1000*100]
deforested_area = [53058955, 681563788, 53058955+100*100, 681563788-100*100]
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
out_file_g = open(sys.argv[2]+"_glo.txt", 'w')
out_file_d = open(sys.argv[2]+"_def.txt", 'w')
out_file_f = open(sys.argv[2]+"_for.txt", 'w')
point_records = in_file.points.copy()

classification = int(sys.argv[3])
print("Class = "+str(classification))
trees_only = np.where(in_file.raw_classification == classification)

# pull out full point records of filtered points, and create an XYZ array for KDTree
trees_points = in_file.points[trees_only]     

deforested_density = 0
forest_density = 0
total_density = 0
for trees_point in trees_points:
    if in_ROI(trees_point['point']['X'], trees_point['point']['Y'], global_area):
        print("%.2f %.2f" % (trees_point['point']['X'], trees_point['point']['Y'])) 
        out_file_g.write("%.2f %.2f %.2f\n" % (trees_point['point']['X']/100, trees_point['point']['Y']/100, trees_point['point']['Z']/100))
        if in_ROI(trees_point['point']['X'], trees_point['point']['Y'], deforested_area):
            deforested_density += 1
            out_file_d.write("%.2f %.2f %.2f\n" % (trees_point['point']['X']/100, trees_point['point']['Y']/100, trees_point['point']['Z']/100))
        elif in_ROI(trees_point['point']['X'], trees_point['point']['Y'], forest_area):
            forest_density += 1
            out_file_f.write("%.2f %.2f %.2f\n" % (trees_point['point']['X']/100, trees_point['point']['Y']/100, trees_point['point']['Z']/100))
        total_density += 1

deforested_density /= 10000
forest_density /= 10000
total_density /= 1000000

print("deforested density " + str(deforested_density))
print("forest density " + str(forest_density))
print("total density " + str(total_density))

out_file_g.close()
out_file_f.close()
out_file_d.close()
