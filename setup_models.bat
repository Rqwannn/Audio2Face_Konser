@echo off
setlocal enabledelayedexpansion

echo [INIT] Memeriksa dependency gdown...
pip install gdown --quiet

echo [INIT] Memulai proses download...

call :DownloadAndExtract 1f4s3wgTOd6BMkEYkBEjMDqVjcyBDYszG inswapper_128.zip
call :DownloadAndExtract 1b_iZJ8TMgDuOS4n24OQAOdmIhmOFjmF2 buffalo_l.zip
call :DownloadAndExtract 15kKcf3QJyQXXOr0EkD5N9J8owCX840IK pretrained_weights.zip

echo.
echo [DONE] Semua selesai!
pause
exit /b

:DownloadAndExtract
set "FILE_ID=%~1"
set "FILENAME=%~2"

echo.
echo -----------------------------------------------------
echo [PROCESS] Sedang memproses: %FILENAME%
echo -----------------------------------------------------

if exist "%FILENAME%" del "%FILENAME%"

echo [DOWNLOAD] Mengambil file dari Google Drive...
gdown --id %FILE_ID% -O %FILENAME%

if exist "%FILENAME%" (
    set "TARGET_DIR=assets\models"
    echo "%FILENAME%" | findstr "pretrained_weights" >nul && set "TARGET_DIR=core"
    echo "%FILENAME%" | findstr "buffalo_l" >nul && set "TARGET_DIR=assets\models\buffalo_l"

    echo [CONFIG] Target folder: !TARGET_DIR!

    if not exist "!TARGET_DIR!" mkdir "!TARGET_DIR!"
    
    echo [EXTRACT] Sedang mengekstrak archive...
    tar -xf "%FILENAME%" -C "!TARGET_DIR!"
    
    del "%FILENAME%"
    echo [SUCCESS] %FILENAME% berhasil dipasang.
) else (
    echo [ERROR] Gagal mendownload %FILENAME%.
)
exit /b