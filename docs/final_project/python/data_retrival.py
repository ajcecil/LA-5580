'''
Author: Alex Cecil
email: ajcecil@iastate.edu
Date Created: 2025-04-20
Last Modified: 2025-05-10
Purpose: Download RS data from Google Earth Engine and other sources
'''

import ee
import pandas as pd
import folium
import json
import requests
import zipfile
import io
import os
import arcpy
from PIL import Image
import datetime

start_time = datetime.datetime.now()

# Trigger Authentication and initialze Library in Google Earth Engine
ee.Authenticate()
ee.Initialize(project='ee-project1') #replace with project name


# Data Sources
soil_data = pd.read_csv(r'coordinate_data.csv') #replace with coordinate file
soil_data.columns = soil_data.columns.str.lower()



deg_cof = 69 # approximate miles n 1 degree of longitude and latitude
buffer = 0.035 # roughly 2.4 miles (0.035 deg)

''' AOI coordinates, formatted for a rectangular area
                (ax, ay) -------------- (bx, by)
                    |                      |
                    |                      |
                    |                      |
                    |                      |
                    |                      |
                    |                      |
                    |                      |
                    |                      |
                    |                      |
                    |                      |
                (dx, dy) -------------- (cx, cy)
'''

ax = (soil_data['x'].max()) + buffer
ay = (soil_data['y'].max()) + buffer

bx = (soil_data['x'].max()) + buffer
by = (soil_data['y'].min()) - buffer

cx = (soil_data['x'].min()) - buffer
cy = (soil_data['y'].min()) - buffer

dx = (soil_data['x'].min()) - buffer
dy = (soil_data['y'].max()) + buffer

aoi_json = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            ax,
                            ay
                        ],
                        [
                            bx,
                            by
                        ],
                        [
                            cx,
                            cy
                        ],
                        [
                            dx,
                            dy
                        ],
                        [
                            ax,
                            ay
                        ]
                    ]
                ]
            }
        }
    ]
}


aoi = ee.Geometry.Polygon(aoi_json['features'][0]['geometry']['coordinates'])

start_date = ee.Date('2024-08-01')
end_date = ee.Date('2024-12-31')


sen_2 = ee.Image(ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterBounds(aoi)
                .filterDate(start_date, end_date)
                .first()
                .clip(aoi)
                )

ls9 = ee.Image(ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
                .filterBounds(aoi)
                .filterDate(ee.Date('2024-06-15'), ee.Date('2024-07-15'))
                .first()
                .clip(aoi)
                )

location = aoi.centroid().coordinates().getInfo()[::-1]



sen_2_map = sen_2.select(
    ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12', 'TCI_R', 'TCI_G', 'TCI_B']
)

ls9_map = ls9.select(
    ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']
)

download_params = {
    'scale': 30,
    'crs': 'EPSG:4326',
    'region': json.dumps(aoi.getInfo()['coordinates'])
}

out_dir = r'products'
rgb_path = r'aoi_new_rgb.tif'
rgb_png = r'aoi_rgb.png'

s2_url = sen_2_map.getDownloadURL(download_params)
ls9_url = ls9_map.getDownloadURL(download_params)

r_s2 = requests.get(s2_url, stream = True)
r_s2.raise_for_status()

r_ls9 = requests.get(ls9_url, stream = True)
r_ls9.raise_for_status()

with zipfile.ZipFile(io.BytesIO(r_s2.content)) as z:

    s2_bands = z.namelist()

    for member in s2_bands:
        if member.lower().endswith('.tif'):
            z.extract(member, path= os.path.join(out_dir, 'sentinel_2'))


with zipfile.ZipFile(io.BytesIO(r_ls9.content)) as z:

    ls9_bands = z.namelist()

    for member in ls9_bands:
        if member.lower().endswith('.tif'):
            z.extract(member, path= os.path.join(out_dir, 'landsat_9'))

s2_true_red = os.path.join(out_dir, 'sentinel_2', s2_bands[12])
s2_true_green = os.path.join(out_dir, 'sentinel_2', s2_bands[13])
s2_true_blue = os.path.join(out_dir, 'sentinel_2', s2_bands[14])

arcpy.env.workspace = r"Project_Directory" #Replace with active directory to use relative paths



s2_rgb_bands = [
    s2_true_red,
    s2_true_green,
    s2_true_blue
]

arcpy.management.CompositeBands(
    in_rasters = s2_rgb_bands,
    out_raster = rgb_path
)

print(f"ArcGIS Pro Sentinel 2 composite at: {rgb_path}")



with Image.open(rgb_path) as img:

    aoi_rgb = img.convert("RGB")
    aoi_rgb.save(rgb_png)


sen_2_bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
ls_bands = ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']

cov_data = pd.DataFrame() 

