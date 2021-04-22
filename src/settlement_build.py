import rasterio
from rasterio.merge import merge
import os
import sys
import geopandas as gpd

def raster_to_point(pop_shp, proj_path):
    """
    Find all VIIRS files named avg_rade9h and mosaic them.
    Extract values to point layer (population layer 1kmx1km)
    """
    current = os.getcwd()
    os.chdir(proj_path)
    files = os.listdir(proj_path)
    tiffiles = []
    for file in files:
        if file.endswith('.tif'):
            f = os.path.abspath(file)
            tiffiles += [f]
    keyword = 'avg_rade9h'  #	(avg_rade9h) nW/cm2/sr https://eogdata.mines.edu/products/vnl/#annual_v2
    viirs = []
    for fname in tiffiles:
        if keyword in fname:
            src = rasterio.open(fname)
            viirs.append(src)

    mosaic, out_trans = merge(viirs)
    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff", "height": mosaic.shape[1],"width": mosaic.shape[2], "transform": out_trans, "crs": ({'init': 'EPSG:32737'})})

    with rasterio.open('%s/viirs.tif' % proj_path, "w", **out_meta) as dest:
        dest.write(mosaic)

    settlements = gpd.read_file(pop_shp)
    print(settlements.crs)
    settlements = settlements[['pointid', 'grid_code', 'geometry']]
    settlements.index = range(len(settlements))
    coords = [(x, y) for x, y in zip(settlements.geometry.x, settlements.geometry.y)]

    # Open the raster and store metadata
    nighttimelight = rasterio.open('%s/viirs.tif' % proj_path)
    print(nighttimelight.crs)

    # Sample the raster at every point location and store values in DataFrame
    settlements['Nighttime light'] = [x[0] for x in nighttimelight.sample(coords)]
    print("Nighttime light")
    return (settlements)

def near_calculations_line(point, proj_path):
    """
    Calculates the nearest distance to lines in relation to population points (1kmx1km)
    """
    lines = gpd.read_file(proj_path + '/Concat_Transmission_lines_UMT37S.shp')
    print(lines.crs)
    point['Distance_to_HV_MV_LV lines'] = point.geometry.apply(lambda x: lines.distance(x).min())
    print("Distance to lines")

    road = gpd.read_file(proj_path + '/UMT37S_Roads.shp')
    print(road.crs)
    point['Distance_to_Roads'] = point.geometry.apply(lambda x: road.distance(x).min())
    print("Distance to road")
    return(point)

def near_calculations_point(point, proj_path):
    """
    Calculates the nearest distance to points in relation to population points (1kmx1km)
    """
    sub = gpd.read_file(proj_path + '/UMT37S_Primary_Substations.shp')
    print(sub.crs)
    point['Distance_to_substations'] = point.geometry.apply(lambda x: sub.distance(x).min())
    print("Distance to substations")

    trans = gpd.read_file(proj_path + '/UMT37S_Distribution_Transformers.shp')
    print(trans.crs)
    point['Distance_to_transformers'] = point.geometry.apply(lambda x: trans.distance(x).min())
    print("Distance to transformers")

    minigrid = gpd.read_file(proj_path + '/Concat_Mini-grid_UMT37S.shp')
    print(minigrid.crs)
    point['Distance_to_Mini-grid'] = point.geometry.apply(lambda x: minigrid.distance(x).min())
    print("Distance to minigrid")

    point.to_file("../Projected_files/settlements_distance.shp")
    return(point)

if __name__ == "__main__":
    pop_shp, Projected_files_path = sys.argv[1], sys.argv[2]
    points = raster_to_point(pop_shp, Projected_files_path)
    point_line = near_calculations_line(points, Projected_files_path)
    settlements = near_calculations_point(point_line, Projected_files_path)