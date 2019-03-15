import numpy as np
import math

## Constants
X = 0
Y = 1
H = 2
T = 3
R = 5
RS2 = R / math.sqrt(2)
filename_in = "/home/roberto/Documents/LIDAR_DATA/Flight7/dsm_fil_for.txt"
filename_out = "/home/roberto/Documents/LIDAR_DATA/Flight7/profile.txt"

## Global variables
profiles_x = [R, RS2, 0, -RS2, -R, -RS2,  0,  RS2, R]
profiles_y = [0, RS2, R,  RS2,  0, -RS2, -R, -RS2, 0]

lsps = []
trees = []
tree_counter = 1

def load_values():
    global lsps
    array = []
    for line in file_in:
        values_str = line.rstrip().split(' ')
        values = [float(i) for i in values_str]
        values[H] -= 190  #Mean value of DTM
        values.append(-1) # value reserved for the tree number
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
    for i in range(0,8):
        profile_gmx = generate_profile_vertices(gmx, i)
        profiles_gmx.append(profile_gmx)
    return profiles_gmx

def find_area(gmx_profiles):
    global lsps
    global trees
    for i in range(0,len(lsps[0])):
        for profile in gmx_profiles:
            if point_in_triangle(lsps[:,i], profile[0], profile[1], profile[2]):
                lsps[T,i] = tree_counter
                trees.append(lsps[:,i].copy())
#                file_out.write(str(lsps[X,i])+" "+str(lsps[Y,i])+" "+str(lsps[H,i])+" "+str(lsps[T,i])+"\n")

### The following line discards the points in area of the profiles, including the gmx
### This needs to be coded in another way
### First evaluating if the point is part of the tree
                lsps[H,i] = -1

        
def find_global_maximum():
    #print(len(lsps[H]))
    max_height = np.argmax(lsps[2])
    return lsps[:,max_height]


file_in = open(filename_in, "r")
file_out = open(filename_out, "w")
load_values()
for i in range(1,20):
    gmx = find_global_maximum()
    gmx_profiles = generate_profiles(gmx)
    tree_area = find_area(gmx_profiles)
    print("Iteration: "+str(tree_counter)+", maximum height: "+str(gmx))
    tree_counter += 1
print("Saving file")
for tree in trees:
    file_out.write(str(tree[X])+" "+str(tree[Y])+" "+str(tree[H])+" "+str(tree[T])+"\n")
file_out.close()
