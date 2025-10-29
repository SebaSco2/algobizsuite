@echo off
setlocal enabledelayedexpansion

echo 🚀 AlgoBizSuite - Odoo 19 with Algorand Payments
echo ================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Error: docker-compose is not installed. Please install Docker Desktop and try again.
        exit /b 1
    )
    set DOCKER_COMPOSE_CMD=docker compose
) else (
    set DOCKER_COMPOSE_CMD=docker-compose
)

echo ✓ Docker is running
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    if exist .env.example (
        copy .env.example .env >nul
        echo ✓ Created .env from .env.example
        echo.
        echo ⚠️  Using default passwords. You should change these in .env for production!
        echo.
    ) else (
        echo ❌ Error: .env.example not found
        exit /b 1
    )
) else (
    echo ✓ .env file exists
)

REM Create docker-compose.yml if it doesn't exist
if not exist docker-compose.yml (
    echo 📝 Creating docker-compose.yml...
    if exist docker-compose.yml.example (
        copy docker-compose.yml.example docker-compose.yml >nul
        echo ✓ Created docker-compose.yml from example
    ) else (
        echo ❌ Error: docker-compose.yml.example not found
        exit /b 1
    )
) else (
    echo ✓ docker-compose.yml exists
)

REM Create etc/odoo.conf if it doesn't exist
if not exist etc\odoo.conf (
    echo 📝 Creating etc/odoo.conf...
    if exist etc\odoo.conf.example (
        copy etc\odoo.conf.example etc\odoo.conf >nul
        echo ✓ Created etc/odoo.conf from example
    ) else (
        echo ❌ Error: etc/odoo.conf.example not found
        exit /b 1
    )
) else (
    echo ✓ etc/odoo.conf exists
)

REM Fix line endings for shell scripts (Windows CRLF to Unix LF)
echo 🔧 Fixing line endings for shell scripts...
if exist entrypoint.sh (
    powershell -Command "(Get-Content entrypoint.sh -Raw) -replace \"`r`n\", \"`n\" | Set-Content entrypoint.sh -NoNewline -Encoding ASCII"
)
if exist install.sh (
    powershell -Command "(Get-Content install.sh -Raw) -replace \"`r`n\", \"`n\" | Set-Content install.sh -NoNewline -Encoding ASCII"
)
echo ✓ Fixed line endings
echo.

echo.
echo 🐳 Starting Docker containers...
echo.

REM Start Docker Compose
%DOCKER_COMPOSE_CMD% up -d

echo.
echo ✅ AlgoBizSuite is starting!
echo.
echo 📊 Container status:
%DOCKER_COMPOSE_CMD% ps
echo.
echo 🌐 Access Odoo at: http://localhost:8069
echo.
echo 📝 Default credentials:
echo    Database: mydb (or create a new one^)
echo    Admin password: admin (change in .env^)
echo.
echo 📖 Next steps:
echo    1. Wait ~60 seconds for services to initialize
echo    2. Open http://localhost:8069 in your browser
echo    3. Database 'mydb' will be created automatically
echo    4. Algorand Pera Payment module will be auto-installed
echo.
echo 💡 Useful commands:
echo    View logs:     %DOCKER_COMPOSE_CMD% logs -f odoo19
echo    Stop services: %DOCKER_COMPOSE_CMD% down
echo    Restart:       %DOCKER_COMPOSE_CMD% restart
echo.
echo 📚 Documentation: see README.md
echo.
echo ⏳ Installing Algorand Pera Payment module...
echo    (This will take about 60 seconds^)
echo.

REM Wait for Odoo to be ready
timeout /t 45 /nobreak >nul

REM Install the algorand_pera_payment module
%DOCKER_COMPOSE_CMD% exec -T odoo19 odoo -c /etc/odoo/odoo.conf -d mydb -i algorand_pera_payment --stop-after-init >nul 2>&1

REM Restart Odoo to ensure everything is loaded
echo 🔄 Restarting Odoo to complete setup...
%DOCKER_COMPOSE_CMD% restart odoo19 >nul 2>&1

timeout /t 10 /nobreak >nul

echo.
echo ✅ Setup complete!
echo 🌐 Odoo is ready at: http://localhost:8069
echo.
echo 📝 Default login:
echo    Email: admin
echo    Password: admin
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🎯 Algorand Pera Payment module is installed!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ⚙️  REQUIRED CONFIGURATION:
echo.
echo 1. Configure your Merchant Algorand Address:
echo    • Navigate to: Website → Configuration → Payment Providers
echo    • Select: 'Algorand Pera Wallet'
echo    • Enter your 58-character Algorand wallet address
echo.
echo 2. Choose your network:
echo    • TestNet (for testing^) - Get free ALGO at: https://bank.testnet.algorand.network/
echo    • MainNet (for production^)
echo.
echo 3. For USD payments via USDC:
echo    • Your merchant wallet MUST be opted-in to USDC
echo    • Click 'Check USDC Opt-in Status' in the provider settings
echo    • ALGO payments work without USDC opt-in
echo.
echo 📖 Full configuration guide:
echo    addons\algorand_pera_payment\readme\CONFIGURE.md
echo.
echo 💡 Quick links:
echo    • Installation: addons\algorand_pera_payment\readme\INSTALL.md
echo    • Usage Guide:  addons\algorand_pera_payment\readme\USAGE.md
echo.

endlocal

