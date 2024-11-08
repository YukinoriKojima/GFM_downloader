# ! not using now!!!!

import numpy as np
import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape
import glob
import os, sys
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from multiprocessing import Pool

# ! not using now!!!!

args = sys.argv[1:]
ysta, msta, dsta = int(args[0]), int(args[1]), int(args[2])
yend, mend, dend = int(args[3]), int(args[4]), int(args[5])
tiff_home_dir = str(args[6])
output_home_dir = str(args[7])
aoi_name = str(args[8])

def process_1day_tiff(date: datetime):
    yyyymmdd = date.strftime('%Y-%m-%d')
    print(f'Process Started : {yyyymmdd}')
    
    # TIFFファイルのパスリストを指定
    tiff_files = glob.glob(f'{tiff_home_dir}/{aoi_name}_{yyyymmdd}*/*.tif')
    if len(tiff_files) == 0:
        print(f'Process Done : {yyyymmdd}')
        return
    
    output_dir = f'{output_home_dir}/{yyyymmdd}'
    os.makedirs(output_dir, exist_ok=True)
    output_name = f'{yyyymmdd}.shp'

    if os.path.exists(f'{output_dir}/{output_name}'):
        print(f'Process Done : {yyyymmdd}')
        return
    
    gdf_list = []

    for idx, tiff_file in enumerate(tiff_files):
        with rasterio.open(tiff_file) as src:
            data = src.read(1)

            # 1の部分を残し、0をNaNに変換
            mask = data == 1

            # dataをshapefileに変換
            results = (
                {'properties': {'raster_val': v}, 'geometry': shape(s)}
                for i, (s, v) in enumerate(
                    shapes(data, mask=mask, transform=src.transform)))

            # GeoDataFrameを作成
            gdf = gpd.GeoDataFrame.from_features(list(results))
            gdf_list.append(gdf)

    # すべてのGeoDataFrameを結合
    combined_gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))

    # ジオメトリを1つにまとめる
    merged_geometry = combined_gdf.unary_union

    # 新しいGeoDataFrameにまとめたジオメトリを格納し、EPSG:4326を指定
    combined_gdf = gpd.GeoDataFrame(geometry=[merged_geometry], crs='EPSG:4326')

    # Shapefile形式で保存
    combined_gdf.to_file(f'{output_dir}/{output_name}', driver='ESRI Shapefile')

    
    print(f'Process Done : {yyyymmdd}')
    
    return


current_date = datetime(ysta, msta, dsta)
end_date = datetime(yend, mend, dend)
print(f'Start Date : {current_date}')
print(f'End Date : {end_date}')

os.makedirs(output_home_dir, exist_ok=True)

date_list = [current_date + timedelta(days=i) for i in range((end_date - current_date).days + 1)]
with Pool(processes=8) as pool:
    pool.map(process_1day_tiff, date_list)
