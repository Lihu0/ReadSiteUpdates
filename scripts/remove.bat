@echo off
:: Check if the task exists
schtasks /Query /TN "ReadSiteUpdates" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Task "ReadSiteUpdates" exists. Deleting...
    schtasks /Delete /TN "ReadSiteUpdates" /F
    echo Task deleted.
) else (
    echo Task "ReadSiteUpdates" does not exist.
)
pause
