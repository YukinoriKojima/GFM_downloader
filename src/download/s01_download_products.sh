#!/bin/bash

# **Params
# ! Please first make your account and AOI
# 1. confidential
EMAIL="your@email.com"
PASSWORD="your_password"

# 2. Area of Your Interest & Layer You Want
AOI_NAME="pakistan"
LAYER_NUMBER="4"

# 3. Date(GMT)
YSTA=2022
MSTA=08
DSTA=01
HSTA=00
YEND=2023
MEND=03
DEND=01
HEND=00

# 4. Output absolute directry
# ! Please assign non-existing directry
# ! the directory will be removed and recreated in the main pipeline
download_dir="/home/ykojima/ykojima/GFM_data/data/download_exclusion_zip"

# **


mkdir -p $download_dir
# Authenticatio

AUTH_INFO=$(curl -s -X 'POST' \
  'https://api.gfm.eodc.eu/v2/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d "{
  "email": "${EMAIL}", #!
  "password": "${PASSWORD}"}" ) #!

# アクセストークンを抽出
ACCESS_TOKEN=$(echo "$AUTH_INFO" | grep -o '"access_token": *"[^"]*"' | sed 's/"access_token": "//' | sed 's/"//')
USER_ID=$(echo "$AUTH_INFO" | grep -o '"client_id": *"[^"]*"' | sed 's/"client_id": "//' | sed 's/"//')

# アクセストークンを表示
echo "Access Token: $ACCESS_TOKEN"
echo "User ID: $USER_ID"

# AOI一覧を取得
AOI_RESPONSE=$(curl -s -X 'GET' \
  "https://api.gfm.eodc.eu/v2/aoi/user/$USER_ID" \
  -H "accept: application/json" \
  -H "Authorization: bearer $ACCESS_TOKEN")

# AOI_IDを抽出
AOI_ID=$(echo "$AOI_RESPONSE" | awk -v RS='{' '/"aoi_name": "'$AOI_NAME'"/ {print $0}' | grep -o '"aoi_id": *"[^"]*"' | sed 's/"aoi_id": "//' | sed 's/"//')

# AOI_IDを表示
echo "AOI ID for $AOI_NAME: $AOI_ID"

# プロダクト一覧を取得
PRODUCT_RESPONSE=$(curl -s -X 'GET' \
  "https://api.gfm.eodc.eu/v1/aoi/$AOI_ID/products?time=range&from=$YSTA-$MSTA-$DSTA"T"$HSTA%3A00%3A00&to=$YEND-$MEND-$DEND"T"$HEND%3A00%3A00" \
  -H 'accept: application/json' \
  -H "Authorization: bearer $ACCESS_TOKEN")

# PRODUCT_RESPONSEをファイルに保存
echo "$PRODUCT_RESPONSE" > products.json

# JSONデータからcell_codeを抽出し、それぞれに対して操作を実行
grep -o '"cell_code": *"[^"]*"' products.json | sed 's/"cell_code": "//' | sed 's/"//' | while read -r cell_code; do
    # cell_code を出力
    echo "Processing cell_code: $cell_code"

    # cell_codeが"S1A"で始まるかを確認
    if [[ $cell_code == S1A* ]]; then
        response=$(curl -s -X 'GET' \
            "https://api.gfm.eodc.eu/v2/download/scene-file/$cell_code/$AOI_ID/$LAYER_NUMBER" \
            -H 'accept: application/json' \
            -H "Authorization: bearer $ACCESS_TOKEN")
        
        # ダウンロードリンクを抽出
        download_link=$(echo "$response" | grep -o '"download_link": *"[^"]*"' | sed 's/"download_link": "//' | sed 's/"//')
        echo "Download link: $download_link"

        # ヘッダーからファイル名を取得
        filename=$(curl -sI "$download_link" | grep -o 'filename="[^"]*"' | sed 's/filename="//' | sed 's/"//')
        echo "File name from header: $filename"

        # ファイル名が取得できない場合、リンクの一部を使う
        if [ -z "$filename" ]; then
            filename=$(echo "$download_link" | sed -n 's#.*/s/\([^/]*\)/download.*#\1#p')
            echo "Defaulting to extracted file name: $filename"
        fi

        # ダウンロードファイルが既に存在するか確認
        if [ -f "$download_dir/$filename" ]; then
            echo "File $filename already exists, skipping download..."
        else
            # ZIPファイルをダウンロード
            curl -L "$download_link" --output "$download_dir/$filename.zip"
            echo "Downloaded file from $download_link to $filename"
        fi

        # # ZIPファイルを解凍し、既に解凍済みか確認
        # unzip_dir="$download_dir/${filename%.zip}"
        # if [ -d "$unzip_dir" ]; then
        #     echo "Directory $unzip_dir already exists, skipping extraction..."
        # else
        #     # 解凍処理
        #     unzip "$download_dir/$filename" -d "$unzip_dir"
        #     echo "Extracted $filename to $unzip_dir"
        # fi
    fi
done
