@echo off
echo ========================================
echo   PixelTraivo YT Downloader - Windows
echo ========================================
echo.

REM ========== CLEANUP ==========
echo [1/5] Cleaning up...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.exe del /q *.exe
echo Done.
echo.

REM ========== SETUP ENVIRONMENT ==========
echo [2/5] Setting up environment...
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q pyinstaller
echo Done.
echo.

REM ========== INSTALL FFMPEG ==========
echo [3/5] Checking ffmpeg...

where ffmpeg >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ffmpeg not found, downloading...
    
    REM Download ffmpeg
    curl -L https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip -o ffmpeg.zip
    
    REM Extract
    tar -xf ffmpeg.zip
    
    REM Move binaries
    move ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe .
    move ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe .
    
    REM Cleanup
    rmdir /s /q ffmpeg-master-latest-win64-gpl
    del ffmpeg.zip
    
    set FFMPEG_PATH=ffmpeg.exe
    set FFPROBE_PATH=ffprobe.exe
) else (
    echo ffmpeg found in PATH
    for /f "delims=" %%i in ('where ffmpeg') do set FFMPEG_PATH=%%i
    for /f "delims=" %%i in ('where ffprobe') do set FFPROBE_PATH=%%i
)

echo ffmpeg: %FFMPEG_PATH%
echo ffprobe: %FFPROBE_PATH%
echo Done.
echo.

REM ========== CHECK ICON ==========
echo [4/5] Checking icon...
if exist assets\icon.ico (
    echo Icon found: assets\icon.ico
    set ICON_ARG=--icon=assets\icon.ico
) else (
    echo Warning: icon.ico not found
    set ICON_ARG=
)
echo.

REM ========== BUILD EXE ==========
echo [5/5] Building Windows executable...

pyinstaller ^
    --name="PixelTraivo-YT-Downloader" ^
    --windowed ^
    --onefile ^
    --noconfirm ^
    --clean ^
    %ICON_ARG% ^
    --add-binary="%FFMPEG_PATH%;." ^
    --add-binary="%FFPROBE_PATH%;." ^
    --add-data="assets;assets" ^
    --hidden-import=yt_dlp ^
    --hidden-import=tkinter ^
    main.py

if exist dist\PixelTraivo-YT-Downloader.exe (
    echo.
    echo ========================================
    echo   BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable: dist\PixelTraivo-YT-Downloader.exe
    echo.
    dir dist\PixelTraivo-YT-Downloader.exe
    echo.
    echo Test: dist\PixelTraivo-YT-Downloader.exe
    echo.
) else (
    echo.
    echo ========================================
    echo   BUILD FAILED!
    echo ========================================
    echo.
)

pause