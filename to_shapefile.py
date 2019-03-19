import fiona
import numpy as np
from shapely.geometry import mapping, Polygon, MultiPoint

def crowns_polygons(shapefile_path, crowns, dataset, row_shift=0, col_shift=0):
    """
    Write detected crowns in polygons list format to the shapefile.

    Args:
        shapefile_path (str): path where to save the shapefile
        crowns (list): list of crowns boundaries polygons
        dataset (rasterio.io.DatasetReader): image dataset used for crowns detection
        row_shift (int): starting point row (if windowing was used for image loading)
        col_shift (int): starting point column (if windowing was used for image loading)
    """
    schema = {'geometry': 'Polygon', 'properties': {'id': 'int'},}
    with fiona.open(shapefile_path, 'w', 'ESRI Shapefile', schema, dataset.crs) as c:
        for i, crown in enumerate(crowns):
            poly = Polygon(list(map(lambda point: dataset.xy(row_shift+point[1], col_shift+point[0]), crown)))
            c.write({'geometry': mapping(poly), 'properties': {'id': i},})

def crowns_points(shapefile_path, crowns, dataset, row_shift=0, col_shift=0):
    """
    Write detected crowns in mask format to the shapefile.

    Args:
        shapefile_path (str): path where to save the shapefile
        crowns (np.array): crowns boundaries points mask
        dataset (rasterio.io.DatasetReader): image dataset used for crowns detection
        row_shift (int): starting point row (if windowing was used for image loading)
        col_shift (int): starting point column (if windowing was used for image loading)
    """
    schema = {'geometry': 'MultiPoint', 'properties': {'id': 'int'},}
    points = np.stack((np.where(crowns==True)[0], np.where(crowns==True)[1]), axis=1)
    multi_point = MultiPoint(list(map(lambda point: dataset.xy(row_shift+point[0], col_shift+point[1]), points)))
    with fiona.open(shapefile_path, 'w', 'ESRI Shapefile', schema, dataset.crs) as c:
        c.write({'geometry': mapping(multi_point),'properties': {'id': 123},})
        
        
def crowns_segments(shapefile_path, crowns, dataset, row_shift=0, col_shift=0):
    schema = {'geometry': 'Polygon', 'properties': {'id': 'int'},}
    crowns = [np.where(crowns==i) for i in range(1,np.max(crowns)+1)]
    with fiona.open(shapefile_path, 'w', 'ESRI Shapefile', schema, dataset.crs) as c:
        for i, crown in enumerate(crowns):
            poly = MultiPoint(list(map(lambda point: dataset.xy(row_shift+point[1],col_shift+point[0]), 
                                       zip(crown[1],crown[0])))).convex_hull
            if type(poly) == Polygon:
                c.write({'geometry': mapping(poly), 'properties': {'id': i},})