for sample in range(len(soil_data)):
    # Create a dictionary for this sample
    sample_data = {
      'latitude': soil_data['y'][sample],
      'longitude': soil_data['x'][sample],
      'grower' : soil_data['grower'][sample],
      'farm' : soil_data['farm_name'][sample],
      'field' : soil_data['field_id'][sample],
      'samp_date' : pd.to_datetime(soil_data['samp_date'][sample]),
      'samp_id' : soil_data['samp_id'][sample],
      'ph' : soil_data['ph'][sample],
      'bph' : soil_data['bph'][sample],
      'om' : soil_data['om'][sample],
      'p_m3' : soil_data['p_m3'][sample],
      'p_bray' : soil_data['p_bray'][sample],
      'p_olsen' : soil_data['p_olsen'][sample],
      'k' : soil_data['k'][sample],
      'zn' : soil_data['zn'][sample],
      's' : soil_data['s'][sample],
      'cec' : soil_data['cec'][sample],
      'ca' : soil_data['ca'][sample],
      'mg' : soil_data['mg'][sample],
      'na' : soil_data['na'][sample],
      'h_sat' : soil_data['h_sat'][sample],
      'k_sat' : soil_data['k_sat'][sample],
      'mg_sat' : soil_data['mg_sat'][sample],
      'ca_sat' : soil_data['ca_sat'][sample],
      'na_sat' : soil_data['na_sat'][sample],
      'fe' : soil_data['fe'][sample],
      'cu' : soil_data['cu'][sample],
      'b' : soil_data['b'][sample],
      'mn' : soil_data['mn'][sample],
      'no3_n' : soil_data['no3_n'][sample],
    } 


    date = sample_data['samp_date']
    
    start_date = (date - pd.Timedelta(days = 15)).strftime('%Y-%m-%d')
    start_date = ee.Date(start_date)

    end_date = (date + pd.Timedelta(days = 15)).strftime('%Y-%m-%d')
    end_date = ee.Date(end_date)

    lon = sample_data['longitude']
    lat = sample_data['latitude']

    point = ee.Geometry.Point([lon, lat])

    print(f'Processing sample #{sample} at Longitude: {lon}, Latitude: {lat}')

    cloud_filter = ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)

    sentinel2 = (
        ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterBounds(point)
        .filterDate(start_date, end_date)
        .sort('system:time_start', False)
    )

    landsat9_sr = (
        ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
        .filterBounds(point)
        .filterDate(start_date, end_date)
        .sort('system:time_start', False)
    )

    s2_data = sentinel2.first()
    ls9_data = landsat9_sr.first()



    for lsband in ls_bands:
        band_value = ls9_data.select(lsband).reduceRegion(
            reducer = ee.Reducer.mean(),
            geometry = point,
            scale = 10,
            bestEffort = True
        ).get(lsband)

        sample_data[f'ls9_{lsband}'] = band_value.getInfo() if band_value is not None else None
        

    for band in sen_2_bands:
        band_value = s2_data.select(band).reduceRegion(
            reducer = ee.Reducer.mean(),
            geometry = point,
            scale = 10,
            bestEffort = True
        ).get(band)

        sample_data[f's2_{band}'] = band_value.getInfo() if band_value is not None else None
    
    rs_samples = pd.DataFrame([sample_data])

    cov_data = pd.concat([cov_data,rs_samples])


cov_data.to_csv(r'training_data.csv')


end_time = datetime.datetime.now()

delta_time = end_time - start_time

hours, remainder = divmod(delta_time.seconds, 3600)
minutes, seconds = divmod(remainder, 60)



# arcpy.management.CreateLasDataset(
#     input = r"LAS files"
#     out_las_dataset=r"A:\Project_Work\work\main\AEA_Farm\USGS_LPC_IA_North_LasDataset.lasd",
#     folder_recursion="NO_RECURSION",
#     in_surface_constraints=None,
#     spatial_reference='PROJCS["NAD83(2011) / UTM zone 15N (Meters)",GEOGCS["NAD83(2011)",DATUM["NAD83 (National Spatial Reference System 2011",SPHEROID["GRS 1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["false_easting",500000.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-93.0],PARAMETER["scale_factor",0.9996],PARAMETER["latitude_of_origin",0.0],UNIT["metre",1.0]],VERTCS["NAVD88 height - Geoid12B (Meters)",VDATUM["North American Vertical Datum 1988"],PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["metre",1.0]]',
#     compute_stats="COMPUTE_STATS",
#     relative_paths="ABSOLUTE_PATHS",
#     create_las_prj="NO_FILES",
#     extent="DEFAULT",
#     boundary=None,
#     add_only_contained_files="INTERSECTED_FILES"
# )

# arcpy.conversion.LasDatasetToRaster(
#     in_las_dataset="USGS_LPC_IA_North_LasDataset.lasd",
#     out_raster=r"a:\project_work\work\main\aea_farm\initial_aea_farm.gdb\usgs_l_lasda",
#     value_field="ELEVATION",
#     interpolation_type="BINNING AVERAGE LINEAR",
#     data_type="FLOAT",
#     sampling_type="CELLSIZE",
#     sampling_value=10,
#     z_factor=1
# )

print(f'Time elapsed: {(delta_time.days * 24) + hours}:{minutes}:{seconds}')