import rasterio
from rasterio.mask import mask
from shapely.geometry import box
import os
import glob

# ** Parameter
INPDIR="/work/a06/ykojima/GFM_data/data/merged_by_day"
OUT_DIRNAME="merged_by_day_regionalized"
NORTH=30
SOUTH=26
EAST=67
WEST=70

def clip_geotiff(input_tif, output_tif, west, south, east, north):
    # 範囲をポリゴンで指定
    print(input_tif)
    bbox = box(west, south, east, north)
    geojson_bbox = [bbox.__geo_interface__]  # mask 関数のためにGeoJSON形式に変換

    with rasterio.open(input_tif) as src:
        # `nodata` 値を 255 に設定
        src_nodata = src.nodata if src.nodata is not None else 255
        
        try:
            # マスク処理 (範囲外の部分を切り抜き)c
            out_image, out_transform = mask(src, geojson_bbox, crop=True, nodata=src_nodata)
            
            # データが全て `nodata` の場合、出力しない
            if (out_image == src_nodata).all():
                print("指定範囲内に有効なデータがありません。出力ファイルを生成しません。")
                return
            
            # 出力するGeoTIFFファイルを作成
            out_meta = src.meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
                "nodata": src_nodata
            })

            # ファイルに書き込む
            with rasterio.open(output_tif, "w", **out_meta) as dest:
                dest.write(out_image)
                
            print(f"{output_tif} に切り抜き保存しました。")

        except ValueError:
            print("指定された範囲に有効なデータが見つかりませんでした。出力ファイルを生成しません。")

# 使用例
original_tifs = glob.glob(f'{INPDIR}/*.tif')

os.makedirs(f'/work/a06/ykojima/GFM_data/data/{OUT_DIRNAME}', exist_ok=True)

for tif in original_tifs:
    outpath = f'/work/a06/ykojima/GFM_data/data/{OUT_DIRNAME}/{os.path.basename(tif)}'
    clip_geotiff(tif, outpath, WEST, SOUTH, EAST, NORTH)
