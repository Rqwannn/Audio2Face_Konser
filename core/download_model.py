from huggingface_hub import snapshot_download
import os

print("⏳ Sedang mendownload Model Utama (EchoMimic)... (Ini akan memakan waktu lama)")
snapshot_download(
    repo_id="BadToBest/EchoMimicV2",
    local_dir="./pretrained_weights",
    local_dir_use_symlinks=False
)

print("✅ Download Selesai!")