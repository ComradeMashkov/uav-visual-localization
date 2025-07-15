@echo off
cd /d %~dp0

set "DROPBOX_URL=https://www.dropbox.com/scl/fi/8m8ujy9z0xzdgnbllqhgo/images.zip?rlkey=r2qz07uddvolmazae9i4lmxae&st=ru1fyb79&dl=1"
set "ZIP_NAME=images.zip"
set "TARGET_DIR=labeled"

if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo.
echo Downloading dataset from Dropbox...
powershell -Command ^
    "$ProgressPreference = 'SilentlyContinue';" ^
    "(New-Object System.Net.WebClient).DownloadFile('%DROPBOX_URL%', '%ZIP_NAME%')"

if not exist "%ZIP_NAME%" (
    echo Error: Failed to download dataset.
    pause
    exit /b 1
)

echo.
echo Extracting dataset...
powershell -Command ^
    "Expand-Archive -Path '%ZIP_NAME%' -DestinationPath '.\%TARGET_DIR%' -Force"

echo.
echo Removing archive...
del "%ZIP_NAME%"

echo.
echo Done! Folders named images and labels are now in %TARGET_DIR%.
pause