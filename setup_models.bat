@echo off
setlocal

echo [1/3] Memeriksa instalasi gdown...
pip install gdown --quiet

if exist inswapper_128.zip del inswapper_128.zip

echo.
echo [2/3] Mendownload Model AI (Size Besar)...
echo Mohon tunggu, proses download sedang berjalan...
gdown --id 1aeOk-yyCBbS8e-KzeAgv_aIaxUC2GHMX -O inswapper_128.zip

if exist inswapper_128.zip (
    echo.
    echo [3/3] Download selesai. Mengekstrak file...
    
    if not exist "assets" mkdir "assets"
    
    tar -xf inswapper_128.zip -C assets
    
    del inswapper_128.zip
    
    echo.
    echo ==============================================
    echo SUKSES! Model berhasil disimpan di folder 'assets'
    echo ==============================================
) else (
    echo.
    echo [ERROR] Gagal mendownload models.zip.
    echo Pastikan internet terhubung dan python/pip sudah terinstall.
)

pause