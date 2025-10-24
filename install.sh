#!/bin/bash

set -e

echo "🚀 AlgoBizSuite - Odoo 19 with Algorand Payments"
echo "================================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✓ Created .env from .env.example"
        echo ""
        echo "⚠️  Using default passwords. You should change these in .env for production!"
        echo ""
    else
        echo "❌ Error: .env.example not found"
        exit 1
    fi
else
    echo "✓ .env file exists"
fi

# Create docker-compose.yml if it doesn't exist
if [ ! -f docker-compose.yml ]; then
    echo "📝 Creating docker-compose.yml..."
    if [ -f docker-compose.yml.example ]; then
        cp docker-compose.yml.example docker-compose.yml
        echo "✓ Created docker-compose.yml from example"
    else
        echo "❌ Error: docker-compose.yml.example not found"
        exit 1
    fi
else
    echo "✓ docker-compose.yml exists"
fi

# Create etc/odoo.conf if it doesn't exist
if [ ! -f etc/odoo.conf ]; then
    echo "📝 Creating etc/odoo.conf..."
    if [ -f etc/odoo.conf.example ]; then
        cp etc/odoo.conf.example etc/odoo.conf
        echo "✓ Created etc/odoo.conf from example"
    else
        echo "❌ Error: etc/odoo.conf.example not found"
        exit 1
    fi
else
    echo "✓ etc/odoo.conf exists"
fi

echo ""
echo "🐳 Starting Docker containers..."
echo ""

# Start Docker Compose
docker-compose up -d

echo ""
echo "✅ AlgoBizSuite is starting!"
echo ""
echo "📊 Container status:"
docker-compose ps
echo ""
echo "🌐 Access Odoo at: http://localhost:8069"
echo ""
echo "📝 Default credentials:"
echo "   Database: mydb (or create a new one)"
echo "   Admin password: admin (change in .env)"
echo ""
echo "📖 Next steps:"
echo "   1. Wait ~60 seconds for services to initialize"
echo "   2. Open http://localhost:8069 in your browser"
echo "   3. Database 'mydb' will be created automatically"
echo "   4. Algorand Pera Payment module will be auto-installed"
echo ""
echo "💡 Useful commands:"
echo "   View logs:     docker-compose logs -f odoo19"
echo "   Stop services: docker-compose down"
echo "   Restart:       docker-compose restart"
echo ""
echo "📚 Documentation: see README.md"
echo ""
echo "⏳ Installing Algorand Pera Payment module..."
echo "   (This will take about 60 seconds)"
echo ""

# Wait for Odoo to be ready
sleep 45

# Install the algorand_pera_payment module
docker-compose exec -T odoo19 odoo -c /etc/odoo/odoo.conf -d mydb -i algorand_pera_payment --stop-after-init > /dev/null 2>&1 || true

# Restart Odoo to ensure everything is loaded
echo "🔄 Restarting Odoo to complete setup..."
docker-compose restart odoo19 > /dev/null 2>&1

sleep 10

echo ""
echo "✅ Setup complete!"
echo "🌐 Odoo is ready at: http://localhost:8069"
echo ""
echo "📝 Default login:"
echo "   Email: admin"
echo "   Password: admin"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Algorand Pera Payment module is installed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚙️  REQUIRED CONFIGURATION:"
echo ""
echo "1. Configure your Merchant Algorand Address:"
echo "   • Navigate to: Website → Configuration → Payment Providers"
echo "   • Select: 'Algorand Pera Wallet'"
echo "   • Enter your 58-character Algorand wallet address"
echo ""
echo "2. Choose your network:"
echo "   • TestNet (for testing) - Get free ALGO at: https://bank.testnet.algorand.network/"
echo "   • MainNet (for production)"
echo ""
echo "3. For USD payments via USDC:"
echo "   • Your merchant wallet MUST be opted-in to USDC"
echo "   • Click 'Check USDC Opt-in Status' in the provider settings"
echo "   • ALGO payments work without USDC opt-in"
echo ""
echo "📖 Full configuration guide:"
echo "   addons/algorand_pera_payment/readme/CONFIGURE.md"
echo ""
echo "💡 Quick links:"
echo "   • Installation: addons/algorand_pera_payment/readme/INSTALL.md"
echo "   • Usage Guide:  addons/algorand_pera_payment/readme/USAGE.md"
echo ""

