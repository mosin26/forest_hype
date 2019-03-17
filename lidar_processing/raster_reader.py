from osgeo import gdal

min_coor_x = -1
min_coor_y = -1
ds = 0

def set_raster(filename):
    global min_coor_x
    global min_coor_y
    global ds
    ds = gdal.Open(filename)
    width = ds.RasterXSize
    height = ds.RasterYSize
    gt = ds.GetGeoTransform()
    min_coor_x = gt[0]
    min_coor_y = gt[3] + width*gt[4] + height*gt[5] 
    print(min_coor_x)
    print(min_coor_y)

def get_value(coor_x, coor_y):
    global ds
    rasterArray = ds.ReadAsArray()
    rel_coor_x = int(coor_x - min_coor_x)
    rel_coor_y = int(coor_y - min_coor_y)
    return rasterArray[rel_coor_y, rel_coor_x]
#    print(rasterArray)

filename_dtm = "/home/roberto/Documents/LIDAR_DATA/Flight7/dtm_1m_for.tif"
set_raster(filename_dtm)
#get_value(0,0)
print(get_value(530932.1,6815411.9))
