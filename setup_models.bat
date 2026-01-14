@echo off
setlocal enabledelayedexpansion

echo [1/2] Memeriksa instalasi gdown...
pip install gdown --quiet

REM --- KONFIGURASI FOLDER TUJUAN ---
set "TARGET_DIR=assets/models"
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo.
echo [2/2] Memulai Loop Download...

REM ============================================================
REM DAFTAR FILE YANG AKAN DIDOWNLOAD
REM Format: call :DownloadAndExtract [GDRIVE_ID] [NAMA_FILE.zip]
REM ============================================================

call :DownloadAndExtract 1f4s3wgTOd6BMkEYkBEjMDqVjcyBDYszG inswapper_128.zip
call :DownloadAndExtract 1b_iZJ8TMgDuOS4n24OQAOdmIhmOFjmF2 buffalo_l.zip"

REM ============================================================

echo.
echo ==============================================
echo SEMUA PROSES SELESAI!
echo ==============================================
pause
exit /b

REM --- FUNGSI DOWNLOADER (JANGAN DIUBAH DI BAWAH INI) ---
:DownloadAndExtract
set "FILE_ID=%~1"
set "FILENAME=%~2"

echo.
echo ----------------------------------------------
echo Sedang memproses: %FILENAME%...
echo ----------------------------------------------

if exist "%FILENAME%" del "%FILENAME%"

gdown --id %FILE_ID% -O %FILENAME%

if exist "%FILENAME%" (
    echo Mengekstrak file...
    REM Menggunakan tar karena bawaan Windows 10/11
    
    echo !FNAME! | findstr /C:"buffalo_l" >nul
        
    if not errorlevel 1 (
        set "TARGET_DIR=assets/models/buffalo_l"
    )

    tar -xf "%FILENAME%" -C "%TARGET_DIR%"
    
    del "%FILENAME%"
    echo [OK] Berhasil diproses ke folder '%TARGET_DIR%'.
) else (
    echo [ERROR] Gagal mendownload %FILENAME%.
)
exit /b