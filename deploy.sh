#!/bin/bash

# Deployment script for GC Resume Filter on Apache Server
# This script builds the frontend and sets up the Apache configuration

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "=========================================="
echo "GC Resume Filter - Apache Deployment"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root for Apache configuration
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}Warning: Not running as root. Apache configuration steps will require sudo.${NC}"
    SUDO_CMD="sudo"
else
    SUDO_CMD=""
fi

# Step 1: Install backend dependencies
echo -e "${GREEN}[1/6] Installing backend dependencies...${NC}"
cd "$PROJECT_ROOT/backend"
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
deactivate
echo ""

# Step 2: Install frontend dependencies
echo -e "${GREEN}[2/6] Installing frontend dependencies...${NC}"
cd "$PROJECT_ROOT/frontend"
npm install
echo ""

# Step 3: Build frontend for production
echo -e "${GREEN}[3/6] Building frontend for production...${NC}"
npm run build
echo ""

# Step 4: Create necessary directories
echo -e "${GREEN}[4/6] Creating necessary directories...${NC}"
cd "$PROJECT_ROOT"
mkdir -p output resumes backend/data
echo ""

# Step 5: Setup Apache configuration
echo -e "${GREEN}[5/6] Setting up Apache configuration...${NC}"

# Update Apache config file with actual paths
APACHE_CONFIG="$PROJECT_ROOT/apache-config.conf"
APACHE_CONFIG_DEPLOYED="/etc/apache2/sites-available/gc-resumefilter.conf"

# Replace placeholder paths with actual paths
sed "s|/mnt/D/Work/GulfContractors/GC_resumefilter|$PROJECT_ROOT|g" "$APACHE_CONFIG" > "$PROJECT_ROOT/apache-config-deployed.conf"

# Copy Apache configuration
if [ -f "$APACHE_CONFIG_DEPLOYED" ]; then
    echo -e "${YELLOW}Apache configuration already exists. Backing up...${NC}"
    $SUDO_CMD cp "$APACHE_CONFIG_DEPLOYED" "$APACHE_CONFIG_DEPLOYED.backup.$(date +%Y%m%d_%H%M%S)"
fi

$SUDO_CMD cp "$PROJECT_ROOT/apache-config-deployed.conf" "$APACHE_CONFIG_DEPLOYED"

# Enable required Apache modules
echo "Enabling required Apache modules..."
$SUDO_CMD a2enmod proxy 2>/dev/null || true
$SUDO_CMD a2enmod proxy_http 2>/dev/null || true
$SUDO_CMD a2enmod rewrite 2>/dev/null || true
$SUDO_CMD a2enmod headers 2>/dev/null || true

# Enable the site
echo "Enabling site configuration..."
$SUDO_CMD a2ensite gc-resumefilter.conf

# Disable default site if it's enabled (optional)
read -p "Disable default Apache site? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    $SUDO_CMD a2dissite 000-default.conf 2>/dev/null || true
fi

# Test Apache configuration
echo "Testing Apache configuration..."
$SUDO_CMD apache2ctl configtest

# Reload Apache
echo "Reloading Apache..."
$SUDO_CMD systemctl reload apache2

echo ""

# Step 6: Setup backend service
echo -e "${GREEN}[6/6] Setting up backend service...${NC}"

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/gc-resumefilter-backend.service"

cat > "$PROJECT_ROOT/gc-resumefilter-backend.service" << EOF
[Unit]
Description=GC Resume Filter Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_ROOT/backend
Environment="PATH=$PROJECT_ROOT/backend/venv/bin"
EnvironmentFile=$PROJECT_ROOT/.env
ExecStart=$PROJECT_ROOT/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Installing systemd service..."
$SUDO_CMD cp "$PROJECT_ROOT/gc-resumefilter-backend.service" "$SERVICE_FILE"
$SUDO_CMD systemctl daemon-reload
$SUDO_CMD systemctl enable gc-resumefilter-backend.service
$SUDO_CMD systemctl restart gc-resumefilter-backend.service

echo ""
echo -e "${GREEN}=========================================="
echo "Deployment Complete!"
echo "==========================================${NC}"
echo ""
echo "Services status:"
echo "  - Frontend: http://localhost (served by Apache)"
echo "  - Backend API: http://localhost/api (proxied to port 8000)"
echo ""
echo "Useful commands:"
echo "  - Check backend status: sudo systemctl status gc-resumefilter-backend"
echo "  - View backend logs: sudo journalctl -u gc-resumefilter-backend -f"
echo "  - Restart backend: sudo systemctl restart gc-resumefilter-backend"
echo "  - Restart Apache: sudo systemctl restart apache2"
echo "  - View Apache logs: sudo tail -f /var/log/apache2/gc_resumefilter_error.log"
echo ""
