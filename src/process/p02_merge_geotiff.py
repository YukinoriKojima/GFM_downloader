from datetime import datetime, timedelta
import glob
from pathlib import Path
import rasterio
from rasterio.merge import merge
import subprocess
from multiprocessing import Process

# ** ====================
# ** Parameters
YSTA = 2023
MSTA = 2
DSTA = 1
YEND = 2023
MEND = 5
DEND = 1
DATA_ROOT_DIR       = Path('/work/a06/ykojima/GFM_data/data/download_flood_3_zip')
OUTPUT_ROOT_DIR     = Path('/work/a06/ykojima/GFM_data/data/merged_by_day_flood_3')
#!! WARNING : this code REMOVES output directory and make it, 
#!! thus please change output dir to avoid deleting data already processed.
DATA_DIR_PREFIX     = 'pakistan_'
MULTIPROCESSMODE    = False
# ** ====================

def merge_tifs(tiff_files:list, output_path:str):
    # TIFFファイルを開く
    src_files_to_mosaic = []
    
    for tiff in tiff_files:
        src = rasterio.open(tiff)
        src_files_to_mosaic.append(src)

    # 重複部分の処理として、最大値を選択
    try:
        mosaic, out_trans = merge(src_files_to_mosaic, method='first')
    except rasterio.errors.WindowError: #! tentative dealing with WindowError
        print(f'Failed : {output_path}')
        return

    # 結合したTIFFを保存
    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=mosaic.shape[1],
        width=mosaic.shape[2],
        count=1,
        dtype=mosaic.dtype,
        crs=src_files_to_mosaic[0].crs,
        transform=out_trans,
    ) as dest:
        dest.write(mosaic)

    # すべてのファイルを閉じる
    for src in src_files_to_mosaic:
        src.close()
        
    if False: 
        import matplotlib.pyplot as plt

        # GeoTIFFファイルを開く
        with rasterio.open(output_path) as src:
            # データを読み込む
            tiff_data = src.read(1)  # バンド1を読み込み
            
            # プロット
            plt.figure(figsize=(10, 10))
            plt.imshow(tiff_data, cmap='terrain')  # カラーマップを変更可能
            plt.colorbar(label='Elevation (m)')
            plt.title('DEM Mosaic')
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')
            
            # プロットを画像として保存
            plt.savefig('./dem_mosaic_plot.png', dpi=300)  # 高解像度で保存

subprocess.run(f'rm -rf {OUTPUT_ROOT_DIR}', shell=True)
subprocess.run(f'mkdir -p {OUTPUT_ROOT_DIR}', shell=True)

cday = datetime(YSTA, MSTA, DSTA)

processes = []

while cday <= datetime(YEND, MEND, DEND):
    
    yyyymmdd = cday.strftime('%Y-%m-%d')
    print(yyyymmdd)
    tiff_list = glob.glob(str(DATA_ROOT_DIR / Path(f'{DATA_DIR_PREFIX}{yyyymmdd}*') / Path('*.tif')))
    
    if len(tiff_list) == 0:
        cday += timedelta(days=1)
        print('No Data!')
        continue
    else:
        print('Number of Data : ', len(tiff_list))
    
    if MULTIPROCESSMODE:
        p = Process(target=merge_tifs, args=(tiff_list, Path(OUTPUT_ROOT_DIR)/Path(f'{yyyymmdd}.tif')))
        p.start()
        processes.append(p)
        
    else:
        merge_tifs(tiff_list, Path(OUTPUT_ROOT_DIR)/Path(f'{yyyymmdd}.tif'))
    
    cday += timedelta(days=1)
    
if MULTIPROCESSMODE:
    for p in processes:
        p.join()