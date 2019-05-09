import warnings
import numpy as np
import cv2

from sklearn.metrics import r2_score
from sklearn.metrics.pairwise import euclidean_distances

from skimage.io import imread
from skimage.exposure import equalize_adapthist
from skimage.filters import gaussian
from skimage.color import rgb2gray
from skimage.feature import peak_local_max

import matplotlib.pyplot as plt


def get_transect_lines(img, center_point, max_radius=300, number_of_transects=8):
    transect_lines = []
    tree_circle = plt.Circle(center_point, max_radius)
    circle_points = tree_circle.get_verts()
    for transect_point in circle_points[:-1:int((len(circle_points)-1)/number_of_transects)]:
        transect_x = np.linspace(center_point[0], transect_point[0], max_radius)
        transect_y = np.linspace(center_point[1], transect_point[1], max_radius)
        max_x, max_y = img.shape
        in_the_image = np.where((transect_x < max_x-1) & (transect_x >= 0)
                                & (transect_y < max_y-1) & (transect_y >= 0))
        transect_lines.append((transect_x[in_the_image], transect_y[in_the_image]))
    return transect_lines

def fit_transect(img, transect, remove_pix=0, poly_deg=4):
    x, y = transect
    transect_values = img[y.astype(np.int), x.astype(np.int)]
    if remove_pix:
        transect_values = transect_values[:-remove_pix]
    transect_range = range(len(transect_values))
    fit_coeffs = np.polyfit(transect_range, transect_values, poly_deg)
    fitted_transect = np.poly1d(fit_coeffs)(transect_range)
    r2score = r2_score(transect_values, fitted_transect)
    return transect_values, fitted_transect, r2score, fit_coeffs

def scale_transects(img, transects, cut_off=0.9):
    scaled_transects = []
    for transect in transects:
        r2score, remove_pix = 0, 0
        while r2score < cut_off and remove_pix < len(transect[0])-1:
            transect_values, fitted_transect, r2score, c = fit_transect(img, transect, remove_pix=remove_pix)
            remove_pix = remove_pix + 1
        if len(transect[0][:-remove_pix])!=0:
            f = np.argmin(np.poly1d(c[:-1])(range(len(transect[0][:-remove_pix]))))
            scaled_transects.append((transect[0][:f], transect[1][:f]))
    return scaled_transects

def transect_averaging(transects, zscore_thrs=2):
    distances = np.array([len(transect[0]) for transect in transects])
    z_scores = (distances - distances.mean())/distances.std()
    return np.mean(distances[np.where(abs(z_scores)<zscore_thrs)])

def new_tops(img, local_maxima, tree_rads):
    tops = []
    for lm, r in zip(local_maxima, tree_rads):
        mask = np.zeros(img.shape, dtype=np.uint8)
        cv2.circle(mask, (lm[1], lm[0]), int(r), (255, 255, 255), -1, 8, 0)
        max_br = np.argmax(img[np.where(mask)])
        tops.append((np.where(mask)[0][max_br], np.where(mask)[1][max_br]))
    return np.array(tops)

def group_list(points_list):
    end_flag = False
    while not end_flag:
        end_flag = True
        for i in range(len(points_list)):
            for_check = points_list[i+1:]
            for points in for_check:
                if any(point in points_list[i] for point in points):
                    end_flag = False
                    points_list[i].extend(points)
                    points_list.remove(points)
        points_list = [list(e) for e in map(set, points_list)]
    return(points_list)

def minimum_distance_filter(points, min_dist=5):
    points = np.array(points)
    distances = euclidean_distances(points)
    close_points = np.where(distances<min_dist)
    close_points = [frozenset((x,y)) for (x,y) in zip(close_points[0], close_points[1])]
    close_points = [list(x) for x in set(close_points)]
    points_groups = group_list(close_points)
    points_groups = [tuple(np.mean(points[g],0,dtype=np.uint)) for g in points_groups]
    return np.array(points_groups)

