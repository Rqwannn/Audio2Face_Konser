## Download Model AI (Wajib)

Repository ini tidak menyertakan file model AI (seperti GFPGAN, Weights, Detection Model) karena ukurannya yang sangat besar (>100MB). Tanpa file ini, aplikasi akan error.

Silakan jalankan script otomatis di bawah ini untuk mengunduh dan menyusun folder `assets` & `core` secara otomatis.

### Mac / Linux
Buka terminal di folder project, lalu jalankan perintah berikut:

```bash
# 1. Berikan izin eksekusi pada file script
chmod +x setup_models.sh

# 2. Jalankan script
./setup_models.sh
```

### Windows
Buka terminal di folder project, lalu jalankan perintah berikut:

```bash
setup_models.bat
```

## Izinkan akses folder data

```
sudo chmod -R 777 data/
```