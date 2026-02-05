#!/bin/bash

# Deployment script for GC Resume Filter on Apache Server
# This script builds the frontend and sets up the Apache configuration
# Designed to work alongside other sites in /var/www/html

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_PATH="/var/www/html/erp/resumefilter"

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
    echo -e "${YELLOW}Warning: Not running as root. Some steps will require sudo.${NC}"
    SUDO_CMD="sudo"
else
    SUDO_CMD=""
fi

# Confirm deployment location
echo -e "${YELLOW}This script will deploy to: ${NC}$DEPLOY_PATH"
echo -e "${YELLOW}Backend will run from: ${NC}$SCRIPT_DIR/backend"
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi
echo ""

# Step 1: Install backend dependencies
echo -e "${GREEN}[1/7] Installing backend dependencies...${NC}"
cd "$SCRIPT_DIR/backend"

# Always recreate the virtual environment to avoid portability issues
# (venvs contain hardcoded paths and are not portable between machines)
if [ -d "venv" ]; then
    echo "Removing existing virtual environment (venvs are not portable)..."
    rm -rf venv
fi
echo "Creating Python virtual environment..."
python3 -m venv venv

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
echo ""

# Step 2: Install frontend dependencies
echo -e "${GREEN}[2/7] Installing frontend dependencies...${NC}"
cd "$SCRIPT_DIR/frontend"
npm install
echo ""

# Step 3: Build frontend for production with base path
echo -e "${GREEN}[3/7] Building frontend for production...${NC}"
echo "Building with base path: /resumefilter/"
npm run build
echo ""

# Step 4: Deploy frontend to /var/www/html/resumefilter
echo -e "${GREEN}[4/7] Deploying frontend to $DEPLOY_PATH...${NC}"

# Create deployment directory
$SUDO_CMD mkdir -p "$DEPLOY_PATH"

# Backup existing deployment if it exists
if [ -d "$DEPLOY_PATH/frontend" ]; then
    echo -e "${YELLOW}Existing deployment found. Backing up...${NC}"
    $SUDO_CMD mv "$DEPLOY_PATH/frontend" "$DEPLOY_PATH/frontend.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Copy built frontend
$SUDO_CMD cp -r "$SCRIPT_DIR/frontend/dist" "$DEPLOY_PATH/frontend"

# Set proper permissions
$SUDO_CMD chown -R www-data:www-data "$DEPLOY_PATH/frontend"
$SUDO_CMD chmod -R 755 "$DEPLOY_PATH/frontend"
echo ""

# Step 5: Create necessary backend directories
echo -e "${GREEN}[5/7] Creating necessary backend directories...${NC}"
cd "$SCRIPT_DIR"
mkdir -p output resumes backend/data
echo ""

# Step 6: Setup Apache configuration
echo -e "${GREEN}[6/7] Setting up Apache configuration...${NC}"

APACHE_CONFIG="$SCRIPT_DIR/apache-config.conf"
APACHE_INCLUDES_DIR="/etc/apache2/conf-available"
APACHE_CONFIG_DEPLOYED="$APACHE_INCLUDES_DIR/gc-resumefilter.conf"

# Replace placeholder paths with actual deployment path
sed "s|__PROJECT_ROOT__|$DEPLOY_PATH|g" "$APACHE_CONFIG" > "$SCRIPT_DIR/apache-config-deployed.conf"

# Backup existing configuration if it exists
if [ -f "$APACHE_CONFIG_DEPLOYED" ]; then
    echo -e "${YELLOW}Apache configuration already exists. Backing up...${NC}"
    $SUDO_CMD cp "$APACHE_CONFIG_DEPLOYED" "$APACHE_CONFIG_DEPLOYED.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Copy Apache configuration to conf-available (safer than sites-available for path-based configs)
$SUDO_CMD cp "$SCRIPT_DIR/apache-config-deployed.conf" "$APACHE_CONFIG_DEPLOYED"

