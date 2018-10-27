import fiona
import numpy as np
from shapely.geometry import mapping, Polygon, MultiPoint

def crowns_polygons(shapefile_path, crowns, dataset, row_shift=0, col_shift=0):
    schema = {'geometry': 'Polygon', 'properties': {'id': 'int'},}
    with fiona.open(shapefile_path, 'w', 'ESRI Shapefile', schema, dataset.crs) as c:
        for i, crown in enumerate(crowns):
            poly = Polygon(list(map(lambda point: dataset.xy(row_shift+point[1], col_shift+point[0]), crown)))
            c.write({'geometry': mapping(poly), 'properties': {'id': i},})

def crowns_points(shapefile_path, crowns, dataset, row_shift=0, col_shift=0):
    schema = {'geometry': 'MultiPoint', 'properties': {'id': 'int'},}
    points = np.stack((np.where(crowns==True)[0], np.where(crowns==True)[1]), axis=1)
    multi_point = MultiPoint(list(map(lambda point: dataset.xy(row_shift+point[0], col_shift+point[1]), points)))
    with fiona.open(shapefile_path, 'w', 'ESRI Shapefile', schema, dataset.crs) as c:
        c.write({'geometry': mapping(multi_point),'properties': {'id': 123},})
