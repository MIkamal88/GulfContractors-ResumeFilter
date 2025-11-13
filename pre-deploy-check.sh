#!/bin/bash

# Pre-deployment check script for GC Resume Filter
# Run this on the Ubuntu server before deploying

echo "=========================================="
echo "GC Resume Filter - Pre-Deployment Check"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

# Check 1: Apache installed and running
echo -n "Checking Apache installation... "
if command -v apache2 &> /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "  Apache2 is not installed"
    ERRORS=$((ERRORS + 1))
fi

echo -n "Checking Apache service status... "
if systemctl is-active --quiet apache2; then
    echo -e "${GREEN}Running${NC}"
else
    echo -e "${YELLOW}Not Running${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 2: Directory permissions
echo -n "Checking /var/www/html exists... "
if [ -d "/var/www/html" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    ERRORS=$((ERRORS + 1))
fi

echo -n "Checking write permissions to /var/www/html... "
if [ -w "/var/www/html" ] || sudo -n test -w "/var/www/html" 2>/dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}Requires sudo${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 3: Required Apache modules
echo ""
echo "Checking required Apache modules:"
REQUIRED_MODS=("proxy" "proxy_http" "rewrite" "headers" "alias")

for mod in "${REQUIRED_MODS[@]}"; do
    echo -n "  - $mod: "
    if apache2ctl -M 2>/dev/null | grep -q "${mod}_module"; then
        echo -e "${GREEN}Enabled${NC}"
    else
        echo -e "${YELLOW}Not Enabled (will be enabled by deploy script)${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
done

# Check 4: Port 8000 availability
echo ""
echo -n "Checking if port 8000 is available... "
if ! ss -tuln 2>/dev/null | grep -q ":8000 "; then
    echo -e "${GREEN}Available${NC}"
else
    echo -e "${RED}In Use${NC}"
    echo "  Port 8000 is already in use by another service"
    ss -tulnp 2>/dev/null | grep ":8000 " || true
    ERRORS=$((ERRORS + 1))
fi

# Check 5: Python3 and pip
echo ""
echo -n "Checking Python3... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}OK${NC} (${PYTHON_VERSION})"
else
    echo -e "${RED}FAILED${NC}"
    ERRORS=$((ERRORS + 1))
fi

echo -n "Checking Python3 venv module... "
if python3 -m venv --help &> /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "  Install with: sudo apt-get install python3-venv"
    ERRORS=$((ERRORS + 1))
fi

echo -n "Checking pip3... "
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}Not Found${NC}"
    echo "  Install with: sudo apt-get install python3-pip"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 6: Node.js and npm
echo ""
echo -n "Checking Node.js... "
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}OK${NC} (${NODE_VERSION})"
else
    echo -e "${RED}FAILED${NC}"
    echo "  Install with: sudo apt-get install nodejs npm"
    ERRORS=$((ERRORS + 1))
fi

echo -n "Checking npm... "
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}OK${NC} (${NPM_VERSION})"
else
    echo -e "${RED}FAILED${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 7: Existing paths check
echo ""
echo "Checking for path conflicts:"
echo -n "  /resumefilter/ in Apache config... "
if grep -r "resumefilter" /etc/apache2/ 2>/dev/null | grep -v ".backup" | grep -q .; then
    echo -e "${YELLOW}Already exists${NC}"
    echo "  Previous deployment detected. Will be backed up during deployment."
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}Not found (clean)${NC}"
fi

echo -n "  /var/www/html/resumefilter/... "
if [ -d "/var/www/html/resumefilter" ]; then
    echo -e "${YELLOW}Exists${NC}"
    echo "  Previous deployment detected. Will be backed up during deployment."
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}Not found (clean)${NC}"
fi

# Check 8: Systemd service check
echo ""
echo -n "Checking for existing backend service... "
if systemctl list-unit-files | grep -q "gc-resumefilter-backend.service"; then
    echo -e "${YELLOW}Exists${NC}"
    echo "  Previous service detected. Will be restarted during deployment."
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}Not found (clean)${NC}"
fi

# Summary
echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo -e "Errors: ${RED}${ERRORS}${NC}"
echo -e "Warnings: ${YELLOW}${WARNINGS}${NC}"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ Server is ready for deployment${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Transfer the project to the server"
    echo "  2. Run: sudo bash deploy.sh"
    echo "  3. Access at: http://192.168.1.62/resumefilter/"
    exit 0
else
    echo -e "${RED}✗ Server has critical issues that must be fixed${NC}"
    echo ""
    echo "Please fix the errors above before deploying."
    exit 1
fi
