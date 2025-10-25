@echo off
setlocal enabledelayedexpansion

:: --- INI settings ---
set "iniFile=..\settings.ini"
set "section=[scheduler]"
set "inSection=false"

for /f "usebackq tokens=* delims=" %%A in ("%iniFile%") do (
    set "line=%%A"
    set "line=!line: =!"

    if /i "!line!"=="%section%" (
        set "inSection=true"
    ) else (
        if "!line:~0,1!"=="[" (
            set "inSection=false"
        )
    )

    if "!inSection!"=="true" (
        if /i not "!line!"=="%section%" (
            for /f "tokens=1,2 delims==" %%B in ("!line!") do (
                if /i "%%B"=="start_time" set "start_time=%%C"
                if /i "%%B"=="interval" set "interval=%%C"
                if /i "%%B"=="script_to_execute" set "script_to_execute=%%C"
            )
        )
    )
)

:: --- Convert interval to minutes ---
for /f "delims=" %%m in ('powershell -NoProfile -Command "$s='%interval%'; if($s -match '^\s*([0-9]*\.?[0-9]+)\s*([hmdHMD])\s*$'){ $v=[double]$matches[1]; switch($matches[2].ToLower()){ 'm'{$r=$v}; 'h'{$r=$v*60}; 'd'{$r=$v*24*60} }; Write-Output $r } else { Write-Output 'invalid' }"') do set "minutes=%%m"

:: --- Resolve absolute script path ---
for %%I in ("%~dp0%script_to_execute%") do set "abs_script=%%~fI"

set "current_dir=%cd%"

for %%I in ("%current_dir%\%script_to_execute%") do set "script_folder=%%~dpI"

if "%script_folder:~-1%"=="\" set "script_folder=%script_folder:~0,-1%"

for %%I in ("%script_folder%\..") do set "script_folder=%%~fI"

if "%script_folder:~-1%"=="\" set "script_folder=%script_folder:~0,-1%"

:: --- Set full command to run in correct folder ---
set "full_command=cd /d !script_folder! & !script_to_execute!"

:: extract just the script name (filename + extension)
for %%J in ("!script_to_execute!") do set "script_name=%%~nxJ"

:: --- Debug output ---
echo Start Time: %start_time%
echo Full Command: !full_command!
echo Interval (minutes): %minutes%

:: --- Create scheduled task (hidden) ---

if %minutes% GEQ 1440 (
    set /a days=%minutes% / 1440
    rem Daily schedule every !days! days
    schtasks /Create /SC DAILY /MO !days! /ST %start_time% /TN "ReadSiteUpdates" /TR "powershell -NoProfile -WindowStyle Hidden -Command \"Set-Location -LiteralPath '!script_folder!'; Start-Process -FilePath '!script_name!' -WorkingDirectory '!script_folder!' -WindowStyle Hidden\"" /RU "%USERNAME%" /RL LIMITED /F
) else (
    rem Minute-based schedule
    schtasks /Create /SC MINUTE /MO %minutes% /ST %start_time% /TN "ReadSiteUpdates" /TR "powershell -NoProfile -WindowStyle Hidden -Command \"Set-Location -LiteralPath '!script_folder!'; Start-Process -FilePath '!script_name!' -WorkingDirectory '!script_folder!' -WindowStyle Hidden\"" /RU "%USERNAME%" /RL LIMITED /F
)

endlocal
pause