# Enable required Apache modules
echo "Enabling required Apache modules..."
$SUDO_CMD a2enmod proxy 2>/dev/null || true
$SUDO_CMD a2enmod proxy_http 2>/dev/null || true
$SUDO_CMD a2enmod rewrite 2>/dev/null || true
$SUDO_CMD a2enmod headers 2>/dev/null || true
$SUDO_CMD a2enmod alias 2>/dev/null || true

# Enable the configuration
echo "Enabling configuration..."
$SUDO_CMD a2enconf gc-resumefilter.conf

# Test Apache configuration before applying
echo "Testing Apache configuration..."
if $SUDO_CMD apache2ctl configtest 2>&1 | grep -q "Syntax OK"; then
    echo -e "${GREEN}Apache configuration syntax OK${NC}"
    
    # Reload Apache
    echo "Reloading Apache..."
    $SUDO_CMD systemctl reload apache2
    echo -e "${GREEN}Apache reloaded successfully${NC}"
else
    echo -e "${RED}Apache configuration test FAILED!${NC}"
    echo "Rolling back configuration..."
    $SUDO_CMD a2disconf gc-resumefilter.conf 2>/dev/null || true
    if [ -f "$APACHE_CONFIG_DEPLOYED.backup."* ]; then
        LATEST_BACKUP=$(ls -t "$APACHE_CONFIG_DEPLOYED.backup."* 2>/dev/null | head -1)
        if [ -n "$LATEST_BACKUP" ]; then
            $SUDO_CMD cp "$LATEST_BACKUP" "$APACHE_CONFIG_DEPLOYED"
        fi
    fi
    echo -e "${RED}Deployment failed. Apache configuration has been rolled back.${NC}"
    exit 1
fi

echo ""

# Step 7: Setup backend service
echo -e "${GREEN}[7/7] Setting up backend service...${NC}"

SERVICE_FILE="/etc/systemd/system/gc-resumefilter-backend.service"

# Create systemd service file
cat > "$SCRIPT_DIR/gc-resumefilter-backend.service" << EOF
[Unit]
Description=GC Resume Filter Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR/backend
Environment="PATH=$SCRIPT_DIR/backend/venv/bin"
EnvironmentFile=$SCRIPT_DIR/.env
ExecStart=$SCRIPT_DIR/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Installing systemd service..."
$SUDO_CMD cp "$SCRIPT_DIR/gc-resumefilter-backend.service" "$SERVICE_FILE"
$SUDO_CMD systemctl daemon-reload
$SUDO_CMD systemctl enable gc-resumefilter-backend.service
$SUDO_CMD systemctl restart gc-resumefilter-backend.service

# Wait a moment and check if service started successfully
sleep 2
if $SUDO_CMD systemctl is-active --quiet gc-resumefilter-backend.service; then
    echo -e "${GREEN}Backend service started successfully${NC}"
else
    echo -e "${RED}Warning: Backend service may have failed to start${NC}"
    echo "Check status with: sudo systemctl status gc-resumefilter-backend"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Deployment Complete!"
echo "==========================================${NC}"
echo ""
echo "Access the application at:"
echo -e "  ${GREEN}http://YOUR_SERVER_IP/erp/resumefilter/${NC}"
echo ""
echo "Services:"
echo "  - Frontend: $DEPLOY_PATH/frontend"
echo "  - Backend API: http://YOUR_SERVER_IP/erp/resumefilter/api (proxied to port 8000)"
echo ""
echo "Useful commands:"
echo "  - Check backend status: sudo systemctl status gc-resumefilter-backend"
echo "  - View backend logs: sudo journalctl -u gc-resumefilter-backend -f"
echo "  - Restart backend: sudo systemctl restart gc-resumefilter-backend"
echo "  - Restart Apache: sudo systemctl restart apache2"
echo "  - Test Apache config: sudo apache2ctl configtest"
echo ""
echo "The deployment does NOT affect other sites in /var/www/html"
echo ""
