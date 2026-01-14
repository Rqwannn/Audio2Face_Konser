#!/bin/bash

# --- KONFIGURASI ---
TARGET_DIR="assets/models"
mkdir -p "$TARGET_DIR"

FILES=(
    "1f4s3wgTOd6BMkEYkBEjMDqVjcyBDYszG:inswapper_128.zip"
    "1b_iZJ8TMgDuOS4n24OQAOdmIhmOFjmF2:buffalo_l.zip" 
)
# -------------------

echo "Memulai proses download..."

for entry in "${FILES[@]}"; do
    FILE_ID="${entry%%:*}"
    FILENAME="${entry##*:}"

    echo "----------------------------------------"
    echo "Processing: $FILENAME"
    
    rm -f "$FILENAME"

    echo "Downloading..."
    gdown --id "$FILE_ID" -O "$FILENAME"

    if [ -f "$FILENAME" ]; then
        echo "Download sukses. Mengekstrak ke $TARGET_DIR..."

        if [[ "$FILENAME" == *"buffalo_l"* ]]; then
            TARGET_DIR="assets/models/buffalo_l"
        fi
        
        unzip -o "$FILENAME" -d "$TARGET_DIR"
        
        rm "$FILENAME"
        echo "Selesai memproses $FILENAME."
    else
        echo "[ERROR] Gagal mendownload $FILENAME. Cek ID Google Drive."
    fi
done

echo "----------------------------------------"
echo "Semua proses selesai!"