import numpy as np

import fiona
from shapely import geometry

from skimage.feature import peak_local_max
from skimage.filters import gaussian


def trees_detection(input_layer, input_raster, output_shapefile_path, smoothing=0, min_distance=3, exclude_border=3, mask=None):
#     input_raster = np.copy(input_raster)
    if mask is not None:
        input_raster[np.where(mask)] = 0
    input_raster = gaussian(input_raster, sigma=smoothing)
    tree_tops = peak_local_max(input_raster, min_distance=min_distance, exclude_border=exclude_border, indices=True)
    
    schema = {'geometry': 'Point', 'properties': {'id': 'int'},}
    with fiona.open(output_shapefile_path, 'w', 'ESRI Shapefile', schema, input_layer.crs) as c:
        for i, tree_top in enumerate(tree_tops):
            tree_point = geometry.Point(input_layer.xy(tree_top[0], tree_top[1]))
            c.write({'geometry': geometry.mapping(tree_point), 'properties': {'id': i},})
            
            