def get_polygon(transects, min_edge_dist=20, zscore_thrs=2):
    transects = np.array(transects)
    distances = np.array([len(transect[0]) for transect in transects])
    z_scores = (distances - distances.mean())/distances.std()
    transects = transects[np.where((distances>min_edge_dist) & (z_scores<zscore_thrs))]
    points = np.array([(int(transect[0][-1]), int(transect[1][-1])) for transect in transects])
    if len(points) != 0:
        points = np.append(points, [points[0]], axis=0)
    return points

def angle(x1, y1, x2, y2):
    # Use dotproduct to find angle between vectors
    # This always returns an angle between 0, pi
    numer = (x1 * x2 + y1 * y2)
    denom = np.sqrt((x1 ** 2 + y1 ** 2) * (x2 ** 2 + y2 ** 2))
    return np.degrees(np.arccos(numer / denom))

def cross_sign(x1, y1, x2, y2):
    # True if cross is positive
    # False if negative or zero
    return x1 * y2 > x2 * y1

def remove_angles(polygon, min_angle=30):
    points = polygon
    new_polygon = []
    p1, ref, p2 = points[1], points[0], points[-2]
    x1, y1 = p1[0] - ref[0], p1[1] - ref[1]
    x2, y2 = p2[0] - ref[0], p2[1] - ref[1]
    if angle(x1, y1, x2, y2)>min_angle:
        new_polygon.append(ref)
    for i in range(1, len(points)-1):
        p1, ref, p2 = points[i+1], points[i], points[i-1]
        x1, y1 = p1[0] - ref[0], p1[1] - ref[1]
        x2, y2 = p2[0] - ref[0], p2[1] - ref[1]
        if angle(x1, y1, x2, y2)>min_angle:
            new_polygon.append(ref)
    if len(new_polygon)<3:
        return np.array([])
    if list(new_polygon[0]) != list(new_polygon[-1]):
        new_polygon.append(new_polygon[0])
    return(np.array(new_polygon))

def delineate_crowns(img, tree_tops, max_r=300, n_of_tr=32, cut_off=0.92, min_edge_dist=10, min_angle=40, zscore=2):
    tree_crowns = []
    tree_crowns_smoothed = []
    for t in tree_tops:
        transects = get_transect_lines(img, (t[1], t[0]), max_radius=max_r, number_of_transects=n_of_tr)
        scaled_transects = scale_transects(img, transects, cut_off=cut_off)
        tree_crown = get_polygon(scaled_transects, min_edge_dist=min_edge_dist, zscore_thrs=zscore)
        if len(tree_crown) != 0:
            tree_crown_smoothed = remove_angles(tree_crown, min_angle=min_angle)
        if tree_crown.size!=0:
            tree_crowns.append(tree_crown)
        if tree_crown_smoothed.size!=0:
            tree_crowns_smoothed.append(tree_crown_smoothed)
    return tree_crowns, tree_crowns_smoothed


def itcd(input_img, smoothing=30, rgb=True, min_crown=50, max_crown=300, n_transects=64,
                   fitting=0.9, outliers=2, sharpness=50):
    # loading data
    if rgb:
        img_gray = rgb2gray(input_img)
    else:
        img_gray = input_img
    # preprocessing
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        img_equlized = equalize_adapthist(img_gray)
    img_gaussian = gaussian(img_equlized, smoothing)
    # local maxima
    local_maxima = peak_local_max(img_gaussian, min_crown)
    # estimate trees widths
    tree_rads = []
    for lm in local_maxima:
        transects = get_transect_lines(img_gaussian, (lm[1], lm[0]), max_radius=max_crown,
                                       number_of_transects=n_transects)
        scaled_transects = scale_transects(img_gaussian, transects, cut_off=fitting)
        radius = transect_averaging(scaled_transects, zscore_thrs=outliers)
        tree_rads.append(radius)
    # compute new local maxima
    tops = new_tops(img_gaussian, local_maxima, tree_rads)
    # apply minimum distance filter
    final_tops = minimum_distance_filter(tops, min_crown)
    # delineate crowns
    crowns, crowns_s = delineate_crowns(img_gaussian, final_tops, max_r=max_crown, cut_off=fitting, zscore=outliers,
                                        min_edge_dist=min_crown, n_of_tr=n_transects, min_angle=sharpness)
    return crowns_s
