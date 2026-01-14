#!/bin/bash

rm -f models.zip

echo "Downloading models..."
gdown --id 1aeOk-yyCBbS8e-KzeAgv_aIaxUC2GHMX -O inswapper_128.zip

if [ -f "models.zip" ]; then
    echo "Download selesai. Mengekstrak..."
    
    TARGET_DIR="assets"
    mkdir -p "$TARGET_DIR"
    
    unzip -o models.zip -d "$TARGET_DIR"
    rm models.zip
    
    echo "Selesai! Model tersimpan di folder '$TARGET_DIR'."
else
    echo "Gagal mendownload models.zip"
fi