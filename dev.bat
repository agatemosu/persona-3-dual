@echo off

where wt >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Windows Terminal is not installed.
    echo Install it from: https://aka.ms/terminal
    pause
    exit /b 1
)

where wsl >nul 2>&1
if errorlevel 1 (
    echo [ERROR] WSL is not installed. Run: wsl --install
    pause
    exit /b 1
)

set "PROJECT_WIN=%~dp0"
if "%PROJECT_WIN:~-1%"=="\" set "PROJECT_WIN=%PROJECT_WIN:~0,-1%"

:: Convert Windows path to a WSL-compatible path
for /f "delims=" %%P in ('wsl wslpath "%PROJECT_WIN:\=/%"') do set "PROJECT_WSL=%%P"

:: Copy setup script from the project folder into /tmp and run it
wsl cp "%PROJECT_WSL%/dev_setup.sh" "/tmp/dev_setup.sh"
wsl chmod +x "/tmp/dev_setup.sh"

:: Launch Windows Terminal, passing the WSL project path as an argument
wt new-tab --profile "Ubuntu" -- wsl -e bash /tmp/dev_setup.sh "%PROJECT_WSL%"
