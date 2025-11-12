# Apache Deployment Setup Guide

This guide provides detailed step-by-step instructions for deploying the GC Resume Filter application on an Apache web server.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Apache Configuration](#apache-configuration)
6. [Systemd Service Setup](#systemd-service-setup)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- Ubuntu/Debian-based Linux or Windows with WSL
- Apache2 web server
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn
- Git

### Install Required Software

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install Apache2
sudo apt install apache2 -y

# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Verify installations
apache2 -v
python3 --version
node --version
npm --version
```

#### Windows (with WSL)

1. Install WSL2 and Ubuntu
2. Follow the Ubuntu/Debian instructions above
3. For Apache on Windows (XAMPP alternative):
   - Download Apache from https://www.apachelounge.com/download/
   - Extract to C:\Apache24
   - Install as Windows service: `httpd.exe -k install`

## Initial Setup

### 1. Clone the Repository

```bash
cd /path/to/your/projects
git clone <repository-url> GC_resumefilter
cd GC_resumefilter
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your favorite editor
nano .env
```

Update the following variables:

```env
# OpenAI Configuration (if using AI summaries)
OPENAI_API_KEY=your_actual_api_key_here
USE_OPENAI=True

# Resume Filter Settings
MIN_KEYWORD_SCORE=50

# File Paths - Update these to match your actual paths
CSV_OUTPUT_PATH=/absolute/path/to/GC_resumefilter/output/filtered_resumes.csv
RESUME_FOLDER_PATH=/absolute/path/to/GC_resumefilter/resumes
```

**Important**: Replace `/absolute/path/to/` with your actual project path.

### 3. Create Required Directories

```bash
mkdir -p output resumes backend/data
chmod 755 output resumes backend/data
```

## Backend Setup

### 1. Create Python Virtual Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt
```

### 2. Install Python Dependencies

```bash
# Ensure you're in the backend directory with venv activated
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Test Backend Locally

```bash
# Still in backend directory with venv activated
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open another terminal and test:

```bash
curl http://localhost:8000
# Should return: {"status":"healthy","message":"Resume Filter API is running"}
```

Press `Ctrl+C` to stop the test server.

```bash
# Deactivate virtual environment
deactivate
```

## Frontend Setup

### 1. Install Node Dependencies

```bash
cd ../frontend

# Install dependencies
npm install
```

### 2. Build for Production

```bash
# Build the production bundle
npm run build

# Verify the build
ls -la dist/
```

You should see files like `index.html`, `assets/`, etc. in the `dist/` directory.

### 3. Test Frontend Locally (Optional)

```bash
# Preview the production build
npm run preview
```

## Apache Configuration

### 1. Update Apache Config File

Edit the `apache-config.conf` file in the project root to use your actual paths:

```bash
cd ..  # Back to project root

# Edit apache-config.conf
nano apache-config.conf
```

Replace all instances of `/mnt/D/Work/GulfContractors/GC_resumefilter` with your actual project path.

For example, if your project is at `/home/user/projects/GC_resumefilter`, update:

```apache
DocumentRoot "/home/user/projects/GC_resumefilter/frontend/dist"

<Directory "/home/user/projects/GC_resumefilter/frontend/dist">
    # ... rest of config
</Directory>
```

### 2. Enable Required Apache Modules

```bash
# Enable proxy modules
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod rewrite
sudo a2enmod headers

# Verify modules are enabled
sudo apache2ctl -M | grep -E 'proxy|rewrite|headers'
```

### 3. Copy Apache Configuration

```bash
# Copy your config to Apache sites-available
sudo cp apache-config.conf /etc/apache2/sites-available/gc-resumefilter.conf

# Enable the site
sudo a2ensite gc-resumefilter.conf

# Disable default site (optional, recommended)
sudo a2dissite 000-default.conf
```

### 4. Test Apache Configuration

```bash
# Test for syntax errors
sudo apache2ctl configtest

# Should output: Syntax OK
```

If there are errors, review the configuration file and fix them.

### 5. Restart Apache

```bash
sudo systemctl restart apache2

# Check status
sudo systemctl status apache2
```

## Systemd Service Setup

### 1. Create Service File

Create a systemd service file for the backend:

```bash
sudo nano /etc/systemd/system/gc-resumefilter-backend.service
```

Add the following content (replace paths with your actual paths):

```ini
[Unit]
Description=GC Resume Filter Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/absolute/path/to/GC_resumefilter/backend
Environment="PATH=/absolute/path/to/GC_resumefilter/backend/venv/bin"
EnvironmentFile=/absolute/path/to/GC_resumefilter/.env
ExecStart=/absolute/path/to/GC_resumefilter/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Important**: Replace:
- `YOUR_USERNAME` with your actual username
- `/absolute/path/to/GC_resumefilter` with your actual project path

### 2. Enable and Start Service

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable gc-resumefilter-backend.service

# Start the service
sudo systemctl start gc-resumefilter-backend.service

# Check status
sudo systemctl status gc-resumefilter-backend.service
```

### 3. Verify Backend is Running

```bash
curl http://localhost:8000
# Should return: {"status":"healthy","message":"Resume Filter API is running"}
```

## Verification

### 1. Check All Services

```bash
# Check Apache
sudo systemctl status apache2

# Check Backend
sudo systemctl status gc-resumefilter-backend

# Check if ports are listening
sudo netstat -tlnp | grep -E ':80|:8000'
```

### 2. Test Frontend

Open your browser and navigate to:
- http://localhost

You should see the React application.

### 3. Test Backend API

Navigate to:
- http://localhost/api/docs

You should see the FastAPI Swagger documentation.

### 4. Test End-to-End

1. Use the frontend to upload a resume
2. Enter some keywords
3. Click to analyze
4. Verify results are displayed
5. Download the CSV report

## Troubleshooting

### Backend Not Starting

```bash
# View detailed logs
sudo journalctl -u gc-resumefilter-backend -n 50 --no-pager

# Common issues:
# 1. Port 8000 already in use
sudo netstat -tlnp | grep 8000
# Kill the process or change port

# 2. Permission issues
chmod 755 backend/
chmod 644 .env

# 3. Missing dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Apache Not Serving Frontend

```bash
# Check Apache error logs
sudo tail -f /var/log/apache2/error.log

# Verify frontend build exists
ls -la frontend/dist/

# Rebuild frontend
cd frontend
npm run build

# Check file permissions
chmod -R 755 frontend/dist/
```

### API Proxy Not Working

```bash
# Verify proxy modules are enabled
sudo apache2ctl -M | grep proxy

# Check Apache config
sudo apache2ctl -t

# View Apache error logs
sudo tail -f /var/log/apache2/gc_resumefilter_error.log

# Restart both services
sudo systemctl restart gc-resumefilter-backend
sudo systemctl restart apache2
```

### Permission Denied Errors

```bash
# Fix ownership (replace YOUR_USERNAME)
sudo chown -R YOUR_USERNAME:YOUR_USERNAME /path/to/GC_resumefilter

# Fix directory permissions
chmod 755 resumes/ output/ backend/data/
chmod 644 .env

# If Apache needs access to files
sudo usermod -a -G YOUR_USERNAME www-data
```

### CORS Errors

The backend is configured to allow all origins. If you still see CORS errors:

1. Check that requests are going through the `/api` proxy
2. Verify Apache proxy configuration
3. Check browser console for actual error

### CSV Export Not Working

```bash
# Check output directory exists and is writable
ls -la output/
chmod 755 output/

# Check backend logs
sudo journalctl -u gc-resumefilter-backend -f

# Test manually
curl -X POST http://localhost:8000/filter-resumes \
  -F "files=@test.pdf" \
  -F 'keywords=["Python"]'
```

## Useful Commands

### View Logs

```bash
# Backend logs (real-time)
sudo journalctl -u gc-resumefilter-backend -f

# Backend logs (last 100 lines)
sudo journalctl -u gc-resumefilter-backend -n 100

# Apache error logs
sudo tail -f /var/log/apache2/gc_resumefilter_error.log

# Apache access logs
sudo tail -f /var/log/apache2/gc_resumefilter_access.log
```

### Service Management

```bash
# Restart services
sudo systemctl restart gc-resumefilter-backend
sudo systemctl restart apache2

# Stop services
sudo systemctl stop gc-resumefilter-backend
sudo systemctl stop apache2

# Start services
sudo systemctl start gc-resumefilter-backend
sudo systemctl start apache2

# Check status
sudo systemctl status gc-resumefilter-backend
sudo systemctl status apache2
```

### Update Application

```bash
# Pull latest code
git pull

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart gc-resumefilter-backend

# Update frontend
cd ../frontend
npm install
npm run build
sudo systemctl reload apache2
```

## Next Steps

After successful deployment:

1. Configure firewall if needed
2. Set up SSL/TLS certificates for HTTPS
3. Configure regular backups
4. Set up monitoring and alerting
5. Review and harden security settings

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review Apache logs
- Check systemd service logs
- Verify all paths and permissions
