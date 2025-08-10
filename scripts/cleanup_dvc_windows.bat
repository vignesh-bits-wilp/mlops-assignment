@echo off
echo Cleaning up DVC cache for Windows compatibility...
echo ================================================

REM Remove DVC cache directories that cause Windows filename issues
if exist ".dvc\cache" (
    echo Removing .dvc\cache directory...
    rmdir /s /q ".dvc\cache"
)

if exist ".dvc\tmp" (
    echo Removing .dvc\tmp directory...
    rmdir /s /q ".dvc\tmp"
)

if exist ".dvc\state" (
    echo Removing .dvc\state directory...
    rmdir /s /q ".dvc\state"
)

if exist ".dvc\state-journal" (
    echo Removing .dvc\state-journal directory...
    rmdir /s /q ".dvc\state-journal"
)

REM Remove any temporary DVC files
for /f "delims=" %%i in ('dir /b /s *.dvc-tmp 2^>nul') do (
    echo Removing temporary file: %%i
    del "%%i"
)

for /f "delims=" %%i in ('dir /b /s *.dvc-cache 2^>nul') do (
    echo Removing cache file: %%i
    del "%%i"
)

echo.
echo DVC cache cleanup completed!
echo.
echo Next steps:
echo 1. Run: git add .
echo 2. Run: git commit -m "Clean up DVC cache for Windows compatibility"
echo 3. Run: dvc pull (to re-download data if needed)
echo.
pause 