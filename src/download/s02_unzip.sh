#!/bin/bash

# ZIPファイルが保存されている親ディレクトリ
zip_dir="/home/ykojima/ykojima/GFM_data/data/download_exclusion_zip"  # ZIPファイルがあるディレクトリを指定
out_home_dir="/home/ykojima/ykojima/GFM_data/data/download_exclusion"

# ZIPファイルを順番に処理
for zip_file in "$zip_dir"/*.zip.zip; do
    # .zipを除いたファイル名を取得
    base_name=$(basename $(basename "$zip_file" .zip) .zip)
    
    # ZIPファイルと同じ名前のディレクトリを作成
    if [-f "$out_home_dir/$output_dir"]; then
        echo "already unzipped ${output_dir}"
    else
        output_dir="$base_name"
        mkdir -p "$out_home_dir/$output_dir"
        
        # ZIPファイルを指定したディレクトリに解凍
        unzip "$zip_file" -d "$out_home_dir/$output_dir"
        
        echo "$zip_file を "$out_home_dir/$output_dir" に解凍しました。"
    fi
done

echo "すべてのZIPファイルが解凍されました。"
