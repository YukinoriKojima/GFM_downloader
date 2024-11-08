import matplotlib.pyplot as plt
import rasterio
from rasterio.mask import mask
import numpy as np
from shapely.geometry import box
from rasterio.warp import reproject, Resampling
from datetime import datetime, timedelta
import os

## * ======================
## * Parameter Setting

# GeoTIFFファイルのパスリスト
start_day = datetime(2022, 8, 6)
days = [start_day+timedelta(days=12)*i for i in range(0, 13)]
yyyymmdds = [day.strftime('%Y-%m-%d') for day in days]
tiff_files = [f'/work/a06/ykojima/GFM_data/data/merged_by_day/{yyyymmdd}.tif'
              for yyyymmdd in yyyymmdds]  # 各自のファイルパスに置き換えてください
cama_tiff_dir = "/work/a06/ykojima/convert_binary_to_tiff/out/flood_pakistan_01min_openloop_nobif"
outdir = '/work/a06/ykojima/GFM_data/src/visualize/ol_with_cama'

# 南北東西の端を定義 (例: xmin, ymin, xmax, ymax)
xmin, ymin, xmax, ymax = 67.0, 26.0, 69.5, 28.5  # 必要に応じて変更

# number of columns 
n_col:int = 4
## * ======================

n_row = (len(tiff_files)//n_col) + 1

# サブプロットの準備 (例: 1行3列)
aoi = [box(xmin, ymin, xmax, ymax)]

# 各GeoTIFFファイルを順番に読み込み、指定された範囲内をクリッピングしてサブプロットに表示
for i, file in enumerate(tiff_files):
    print(file)
    if os.path.exists(file) == False:
        continue
    
    with rasterio.open(file) as src:
        # 指定範囲内のウィンドウを取得
        clipped_src, clipped_src_transform = mask(src, aoi, crop=True)

        # ウィンドウ内のデータを読み込み
        data = clipped_src[0].astype(np.float32)
        data[data == 0] = np.nan  # 0の値を透明化
        data[data == 255] = np.nan  # 255の値を透明化

        # 背景地図を読み込み
        cama_tiff_path = cama_tiff_dir + "/flood_" + days[i].strftime('%Y%m%d') + ".tif"
        with rasterio.open(cama_tiff_path) as bg_src:
            # 背景地図をdataの解像度にリサンプリング
            out_shape = (data.shape[0], data.shape[1])  # データの解像度に合わせた出力形状
            resampled_bg = np.empty(out_shape, dtype=np.float32)

            reproject(
                source=rasterio.band(bg_src, 2),  # CaMaシミュレーション結果のバンドを使用
                destination=resampled_bg,
                src_transform=bg_src.transform,
                src_crs=bg_src.crs,
                dst_transform=clipped_src_transform,
                dst_crs=src.crs,
                resampling=Resampling.bilinear  # リサンプリングの方法。ここではバイリニア補間を使用
            )

            # リサンプリング後の背景地図の範囲を取得
            bg_resampled_extent = rasterio.transform.array_bounds(out_shape[0], out_shape[1], clipped_src_transform)
            resampled_bg = np.where(resampled_bg!=0.0, 1.0, np.nan)
            # 背景地図を描画 (リサンプリングされたもの)
            plt.imshow(resampled_bg, cmap='Blues', extent=bg_resampled_extent, vmin=0, vmax=1, alpha=0.5)

        # 描画データの範囲を取得 (xmin, xmax, ymin, ymax)
        data_extent = rasterio.transform.array_bounds(data.shape[0], data.shape[1], clipped_src_transform)

        # サブプロットにクリップされたデータを重ねて描画 (extentを使って座標を揃える)
        plt.imshow(data, cmap='Reds', vmin=0, vmax=1, extent=data_extent)
        yyyymmdd = yyyymmdds[i]
        plt.title(yyyymmdd)
        plt.gca().axis('off')  # 軸を非表示にする
        plt.tight_layout()
        plt.savefig(outdir+f'/{yyyymmdd}.png', dpi=1000)
        plt.close()
        print(f'Done : {yyyymmdd}')

