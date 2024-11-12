#!/bin/bash

# ! not using now!!!!
YSTA=2022
MSTA=08
DSTA=15
YEND=2022
MEND=10
DEND=15

TIFF_HOME_DIR='/work/a06/ykojima/GFM_data/data/download_20240908'
OUTPUT_HOME_DIR='/work/a06/ykojima/GFM_data/data/shp'
AOI_NAME='pakistan'

python /work/a06/ykojima/GFM_data/src/process/p01_process_tif.py $YSTA $MSTA $DSTA $YEND $MEND $DEND $TIFF_HOME_DIR $OUTPUT_HOME_DIR $AOI_NAME
