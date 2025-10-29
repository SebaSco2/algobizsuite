@echo off
echo Fixing line endings for shell scripts...
echo.

REM Check if dos2unix is available (from Git for Windows or WSL)
where dos2unix >nul 2>&1
if errorlevel 1 (
    echo Using PowerShell to fix line endings...
    powershell -Command "(Get-Content entrypoint.sh -Raw) -replace \"`r`n\", \"`n\" | Set-Content entrypoint.sh -NoNewline -Encoding ASCII"
    powershell -Command "(Get-Content install.sh -Raw) -replace \"`r`n\", \"`n\" | Set-Content install.sh -NoNewline -Encoding ASCII"
    echo ✓ Fixed entrypoint.sh and install.sh line endings
) else (
    echo Using dos2unix...
    dos2unix entrypoint.sh install.sh >nul 2>&1
    echo ✓ Fixed entrypoint.sh and install.sh line endings
)

echo.
echo Line endings have been fixed. You can now restart Docker containers:
echo   docker-compose down
echo   docker-compose up -d
echo.

