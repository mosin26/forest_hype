## Libraries
import numpy as np
import math
from raster_metadata import set_raster, get_value

## Constants
X = 0 # Longitude
Y = 1 # Latitude
H = 2 # Height of Tree
T = 3 # Tree ID
P = 4 # Profile ID
D = 5 # Distance to DMX

R = 4 # Radius of Area of interest
NUM_PROF = 12
RS2 = R / math.sqrt(2)
R2 = R/2
R3 = R/2 * math.sqrt(3)
filename_in = "/home/roberto/Documents/LIDAR_DATA/Flight7/dsm_fil_for.txt"
filename_trees = "/home/roberto/Documents/LIDAR_DATA/Flight7/trees.txt"
filename_profiles = "/home/roberto/Documents/LIDAR_DATA/Flight7/profiles.txt"
filename_dtm = "/home/roberto/Documents/LIDAR_DATA/Flight7/dtm_1m_for.tif"

## Global variables
#profiles_x = [R, RS2, 0, -RS2, -R, -RS2,  0,  RS2, R]
#profiles_y = [0, RS2, R,  RS2,  0, -RS2, -R, -RS2, 0]
profiles_x = [R, R3, R2, 0, -R2, -R3, -R, -R3, -R2,  0,  R2, R3,  R]
profiles_y = [0, R2, R3, R,  R3, R2,   0, -R2, -R3, -R, -R3, -R2, 0]

lsps = []
trees = []
tree_counter = 1

def load_values():
    global lsps
    array = []
    for line in file_in:
        values_str = line.rstrip().split(' ')
        values = [float(i) for i in values_str]
        dtm = get_value(values[X], values[Y])
        if dtm >= 0:
            values[H] -= dtm   #Mean value of DTM
        else:
            values[H] = 0
        values.append(-1) # value reserved for tree id
        values.append(-1) # value reserved for profile id
        values.append(-1) # value reserved for distance to dmx
        array.append(values)
    lsps = np.transpose(array)


def get_sign(p0, p1, p2):
    return (p0[X] - p2[X]) * (p1[Y] - p2[Y]) - (p1[X] - p2[X]) * (p0[Y] - p2[Y])

def point_in_triangle(p, v0, v1, v2):
    d0 = get_sign(p, v0, v1)
    d1 = get_sign(p, v1, v2)
    d2 = get_sign(p, v2, v0)
    
    has_neg = (d0 < 0) or (d1 < 0) or (d2 < 0)
    has_pos = (d0 > 0) or (d1 > 0) or (d2 > 0)

    return not has_neg and has_pos
    
def generate_profile_vertices(gmx, index):
    v0 = gmx[X:Y+1]
    v1 = [gmx[X]+profiles_x[index], gmx[Y]+profiles_y[index]]
    v2 = [gmx[X]+profiles_x[index+1], gmx[Y]+profiles_y[index+1]]
    return [v0, v1, v2]

def generate_profiles(gmx):
    profiles_gmx = []
    for i in range(0,NUM_PROF):
        profile_gmx = generate_profile_vertices(gmx, i)
        profiles_gmx.append(profile_gmx)
    return profiles_gmx

#TODO: add constraint to evaluate only remaining points (currently positives only)
def evaluate_neighbors(gmx):
    global file_trees
    global lsps
    
    neighbors_i = np.where(np.logical_and(lsps[T] < 0, lsps[P] > 0))
    neighbors_sorted_i = np.argsort(lsps[D,neighbors_i])
    
    for i in range(0,NUM_PROF):
        mask = np.where(np.logical_and(lsps[T] < 0,lsps[P,:] == i))
        neighbors_sorted_i = np.argsort(lsps[D,mask[0]])
        min_height = gmx[H]
        no_decreasing = 0
        current_dist = 0
        for j in neighbors_sorted_i:
            if lsps[H, mask[0][j]] < min_height+0.3 and lsps[D, mask[0][j]]-current_dist < 0.5:
                current_dist = lsps[D, mask[0][j]]
                if lsps[H, mask[0][j]] < min_height:
                    min_height = lsps[H, mask[0][j]]
                lsps[T, mask[0][j]] = tree_counter
                for k in range (X,D+1):
                    file_trees.write(str(lsps[k, mask[0][j]])+" ")
                file_trees.write("\n")
            else:
                break

def get_distance(gmx, neighbor):
    x1 = gmx[X]
    y1 = gmx[Y]
    x2 = neighbor[X]
    y2 = neighbor[Y]
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

def find_area(gmx_profiles):
    global lsps
    maxx = []
    for i in range(0,len(lsps[0])):
        p = 0
        for profile in gmx_profiles:
            if point_in_triangle(lsps[:,i], profile[0], profile[1], profile[2]):
                maxx.append(lsps[H,i])
                lsps[P,i] = p
                lsps[D,i] = get_distance(profile[0], lsps[:,i])
                for k in range (X,D+1):
                    file_profiles.write(str(lsps[k, i])+" ")
                file_profiles.write("\n")

            p += 1

        
def find_global_maximum():
    mask = np.where(lsps[T] < 0)
    max_height = np.argmax(lsps[H, mask[0]]) #Check if it is > 0; if not stop
    maxx = 0
    max_index = -1
    for i in mask[0]:
        if lsps[H, i] > maxx:
            maxx = lsps[H, i]
            max_index = i
    return lsps[:,max_index]

########################### Main #################################
set_raster(filename_dtm)
file_in = open(filename_in, "r")
file_trees = open(filename_trees, "w")
file_profiles = open(filename_profiles, "w")
load_values()
for i in range(1,5):
    gmx = find_global_maximum()
    gmx_profiles = generate_profiles(gmx)
    find_area(gmx_profiles)

    tree = evaluate_neighbors(gmx)
    print("Iteration: "+str(tree_counter)+", maximum height: "+str(gmx[H]))
    tree_counter += 1

print("Saving file.............................")
file_trees.close()
file_profiles.close()

#TODO: Filter vegetation lower than 5 mts
